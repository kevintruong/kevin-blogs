from datetime import timezone
import git
import pathlib
import sqlite_utils

root = pathlib.Path(__file__).parent.resolve()


def created_changed_times(repo_path, ref="master"):
    created_changed_times = {}
    repo = git.Repo(repo_path, odbt=git.GitDB, search_parent_directories=True)
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
    return created_changed_times


def get_title_of_doc(body: str):
    title_line = [line for line in body.split('\n') if "title: " in line]
    title_str= title_line[0].lstrip("title: ").strip()
    print(title_str)
    return title_str


def build_database(repo_path):
    all_times = created_changed_times(repo_path)
    db = sqlite_utils.Database(repo_path / "til.db")
    table = db.table("til", pk="path")
    for filepath in root.glob("*/*.adoc"):
        fp = filepath.open()
        body = fp.read().strip()
        title = get_title_of_doc(body)
        path = str(filepath.relative_to(root))
        url = "https://github.com/kevintruong/kevin-blogs/blob/master/{}".format(path)
        record = {
            "path": path.replace("/", "_").replace("-","_"),
            "topic": path.split("/")[0],
            "title": title,
            "url": url,
            "body": body,
        }
        record.update(all_times[path])
        table.insert(record)
    if "til_fts" not in db.table_names():
        table.enable_fts(["title", "body"])


if __name__ == "__main__":
    build_database(root)
