import os

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
        """Render the index page with directory structure."""
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
            
        target_dir = os.path.normpath(os.path.join(base_dir, path))
        
        # Security check - prevent directory traversal attacks
        if not os.path.commonpath([target_dir, base_dir]) == base_dir:
            return "Access denied.", 403
            
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            return "Directory not found.", 404
            
        # Calculate parent path for navigation
        parent_path = os.path.dirname(path) if path else None
        
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
        return send_from_directory(instance.config['IMAGE_DIR'], filename)
    
    return instance

def get_directories(directory, base_path=''):
    """Get subdirectories from the specified directory.
    
    Args:
        directory (str): Directory to scan for subdirectories.
        base_path (str, optional): Base path for URL construction. Defaults to ''.
        
    Returns:
        list: List of directory information dictionaries.
    """
    if not os.path.exists(directory):
        return []
        
    result = []
    
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            url_path = f"/browse/{os.path.join(base_path, item)}".replace('\\', '/')
            result.append({
                'name': item,
                'path': url_path
            })
            
    return sorted(result, key=lambda x: x['name'])

def get_formatted_images(directory, base_path=''):
    """Get images from directory with proper URL paths.
    
    Args:
        directory (str): Directory to scan for image files.
        base_path (str, optional): Base path for URL construction. Defaults to ''.
        
    Returns:
        list: List of image information dictionaries.
    """
    if not os.path.exists(directory):
        return []
        
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    result = []
    
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) and os.path.splitext(item)[1].lower() in image_extensions:
            url_path = f"/images/{os.path.join(base_path, item)}".replace('\\', '/')
            result.append({
                'name': item,
                'path': url_path
            })
            
    return sorted(result, key=lambda x: x['name'])

if __name__ == '__main__':
    app = create_app(image_dir='path/to/images')
    app.run(debug=True)