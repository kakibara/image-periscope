import shutil
import tempfile
from pathlib import Path

import pytest

from image_viewer.image_utils import get_image_list


@pytest.fixture
def test_image_dir():
    """テスト用の一時画像ディレクトリを作成する。
    
    テスト用の画像ファイルとサブディレクトリを含む一時ディレクトリを作成し、
    テスト後に自動的にクリーンアップする。
    
    Returns:
        Path: 一時ディレクトリのパス
    """
    # 一時ディレクトリを作成
    temp_dir = Path(tempfile.mkdtemp())
    
    # テスト用のディレクトリ構造を作成
    (temp_dir / "subdir1").mkdir()
    (temp_dir / "subdir2").mkdir()
    
    # テスト画像ファイルを作成
    (temp_dir / "image1.jpg").write_text("This is a test image file.")
    (temp_dir / "subdir1" / "image2.png").write_text("This is another test image file.")
    (temp_dir / "subdir2" / "image3.gif").write_text("This is yet another test image file.")
    
    yield temp_dir
    
    # テスト後に一時ディレクトリを削除
    shutil.rmtree(temp_dir)


def test_get_image_list(test_image_dir):
    """get_image_list関数が正しく画像ファイルのリストを返すことをテストする。
    
    Args:
        test_image_dir: テスト画像用の一時ディレクトリ
    """
    # 関数をテスト
    image_list = get_image_list(test_image_dir)
    
    # 結果を検証
    assert len(image_list) == 3
    
    # 各画像がリストに含まれているか確認
    paths = {str(img["path"]): img["name"] for img in image_list}
    
    assert "image1.jpg" in paths.values()
    assert "image2.png" in paths.values()
    assert "image3.gif" in paths.values()
    
    # パスが正しく取得されているか確認
    assert any(path.endswith("image1.jpg") for path in paths.keys())
    assert any("subdir1" in path and path.endswith("image2.png") for path in paths.keys())
    assert any("subdir2" in path and path.endswith("image3.gif") for path in paths.keys())