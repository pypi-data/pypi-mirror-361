# project_odysseus/connectors/base.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseConnector(ABC):
    """
    모든 데이터 커넥터가 상속받는 추상 기본 클래스입니다.
    데이터 소스에 연결하고, 데이터를 읽어오는 표준 인터페이스를 정의합니다.
    """
    @abstractmethod
    def connect(self):
        """데이터 소스에 대한 연결을 설정합니다."""
        pass

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """데이터를 읽어 Pandas DataFrame으로 반환합니다."""
        pass
