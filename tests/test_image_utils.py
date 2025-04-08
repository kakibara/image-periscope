import os
import pytest
from image_viewer.image_utils import get_image_list

def test_get_image_list():
    """Test the get_image_list function for various directory structures."""
    
    # Create a temporary directory structure for testing
    test_dir = 'test_images'
    os.makedirs(os.path.join(test_dir, 'subdir1'), exist_ok=True)
    os.makedirs(os.path.join(test_dir, 'subdir2'), exist_ok=True)
    
    # Create some test image files
    with open(os.path.join(test_dir, 'image1.jpg'), 'w') as f:
        f.write('This is a test image file.')
    with open(os.path.join(test_dir, 'subdir1', 'image2.png'), 'w') as f:
        f.write('This is another test image file.')
    with open(os.path.join(test_dir, 'subdir2', 'image3.gif'), 'w') as f:
        f.write('This is yet another test image file.')

    # Test the function
    image_list = get_image_list(test_dir)
    
    # Check if the image list contains the correct paths
    expected_images = [
        os.path.join(test_dir, 'image1.jpg'),
        os.path.join(test_dir, 'subdir1', 'image2.png'),
        os.path.join(test_dir, 'subdir2', 'image3.gif')
    ]
    
    assert sorted(image_list) == sorted(expected_images)

    # Clean up the temporary directory
    for root, dirs, files in os.walk(test_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(test_dir)