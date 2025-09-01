"""This module provides utility functions for handling images."""
from pathlib import Path


def get_image_list(directory: str | Path) -> list[dict[str, str]]:
    """画像ディレクトリ内の全画像ファイルのリストを取得する。

    ディレクトリ内の画像を再帰的に検索し、その階層関係を保持したリストを返します。

    Args:
        directory: 画像を検索するディレクトリのパス

    Returns:
        画像パスとその名前を含む辞書のリスト
    """
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
    images = []
    dir_path = Path(directory)

    for file_path in dir_path.glob("**/*"):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            # 相対パスを計算
            relative_path = file_path.relative_to(dir_path)
            images.append({"path": str(relative_path), "name": file_path.name})

    return images


def organize_images(images: list[dict[str, str]]) -> dict[str, str | dict]:
    """画像リストを階層構造に整理する。

    画像のパス情報から、ディレクトリ階層を表す入れ子の辞書構造を作成します。

    Args:
        images: 画像パス情報を含む辞書のリスト

    Returns:
        画像の階層構造を表す入れ子の辞書
    """
    organized: dict[str, str | dict] = {}
    for image in images:
        # パス部分を取得
        path_parts = Path(image["path"]).parts
        current_level: dict[str, str | dict] = organized

        # ファイル名を除く各パス部分を処理
        for part in path_parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]  # type: ignore

        # 最後の部分（ファイル名）を追加
        current_level[path_parts[-1]] = image["path"]

    return organized
