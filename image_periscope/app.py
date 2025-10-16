"""This module implements the Flask web application for the Image Viewer."""
import socket
from importlib import metadata
from pathlib import Path
from typing import TypedDict

import bleach
from flask import Flask, abort, render_template, request, send_from_directory


class DirectoryTree(TypedDict):
    """Directory tree structure."""

    name: str
    path: str
    children: list["DirectoryTree"]


def create_app(image_dir=None):
    """Create and configure the Flask application.

    Args:
        image_dir (str, optional): Directory containing images to display.
            Defaults to None.

    Returns:
        Flask: Configured Flask application instance.
    """
    instance = Flask(__name__)

    # 絶対パスに変換して保存
    if image_dir:
        instance.config["IMAGE_DIR"] = str(Path(image_dir).absolute())
    else:
        instance.config["IMAGE_DIR"] = None

    try:
        instance.config["APP_VERSION"] = metadata.version("image-periscope")
    except metadata.PackageNotFoundError:
        instance.config["APP_VERSION"] = "dev"

    commit_hash_file = Path(__file__).parent / "COMMIT_HASH"
    if commit_hash_file.exists():
        instance.config["COMMIT_HASH"] = commit_hash_file.read_text().strip()
    else:
        instance.config["COMMIT_HASH"] = "N/A"


    @instance.route("/")
    def index():
        """Render the index page with directory structure.

        Returns:
            str: Rendered HTML template with directory contents.
        """
        base_dir_path = Path(instance.config.get("IMAGE_DIR")).resolve()
        if not base_dir_path or not base_dir_path.exists():
            return "Image directory not configured or not found.", 400

        search_query = request.args.get("q", None)
        directories = get_directories(base_dir_path)
        items = get_formatted_items(base_dir_path, search_query=search_query, base_dir=base_dir_path)

        # パンくずリスト用
        path_parts: list[str] = []

        # ページネーション
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 100))
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        paged_items = items[start:end]
        total_pages = (total + per_page - 1) // per_page

        col_count = int(request.args.get("col_count", 3))
        directory_tree = get_directory_tree(base_dir_path)

        # サーバー情報を取得
        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        image_directory = instance.config.get("IMAGE_DIR")

        return render_template("index.html",
                              directories=directories,
                              items=paged_items,
                              current_path="",
                              parent_path=None,
                              page=page,
                              total_pages=total_pages,
                              per_page=per_page,
                              col_count=col_count,
                              directory_tree=directory_tree,
                              path_parts=path_parts,
                              search_query=search_query,
                              host_name=host_name,
                              ip_address=ip_address,
                              image_directory=image_directory,
                              app_version=instance.config.get("APP_VERSION"),
                              commit_hash=instance.config.get("COMMIT_HASH"))

    @instance.route("/browse/", defaults={"path": ""})
    @instance.route("/browse/<path:path>")
    def browse(path):
        """Browse directory structure and show images.

        Args:
            path (str): Relative path within the image directory.

        Returns:
            str: Rendered HTML template with directory contents.
        """
        base_dir_path = Path(instance.config.get("IMAGE_DIR")).resolve()
        if not base_dir_path:
            return "Image directory not configured.", 400

        # パスを安全に結合
        target_dir_path = (base_dir_path / path).resolve()

        # セキュリティチェック - ディレクトリトラバーサルを防止
        if base_dir_path not in target_dir_path.parents and target_dir_path != base_dir_path:
            abort(403)

        if not target_dir_path.exists() or not target_dir_path.is_dir():
            abort(404)

        # 親パスを計算
        parent_path = str(Path(path).parent) if path else None
        if parent_path == ".":
            parent_path = ""

        search_query = request.args.get("q", None)
        directories = get_directories(target_dir_path, base_path=path)
        items = get_formatted_items(target_dir_path, base_path=path, search_query=search_query, base_dir=base_dir_path)

        # パンくずリスト用
        path_parts = path.split("/") if path else []

        # ページネーション
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 100))
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        paged_items = items[start:end]
        total_pages = (total + per_page - 1) // per_page

        col_count = int(request.args.get("col_count", 3))
        directory_tree = get_directory_tree(base_dir_path)

        # サーバー情報を取得
        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        image_directory = instance.config.get("IMAGE_DIR")

        return render_template("index.html",
                              directories=directories,
                              items=paged_items,
                              current_path=path,
                              parent_path=parent_path,
                              page=page,
                              total_pages=total_pages,
                              per_page=per_page,
                              col_count=col_count,
                              directory_tree=directory_tree,
                              path_parts=path_parts,
                              search_query=search_query,
                              host_name=host_name,
                              ip_address=ip_address,
                              image_directory=image_directory,
                              app_version=instance.config.get("APP_VERSION"),
                              commit_hash=instance.config.get("COMMIT_HASH"))

    @instance.route("/images/<path:filename>")
    def serve_image(filename):
        """Serve an image from the configured image directory.

        Args:
            filename (str): Path to image file relative to image directory.

        Returns:
            Response: Flask response containing the requested image.
        """
        base_dir_path = Path(instance.config.get("IMAGE_DIR")).resolve()
        if not base_dir_path:
            abort(400)

        # パスを安全に解決
        file_path = (base_dir_path / filename).resolve()

        # セキュリティチェック - ディレクトリトラバーサルを防止
        if base_dir_path not in file_path.parents and file_path != base_dir_path:
            abort(403)

        # ディレクトリとファイル名を分ける
        directory = file_path.parent
        basename = file_path.name

        return send_from_directory(directory, basename)

    @instance.route("/view/<path:filename>")
    def view_html(filename):
        """Serve an HTML file from the configured image directory."""
        base_dir_path = Path(instance.config.get("IMAGE_DIR")).resolve()
        if not base_dir_path:
            abort(400)

        file_path = (base_dir_path / filename).resolve()

        if base_dir_path not in file_path.parents and file_path != base_dir_path:
            abort(403)

        if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() not in {".html", ".htm"}:
            abort(404)

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except UnicodeDecodeError:
                abort(500)  # Return error if file cannot be decoded

        allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ["h1", "h2", "h3", "p", "br", "hr", "pre"]
        safe_content = bleach.clean(content, tags=allowed_tags, strip=True)
        return render_template("view_html.html", title=file_path.name, content=safe_content)

    # CORS設定を強化
    @instance.after_request
    def add_header(response):
        """Add headers to allow cross-origin requests.

        Args:
            response: Flask response object.

        Returns:
            Response: Modified response with CORS headers.
        """
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        # キャッシュ問題を回避
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    return instance


