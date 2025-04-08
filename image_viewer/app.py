import os
from pathlib import Path

from flask import Flask, render_template, send_from_directory


def create_app(image_dir=None):
    """Create and configure the Flask application.
    
    Args:
        image_dir (str, optional): Directory containing images to display.
            Defaults to None.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    instance = Flask(__name__)
    instance.config['IMAGE_DIR'] = image_dir
    
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
        
        return render_template('index.html', 
                              directories=directories,
                              images=images,
                              current_path="",
                              parent_path=None)
    
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
            
        target_dir = Path(base_dir) / path
        target_dir = target_dir.resolve()
        base_path = Path(base_dir).resolve()
        
        # Security check - prevent directory traversal attacks
        try:
            target_dir.relative_to(base_path)
        except ValueError:
            return "Access denied.", 403
            
        if not target_dir.exists() or not target_dir.is_dir():
            return "Directory not found.", 404
            
        # Calculate parent path for navigation
        parent_path = str(Path(path).parent) if path else None
        if parent_path == '.':
            parent_path = ''
        
        directories = get_directories(target_dir, base_path=path)
        images = get_formatted_images(target_dir, base_path=path)
        
        return render_template('index.html',
                              directories=directories,
                              images=images,
                              current_path=path,
                              parent_path=parent_path)
    
    @instance.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve an image from the configured image directory.
        
        Args:
            filename (str): Path to image file relative to image directory.
            
        Returns:
            Response: Flask response containing the requested image.
        """
        base_dir = instance.config.get('IMAGE_DIR')
        return send_from_directory(base_dir, filename)
    
    # 外部からの画像表示を許可するためにCORSヘッダーを追加
    @instance.after_request
    def add_header(response):
        """Add headers to allow cross-origin requests.
        
        Args:
            response: Flask response object.
            
        Returns:
            Response: Modified response with CORS headers.
        """
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    return instance

def get_directories(directory, base_path=''):
    """Get subdirectories from the specified directory.
    
    Args:
        directory (str or Path): Directory to scan for subdirectories.
        base_path (str, optional): Base path for URL construction. Defaults to ''.
        
    Returns:
        list: List of directory information dictionaries.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
        
    result = []
    
    for item in dir_path.iterdir():
        if item.is_dir():
            # パスの結合とURLの正規化
            url_path_parts = Path(base_path) / item.name
            url_path = f"/browse/{url_path_parts}".replace('\\', '/')
            result.append({
                'name': item.name,
                'path': url_path
            })
            
    return sorted(result, key=lambda x: x['name'])

def get_formatted_images(directory, base_path=''):
    """Get images from directory with proper URL paths.
    
    Args:
        directory (str or Path): Directory to scan for image files.
        base_path (str, optional): Base path for URL construction. Defaults to ''.
        
    Returns:
        list: List of image information dictionaries with absolute URLs.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
        
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    result = []
    
    for item in dir_path.iterdir():
        if item.is_file() and item.suffix.lower() in image_extensions:
            # パスの結合とURLの正規化
            url_path_parts = Path(base_path) / item.name
            url_path = f"/images/{url_path_parts}".replace('\\', '/')
            result.append({
                'name': item.name,
                'path': url_path
            })
            
    return sorted(result, key=lambda x: x['name'])

if __name__ == '__main__':
    app = create_app(image_dir='path/to/images')
    app.run(debug=True, host='0.0.0.0')