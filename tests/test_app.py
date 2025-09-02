import shutil
import tempfile
from pathlib import Path

import pytest
from flask import Flask

from image_periscope.app import create_app, get_directories, get_formatted_images


@pytest.fixture
def test_image_dir():
    """Creates a temporary image directory for testing.
    Sets up a test environment with directories and sample image files.
    Returns:
        str: Path to temporary directory
    """
    # 一時ディレクトリを作成
    temp_dir = Path(tempfile.mkdtemp())

    # テスト用のディレクトリ構造を作成
    (temp_dir / "subdir1").mkdir()
    (temp_dir / "subdir2" / "nested").mkdir(parents=True)

    # テスト画像ファイルを作成
    (temp_dir / "image1.jpg").write_text("dummy data")
    (temp_dir / "subdir1" / "image2.png").write_text("dummy data")
    (temp_dir / "subdir2" / "image3.gif").write_text("dummy data")
    (temp_dir / "not_image.txt").write_text("dummy text file")

    yield str(temp_dir)

    # テスト後にディレクトリを削除
    shutil.rmtree(temp_dir)

@pytest.fixture
def app(test_image_dir):
    """テスト用のFlaskアプリケーションを作成するフィクスチャ。

    Args:
        test_image_dir (str): テスト用画像ディレクトリのパス

    Returns:
        Flask: テスト用Flaskアプリケーション
    """
    app = create_app(test_image_dir)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """テストクライアントを作成するフィクスチャ。

    Args:
        app (Flask): テスト用Flaskアプリケーション

    Returns:
        FlaskClient: テスト用クライアント
    """
    return app.test_client()

def test_create_app():
    """create_app関数が正しくFlaskアプリケーションを作成することをテスト。"""
    app = create_app()
    assert isinstance(app, Flask)
    assert app.config.get("IMAGE_DIR") is None

    app = create_app("/test/path")
    assert app.config.get("IMAGE_DIR") == "/test/path"

def test_index_route(client):
    """インデックスルートが正しくレンダリングされることをテスト。"""
    response = client.get("/")
    assert response.status_code == 200

def test_index_route_invalid_dir(client, app):
    """存在しないディレクトリを設定した場合のインデックスルートをテスト。"""
    app.config["IMAGE_DIR"] = "/invalid/directory"
    response = client.get("/")
    assert response.status_code == 400
    assert b"Image directory not configured or not found." in response.data

def test_browse_route(client, test_image_dir):
    """ブラウズルートが正しくディレクトリをナビゲートすることをテスト。"""
    response = client.get("/browse/subdir1")
    assert response.status_code == 200
    assert b"image2.png" in response.data

def test_browse_route_invalid_path(client):
    """存在しないパスへのブラウズルートをテスト。"""
    response = client.get("/browse/invalid_path")
    assert response.status_code == 404

def test_serve_image(client, test_image_dir):
    """画像サービングルートが正しく画像を提供することをテスト。"""
    response = client.get("/images/image1.jpg")
    assert response.status_code == 200
    assert response.data == b"dummy data"

def test_get_directories(test_image_dir):
    """get_directories関数がディレクトリ情報を正しく取得することをテスト。"""
    directories = get_directories(test_image_dir)
    assert len(directories) == 2
    assert any(d["name"] == "subdir1" for d in directories)
    assert any(d["name"] == "subdir2" for d in directories)

    # ベースパスを設定してテスト
    nested_dirs = get_directories(Path(test_image_dir) / "subdir2", "subdir2")
    assert len(nested_dirs) == 1
    assert nested_dirs[0]["name"] == "nested"
    assert nested_dirs[0]["path"] == "/browse/subdir2/nested"

def test_get_formatted_images(test_image_dir):
    """get_formatted_images関数が画像情報を正しく取得することをテスト。"""
    images = get_formatted_images(test_image_dir)
    assert len(images) == 1  # トップレベルにはimage1.jpgのみ
    assert images[0]["name"] == "image1.jpg"
    assert images[0]["path"] == "/images/image1.jpg"

    # サブディレクトリの画像
    subdir_images = get_formatted_images(Path(test_image_dir) / "subdir1", "subdir1")
    assert len(subdir_images) == 1
    assert subdir_images[0]["name"] == "image2.png"
    assert subdir_images[0]["path"] == "/images/subdir1/image2.png"
