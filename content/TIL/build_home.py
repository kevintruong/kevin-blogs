import os
from datetime import timezone
import git
import pathlib
from os.path import relpath

root = pathlib.Path(__file__).parent.resolve()


def created_changed_times(repo_path, ref="master"):
    created_changed_times = {}
    repo = git.Repo(repo_path, odbt=git.GitDB, search_parent_directories=True)
    git_root = repo.git.rev_parse("--show-toplevel")
    commits = reversed(list(repo.iter_commits(ref)))
    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())
        for filepath in affected_files:
            if filepath not in created_changed_times:
                created_changed_times[filepath] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )
    return created_changed_times, git_root


def get_title_of_doc(body: str):
    title_line = [line for line in body.split('\n') if "title: " in line]
    title_str = title_line[0].lstrip("title: ").strip()
    print(title_str)
    return title_str


def prepare_topic_records(repo_path):
    all_times, git_root = created_changed_times(repo_path)

    topic_dirs = [f.path for f in os.scandir(root) if f.is_dir()]

    for each_topic_dir in topic_dirs:
        topic = os.path.basename(each_topic_dir)
        adoc_files = list(pathlib.Path(each_topic_dir).glob('*.adoc'))
        records = []
        for filepath in adoc_files:
            fp = filepath.open()
            body = fp.read().strip()
            title = get_title_of_doc(body)
            path = str(filepath.relative_to(root))
            git_path_file = relpath(filepath, git_root)
            url = "https://github.com/kevintruong/kevin-blogs/blob/master/{}".format(path)
            record = {
                "path": path,
                "title": title,
                "url": url,
                "body": body,
            }
            record.update(all_times[git_path_file])
            records.append(record)
        yield {'topic': topic, 'info': records}


def dump_topic_records_to_index(topic_records: dict, til_home):
    til_home.write("=== {} \n".format(topic_records['topic']))
    for each_til in topic_records['info']:
        til_home.write("* link:{}[{}] {}".format(each_til['path'].replace('.adoc', '').lower(),
                                                 each_til["title"].replace('"', ""),
                                                 each_til["created"].split("T")[0]))
    pass


if __name__ == "__main__":
    home_file = root.joinpath("_index.adoc")
    temp_home_file = root.joinpath("_index.adoc.in")
    temp_content = temp_home_file.open().read()
    with open(home_file, "w") as til_home:
        til_home.write(temp_content)
        for recors in prepare_topic_records(root):
            dump_topic_records_to_index(recors, til_home)
