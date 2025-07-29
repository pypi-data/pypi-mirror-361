import pytest
from pathlib import Path
from unittest.mock import MagicMock

from r2pb.fetcher import RosMsgFetcher, ROS_MSG_REPOS


@pytest.fixture
def mock_git_repo(monkeypatch):
    """模拟 git.Repo 类及其 clone_from 方法。"""
    mock_repo_instance = MagicMock()
    mock_repo_class = MagicMock(return_value=mock_repo_instance)

    def mock_clone_from_side_effect(url, path):
        repo_dir = Path(path)
        # 模拟 `git clone`: 创建仓库根目录
        repo_dir.mkdir(parents=True, exist_ok=True)

        # 在仓库内创建模拟的包目录
        repo_name = Path(url).stem
        if repo_name == "common_msgs":
            (repo_dir / "sensor_msgs").mkdir()
        elif repo_name == "std_msgs":
            (repo_dir / "std_msgs").mkdir()

        # clone_from 应该返回一个 Repo 实例
        return mock_repo_instance

    # 1. 使用 monkeypatch 替换真实的的 Repo 类为一个 Mock 类
    monkeypatch.setattr("r2pb.fetcher.Repo", mock_repo_class)

    # 2. 配置 Mock 类的 clone_from 方法的行为
    #    它现在是一个具有 side_effect 的 MagicMock，可以被断言
    mock_repo_class.clone_from.side_effect = mock_clone_from_side_effect

    return mock_repo_class, mock_repo_instance


@pytest.fixture
def fetcher(tmp_path):
    """创建一个使用临时缓存目录的 RosMsgFetcher 实例。"""
    return RosMsgFetcher(cache_dir=tmp_path)


def test_fetch_package_clone(fetcher, mock_git_repo, tmp_path):
    """测试当缓存为空时，是否会克隆仓库。"""
    mock_repo_class, _ = mock_git_repo
    repo_url = ROS_MSG_REPOS["std_msgs"]
    package_path = fetcher.fetch_package("std_msgs", repo_url)

    # 验证 clone_from 被正确调用
    mock_repo_class.clone_from.assert_called_once_with(repo_url, tmp_path / "std_msgs")
    # 验证返回的路径是否正确
    assert package_path == tmp_path / "std_msgs" / "std_msgs"


def test_fetch_package_update(fetcher, mock_git_repo, tmp_path):
    """测试当仓库已存在时，是否会执行更新。"""
    mock_repo_class, mock_repo_instance = mock_git_repo
    repo_url = ROS_MSG_REPOS["std_msgs"]
    repo_path = tmp_path / "std_msgs"

    # 预先创建目录，模拟仓库已存在
    (repo_path / "std_msgs").mkdir(parents=True)

    fetcher.fetch_package("std_msgs", repo_url)

    # 验证是实例化的 Repo 对象，而不是 clone
    mock_repo_class.assert_called_with(repo_path)
    # 验证 pull 被调用
    mock_repo_instance.remotes.origin.pull.assert_called_once()


def test_find_and_fetch_known_package(fetcher, mock_git_repo):
    """测试查找一个已知的、有自己仓库的包。"""
    package_path = fetcher.find_and_fetch("std_msgs")
    assert package_path.name == "std_msgs"
    assert package_path.parent.name == "std_msgs"


def test_find_and_fetch_package_in_common_msgs(fetcher, mock_git_repo):
    """测试在 common_msgs 中查找一个包。"""
    package_path = fetcher.find_and_fetch("sensor_msgs")
    assert package_path.name == "sensor_msgs"
    assert package_path.parent.name == "common_msgs"


def test_find_and_fetch_package_not_found(fetcher, mock_git_repo):
    """测试当包在任何地方都找不到时，是否抛出 KeyError。"""
    with pytest.raises(KeyError, match="'non_existent_pkg' not found"):
        fetcher.find_and_fetch("non_existent_pkg")


def test_fetch_package_not_in_repo(fetcher, mock_git_repo):
    """测试当仓库中不包含请求的包时，是否抛出 FileNotFoundError。"""
    repo_url = ROS_MSG_REPOS["std_msgs"]
    with pytest.raises(
        FileNotFoundError, match="'wrong_pkg' not found in repository 'std_msgs'"
    ):
        fetcher.fetch_package("wrong_pkg", repo_url)
