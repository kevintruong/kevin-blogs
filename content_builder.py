import abc
import shutil
from pathlib import Path
from build_home import *
import yaml


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
        git.Repo.clone_from(self.url, self.path, branch=self.branch)
        if self.update:
            index_generate(abs_dir_path)


class Action(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        pass


class IndexGenerateAction(Action):

    def __init__(self, actionobj: dict):
        self.actionObj = actionobj
        self.paths = []
        for each_path in self.actionObj['paths']:
            self.paths.append(each_path['path'])
        pass

    def execute(self):
        for each_path in self.paths:
            abs_current_path = pathlib.Path(__file__).parent.resolve()
            abs_dir_path = os.path.join(abs_current_path, each_path)
            print(f"run Index generate for path {abs_dir_path}")
            index_generate(Path(abs_dir_path), True)
        pass


class ActionGenerator:

    @classmethod
    def action_generator(cls, actionObj: dict):
        if actionObj['action'] == "index_generate":
            return IndexGenerateAction(actionObj)
        pass


if __name__ == '__main__':
    content_cfg = open("content_conf.yml")
    config = yaml.load(content_cfg, Loader=yaml.FullLoader)
    for each_content in config['contents']:
        content = Content(each_content)
        content.clone_content()
    if config['actions']:
        for each_action in config['actions']:
            act = ActionGenerator.action_generator(each_action)
            act.execute()
