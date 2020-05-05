import yaml
import pathlib
import git
from build_home import *


class Content:
    def __init__(self, info: dict):
        if "url" in info.keys():
            self.url = info['url']
        if "path" in info.keys():
            self.path = info['path']
        if "update" in info.keys():
            self.update = info['update']

    def clone_content(self):
        abs_dir_path = pathlib.Path(__file__).parent.absolute().joinpath(self.path)
        git.Git(abs_dir_path).clone(self.url)
        if self.update:
            index_generate(abs_dir_path)


if __name__ == '__main__':
    content_cfg = open("content_conf.yml")
    config = yaml.load(content_cfg, Loader=yaml.FullLoader)
    for each_content in config['contents']:
        content = Content(each_content)
        content.clone_content()
