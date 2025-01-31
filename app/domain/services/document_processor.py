import json
import logging
import traceback
from datetime import datetime
from typing import Any, List
from app.core.config import settings

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class DocumentProcessor:
    @staticmethod
    def _create_chunks(data: str) -> List[str]:
        return [data[i:i + settings.CHUNK_SIZE] for i in range(0, len(data), settings.CHUNK_SIZE)]

    @staticmethod
    def process_repository_data(repo_data: str) -> List[str]:
        """
        Processa os dados de um reposit rio, separando-os em chunks menores para
        posteriormente serem enviados para o Elasticsearch.

        :param repo_data: Dados do reposit rio em formato de string no formato JSON
        :return: Uma lista de strings, cada uma representando um chunk do dado
        """
        chunks = []

        try:
            data = json.loads(repo_data)

            json_data = json.dumps(data, cls=CustomJSONEncoder)

            chunks = DocumentProcessor._create_chunks(json_data)

        except json.JSONDecodeError as e:
            logging.error(f"Erro ao decodificar JSON: {e}")
            logging.error(traceback.format_exc())
        except Exception as e:
            logging.error(f"Erro ao processar dado: {e}")
            logging.error(traceback.format_exc())

        return chunks