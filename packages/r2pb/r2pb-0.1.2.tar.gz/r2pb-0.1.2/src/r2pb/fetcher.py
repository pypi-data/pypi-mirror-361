import os
import shutil
import tempfile
from pathlib import Path
from git import Repo, GitCommandError

# 预设的 ROS 消息仓库
ROS_MSG_REPOS = {
    "common_msgs": "https://github.com/ros/common_msgs.git",
    "std_msgs": "https://github.com/ros/std_msgs.git",
    # ... 可以根据需要添加更多仓库
}


class RosMsgFetcher:
    """从远程 Git 仓库获取并缓存 ROS 消息包。"""

    def __init__(self, cache_dir: Path = None):
        if cache_dir is None:
            self.cache_dir = Path.home() / ".cache" / "r2pb"
        else:
            self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_package(self, package_name: str, repo_url: str) -> Path:
        """
        从指定的 Git 仓库 URL 下载或更新一个 ROS 包。

        Args:
            package_name: 要获取的包名 (例如 'sensor_msgs')。
            repo_url: 包含该包的 Git 仓库 URL。

        Returns:
            包在本地缓存中的路径。
        """
        repo_name = Path(repo_url).stem
        repo_path = self.cache_dir / repo_name

        try:
            if repo_path.exists():
                print(f"Updating repository: {repo_name}...")
                repo = Repo(repo_path)
                repo.remotes.origin.pull()
            else:
                print(f"Cloning repository: {repo_name} from {repo_url}...")
                Repo.clone_from(repo_url, repo_path)
        except GitCommandError as e:
            print(f"Error fetching repository {repo_url}: {e}")
            raise

        # Check if a subdirectory with the package name exists.
        # If not, assume the repo root is the package path (e.g., for std_msgs repo).
        package_path = repo_path / package_name
        if not package_path.is_dir():
            # If the subdirectory doesn't exist, maybe the repo itself is the package.
            if (repo_path / "package.xml").exists() or (repo_path / "msg").is_dir():
                return repo_path
            else:
                raise FileNotFoundError(
                    f"Package '{package_name}' not found in repository '{repo_name}'."
                )

        return package_path

    def find_and_fetch(self, package_name: str) -> Path:
        """
        在预设的仓库中查找并获取一个 ROS 包。

        Args:
            package_name: 要查找的包名。

        Returns:
            包在本地缓存中的路径。

        Raises:
            KeyError: 如果在任何预设的仓库中都找不到该包。
        """
        # 简单的实现：假设包名直接对应仓库名或在 common_msgs 中
        # 更复杂的实现可以查询一个清单文件
        if package_name in ROS_MSG_REPOS:
            repo_url = ROS_MSG_REPOS[package_name]
            return self.fetch_package(package_name, repo_url)

        # 尝试在 common_msgs 中查找
        common_msgs_url = ROS_MSG_REPOS.get("common_msgs")
        if common_msgs_url:
            try:
                return self.fetch_package(package_name, common_msgs_url)
            except FileNotFoundError:
                pass  # 在 common_msgs 中没找到，继续

        raise KeyError(f"Package '{package_name}' not found in any known repository.")
