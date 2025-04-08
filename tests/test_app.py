import os
import pytest
from flask import Flask, render_template
from image_viewer.app import create_app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Image Viewer' in response.data

def test_gallery_page(client):
    """Test the gallery page loads successfully with images."""
    # Assuming there is a directory with images for testing
    test_directory = 'path/to/test/images'
    response = client.get(f'/gallery?directory={test_directory}')
    assert response.status_code == 200
    assert b'Image Gallery' in response.data

def test_invalid_directory(client):
    """Test handling of an invalid directory."""
    response = client.get('/gallery?directory=invalid_directory')
    assert response.status_code == 404
    assert b'Directory not found' in response.data

def test_empty_directory(client):
    """Test handling of an empty directory."""
    empty_directory = 'path/to/empty/directory'
    response = client.get(f'/gallery?directory={empty_directory}')
    assert response.status_code == 200
    assert b'No images found' in response.data