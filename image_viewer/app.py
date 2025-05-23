import os
from pathlib import Path
from typing import Dict, List, Union

from flask import Flask, abort, render_template, request, send_from_directory


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
        instance.config['IMAGE_DIR'] = str(Path(image_dir).absolute())
    else:
        instance.config['IMAGE_DIR'] = None
    
    @instance.route('/')
    def index():
        """Render the index page with directory structure.
        
        Returns:
            str: Rendered HTML template with directory contents.
        """
        base_dir = instance.config.get('IMAGE_DIR')
        if not base_dir or not os.path.exists(base_dir):
            return "Image directory not configured or not found.", 400
            
        directories = get_directories(base_dir)
        images = get_formatted_images(base_dir)
        
        # ページネーション
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        total = len(images)
        start = (page - 1) * per_page
        end = start + per_page
        paged_images = images[start:end]
        total_pages = (total + per_page - 1) // per_page
        
        col_count = int(request.args.get('col_count', 3))
        return render_template('index.html', 
                              directories=directories,
                              images=paged_images,
                              current_path="",
                              parent_path=None,
                              page=page,
                              total_pages=total_pages,
                              per_page=per_page,
                              col_count=col_count)
    
    @instance.route('/browse/', defaults={'path': ''})
    @instance.route('/browse/<path:path>')
    def browse(path):
        """Browse directory structure and show images.
        
        Args:
            path (str): Relative path within the image directory.
        
        Returns:
            str: Rendered HTML template with directory contents.
        """
        base_dir = instance.config.get('IMAGE_DIR')
        if not base_dir:
            return "Image directory not configured.", 400
            
        # パスを安全に結合
        target_dir = os.path.normpath(os.path.join(base_dir, path))
        
        # セキュリティチェック - ディレクトリトラバーサルを防止
        if not os.path.commonpath([os.path.abspath(target_dir), base_dir]) == base_dir:
            abort(403)
            
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            abort(404)
            
        # 親パスを計算
        parent_path = str(Path(path).parent) if path else None
        if parent_path == '.':
            parent_path = ''
        
        directories = get_directories(target_dir, base_path=path)
        images = get_formatted_images(target_dir, base_path=path)
        
        # ページネーション
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        total = len(images)
        start = (page - 1) * per_page
        end = start + per_page
        paged_images = images[start:end]
        total_pages = (total + per_page - 1) // per_page
        
        col_count = int(request.args.get('col_count', 3))
        return render_template('index.html',
                              directories=directories,
                              images=paged_images,
                              current_path=path,
                              parent_path=parent_path,
                              page=page,
                              total_pages=total_pages,
                              per_page=per_page,
                              col_count=col_count)
    
    @instance.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve an image from the configured image directory.
        
        Args:
            filename (str): Path to image file relative to image directory.
            
        Returns:
            Response: Flask response containing the requested image.
        """
        base_dir = instance.config.get('IMAGE_DIR')
        if not base_dir:
            abort(400)
        
        # パスを安全に解決
        file_path = os.path.normpath(os.path.join(base_dir, filename))
        
        # セキュリティチェック - ディレクトリトラバーサルを防止
        if not os.path.commonpath([os.path.abspath(file_path), base_dir]) == base_dir:
            abort(403)
        
        # ディレクトリとファイル名を分ける
        directory = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        
        return send_from_directory(directory, basename)
    
    # CORS設定を強化
    @instance.after_request
    def add_header(response):
        """Add headers to allow cross-origin requests.
        
        Args:
            response: Flask response object.
            
        Returns:
            Response: Modified response with CORS headers.
        """
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        # キャッシュ問題を回避
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    return instance


def get_directories(directory: Union[str, Path], base_path: str = '') -> List[Dict[str, str]]:
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
                url_path = f"/browse/{base_path}/{item.name}".replace('//', '/').rstrip('/')
                if not url_path.startswith('/browse'):
                    url_path = f"/browse{url_path}"
                result.append({
                    'name': item.name,
                    'path': url_path
                })
                
        return sorted(result, key=lambda x: x['name'])
    except Exception as e:
        print(f"ディレクトリ取得エラー: {e}")
        return []


def get_formatted_images(directory: Union[str, Path], base_path: str = '') -> List[Dict[str, str]]:
    """Get images from directory with proper URL paths.
    
    Args:
        directory: Directory to scan for image files.
        base_path: Base path for URL construction. Defaults to ''.
        
    Returns:
        List of image information dictionaries with absolute URLs.
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
            
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        result = []
        
        for item in dir_path.iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                # 安全にURLパスを構築
                image_path = f"{base_path}/{item.name}".lstrip('/').replace('\\', '/')
                url_path = f"/images/{image_path}"
                
                result.append({
                    'name': item.name,
                    'path': url_path
                })
                
        return sorted(result, key=lambda x: x['name'])
    except Exception as e:
        print(f"画像リスト取得エラー: {e}")
        return []


if __name__ == '__main__':
    app = create_app(image_dir='path/to/images')
    app.run(debug=True, host='0.0.0.0', port=5000)