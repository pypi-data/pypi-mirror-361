# project_odysseus/applications/sdk.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology.models import OntologyModel
from governance.access_control import check_permission

class OntologySDK:
    """
    개발자가 프로그래밍 방식으로 온톨로지와 상호작용할 수 있도록 제공하는 SDK입니다.
    데이터 조회, 액션 실행 등의 기능을 포함합니다.
    """
    def __init__(self, ontology_model: OntologyModel, user: str):
        self.ontology_model = ontology_model
        self.user = user # SDK를 사용하는 현재 사용자
        print(f"✅ OntologySDK 초기화 완료 (사용자: {self.user}).")

    @check_permission(required_role='viewer')
    def query(self, sparql_query: str):
        """
        SPARQL 쿼리를 실행하여 온톨로지에서 정보를 조회합니다.
        'viewer' 역할 이상이 필요합니다.
        """
        print(f"\n🔍 SDK 쿼리 실행 (사용자: {self.user})...")
        results = self.ontology_model.graph.query(sparql_query)
        print(f"   -> 쿼리 결과: {len(results)} 개 행 반환")
        return results

    # 여기에 객체 수정/삭제 등 더 많은 '액션' 메서드 추가 가능
    # @check_permission(required_role='manager')
    # def update_object_property(...):
    #     ...
