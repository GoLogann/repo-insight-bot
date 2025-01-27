import json
from datetime import datetime
from app.core.config import settings
import traceback


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class DocumentProcessor:
    @staticmethod
    def process_repository_data(repo_data):
        chunks = []
        for commit in repo_data:
            try:
                if not isinstance(commit, dict):
                    try:
                        commit_dict = commit.__dict__
                    except AttributeError:
                        commit_dict = {attr: getattr(commit, attr) for attr in dir(commit)
                                       if not attr.startswith('__') and not callable(getattr(commit, attr))}
                else:
                    commit_dict = commit.copy()

                for key, value in commit_dict.items():
                    if isinstance(value, datetime):
                        commit_dict[key] = value.isoformat()

                data = json.dumps(commit_dict, cls=CustomJSONEncoder)

                for i in range(0, len(data), settings.CHUNK_SIZE):
                    chunk = data[i:i + settings.CHUNK_SIZE]
                    chunks.append(chunk)

            except Exception as e:
                print(f"Erro ao processar commit: {e}")
                print(traceback.format_exc())
                continue

        return chunks
