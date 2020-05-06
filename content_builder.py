import shutil

import yaml
import pathlib
import git
from build_home import *


class Content:
    def __init__(self, info: dict):
        self.branch = "master"
        if "url" in info.keys():
            self.url = info['url']
        if "path" in info.keys():
            self.path = info['path']
        if "update" in info.keys():
            self.update = info['update']
        if "branch" in info.keys():
            self.branch = info['branch']

    def is_git_repo(self, path):
        try:
            _ = git.Repo(path).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False

    def clone_content(self):
        abs_dir_path = pathlib.Path(__file__).parent.absolute().joinpath(self.path)
        if os.path.isdir(abs_dir_path):
            shutil.rmtree(abs_dir_path)
        git.Repo.clone_from(self.url, self.path,branch=self.branch)
        if self.update:
            index_generate(abs_dir_path)


if __name__ == '__main__':
    content_cfg = open("content_conf.yml")
    config = yaml.load(content_cfg, Loader=yaml.FullLoader)
    for each_content in config['contents']:
        content = Content(each_content)
        content.clone_content()