def get_directories(directory: Path, base_path: str = "") -> list[dict[str, str]]:
    """Get subdirectories from the specified directory.

    Args:
        directory: Directory to scan for subdirectories.
        base_path: Base path for URL construction. Defaults to ''.

    Returns:
        List of directory information dictionaries.
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return []

        result = []

        for item in dir_path.iterdir():
            if item.is_dir():
                # 安全にURLパスを構築
                url_path = f"/browse/{base_path}/{item.name}".replace("//", "/").rstrip("/")
                if not url_path.startswith("/browse"):
                    url_path = f"/browse{url_path}"
                result.append({
                    "name": item.name,
                    "path": url_path
                })

        return sorted(result, key=lambda x: x["name"])
    except Exception as e:
        print(f"ディレクトリ取得エラー: {e}")
        return []


def get_formatted_items(directory: Path, base_path: str = "", search_query: str | None = None, base_dir: Path | None = None) -> list[dict[str, str]]:
    """Get items from directory with proper URL paths.

    Args:
        directory: Directory to scan for image files.
        base_path: Base path for URL construction. Defaults to ''.
        search_query: If provided, recursively search for files matching this query.
        base_dir: The base directory for the image library.

    Returns:
        List of item information dictionaries with absolute URLs.
    """
    if search_query:
        return get_items_recursive(directory, search_query, base_dir or directory)
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return []

        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
        html_extensions = {".html", ".htm"}
        result = []

        for item in dir_path.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                item_path = f"{base_path}/{item.name}".lstrip("/").replace("\\", "/")
                if ext in image_extensions:
                    url_path = f"/images/{item_path}"
                    result.append({"name": item.name, "path": url_path, "type": "image"})
                elif ext in html_extensions:
                    url_path = f"/view/{item_path}"
                    result.append({"name": item.name, "path": url_path, "type": "html"})

        return sorted(result, key=lambda x: x["name"])
    except Exception as e:
        print(f"アイテムリスト取得エラー: {e}")
        return []


def get_items_recursive(directory: Path, search_query: str, base_dir: Path) -> list[dict[str, str]]:
    """Recursively get items from directory matching the search query.

    Args:
        directory: Directory to scan for files.
        search_query: The query to match against file names.
        base_dir: The base directory for the image library, for correct path calculation.

    Returns:
        List of item information dictionaries with absolute URLs.
    """
    try:
        base_dir_path = Path(directory)
        if not base_dir_path.exists():
            return []

        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
        html_extensions = {".html", ".htm"}
        result = []

        for item in base_dir_path.rglob(f"*{search_query}*"):
            if item.is_file():
                ext = item.suffix.lower()
                # app.config["IMAGE_DIR"] を基準とした相対パスを計算
                try:
                    item_path = str(item.relative_to(base_dir)).replace("\\", "/")
                except ValueError:
                    # This can happen if the file is outside the base directory, though rglob shouldn't do that.
                    item_path = item.name

                if ext in image_extensions:
                    url_path = f"/images/{item_path}"
                    result.append({"name": item.name, "path": url_path, "type": "image"})
                elif ext in html_extensions:
                    url_path = f"/view/{item_path}"
                    result.append({"name": item.name, "path": url_path, "type": "html"})

        return sorted(result, key=lambda x: x["name"])
    except Exception as e:
        print(f"アイテムリスト取得エラー: {e}")
        return []


def get_directory_tree(directory: Path, base_path: str = "") -> DirectoryTree:
    """指定ディレクトリ以下のツリー構造を再帰的に辞書で返す。"""
    dir_path = Path(directory)
    tree: DirectoryTree = {
        "name": dir_path.name if base_path else "ルート",
        "path": f"/browse/{base_path}" if base_path else "/",
        "children": []
    }
    for item in sorted(dir_path.iterdir(), key=lambda x: x.name):
        if item.is_dir():
            child_base = f"{base_path}/{item.name}".lstrip("/")
            tree["children"].append(get_directory_tree(item, child_base))
    return tree


if __name__ == "__main__":
    app = create_app(image_dir="path/to/images")
    app.run(debug=True, host="127.0.0.1", port=5000)
