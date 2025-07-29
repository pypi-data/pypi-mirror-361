# project_odysseus/connectors/implementations.py
import pandas as pd
import sqlite3
from .base import BaseConnector

class FileConnector(BaseConnector):
    """
    CSV, JSON 등 파일 기반 데이터 소스를 위한 커넥터입니다.
    """
    def __init__(self, file_path: str, file_type: str = 'csv'):
        self.file_path = file_path
        self.file_type = file_type
        print(f"✅ FileConnector 초기화: {self.file_path}")

    def connect(self):
        """파일 시스템에 접근하므로 별도 연결 과정은 없습니다."""
        print(f"   -> 파일 시스템에 접근 준비 완료.")
        pass

    def read(self) -> pd.DataFrame:
        """파일을 읽어 DataFrame으로 반환합니다."""
        print(f"   -> 파일 읽기 시도: {self.file_path}")
        if self.file_type == 'csv':
            return pd.read_csv(self.file_path)
        # 여기에 JSON, Parquet 등 다른 파일 타입에 대한 로직 추가 가능
        raise ValueError(f"지원하지 않는 파일 타입입니다: {self.file_type}")


class DatabaseConnector(BaseConnector):
    """
    SQLAlchemy를 활용하여 데이터베이스에 연결하기 위한 커넥터입니다.
    이 예제에서는 가벼운 SQLite를 사용합니다.
    """
    def __init__(self, db_path: str, query: str):
        self.db_path = db_path
        self.query = query
        self.connection = None
        print(f"✅ DatabaseConnector 초기화: {self.db_path}")

    def connect(self):
        """데이터베이스에 연결합니다."""
        print(f"   -> DB 연결 시도...")
        self.connection = sqlite3.connect(self.db_path)
        print(f"   -> DB 연결 성공.")

    def read(self) -> pd.DataFrame:
        """쿼리를 실행하여 결과를 DataFrame으로 반환합니다."""
        if not self.connection:
            raise ConnectionError("DB에 먼저 연결해야 합니다.")
        print(f"   -> DB 쿼리 실행: {self.query}")
        return pd.read_sql_query(self.query, self.connection)
