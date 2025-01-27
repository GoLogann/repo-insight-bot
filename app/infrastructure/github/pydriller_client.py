from pydriller import Repository

class PyDrillerClient:
    @staticmethod
    def fetch_repository_data(repo_url: str):
        commits = []
        for commit in Repository(repo_url).traverse_commits():
            commits.append({
                "hash": commit.hash,
                "author": commit.author.name,
                "date": commit.author_date,
                "message": commit.msg,
                "files": [mod.filename for mod in commit.modified_files]
            })
        return commits