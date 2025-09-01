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
    temp_dir = Path(tempfile.mkdtemp())
    # テスト用のディレクトリ構造を作成
    (temp_dir / "subdir1").mkdir()
    (temp_dir / "image1.jpg").write_text("dummy data")
    (temp_dir / "subdir1" / "image2.png").write_text("dummy data")

    yield temp_dir

    # クリーンアップ
    shutil.rmtree(temp_dir)


def test_get_image_list(test_image_dir):
    """get_image_list関数が正しく画像ファイルのリストを返すことをテストする。
    Args:
        test_image_dir: テスト画像用の一時ディレクトリ
    """
    # get_image_list を呼び出し
    image_list = get_image_list(test_image_dir)

    # 結果を検証
    assert len(image_list) == 2
    # 'image1.jpg' と 'subdir1/image2.png' が含まれていることを確認
    paths = [img["path"] for img in image_list]
    assert "image1.jpg" in paths
    assert str(Path("subdir1") / "image2.png") in paths
