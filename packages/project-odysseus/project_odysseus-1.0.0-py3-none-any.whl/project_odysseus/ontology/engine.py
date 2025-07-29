# project_odysseus/ontology/engine.py
import pandas as pd
from .models import OntologyModel

class MappingEngine:
    """
    데이터 소스(DataFrame)의 데이터를 온톨로지 모델에 매핑하는 역할을 담당합니다.
    """
    def __init__(self, ontology_model: OntologyModel):
        self.ontology_model = ontology_model
        print("✅ MappingEngine 초기화 완료.")

    def map_to_ontology(self,
                          df: pd.DataFrame,
                          class_name: str,
                          id_column: str,
                          property_mappings: dict,
                          link_mappings: dict = None):
        """
        DataFrame의 각 행을 순회하며 온톨로지 객체와 관계로 변환합니다.

        :param df: 소스 데이터프레임
        :param class_name: 매핑될 온톨로지 클래스 이름
        :param id_column: 객체의 고유 ID로 사용될 컬럼
        :param property_mappings: {'온톨로지속성': 'DF컬럼명'}
        :param link_mappings: {'온톨로지관계': '연결될객체ID컬럼명'}
        """
        print(f"   -> '{class_name}' 클래스로 데이터 매핑 시작...")
        for _, row in df.iterrows():
            obj_id = f"{class_name.lower()}_{row[id_column]}"

            # 속성 매핑
            properties = {
                prop: row[col] for prop, col in property_mappings.items()
            }
            self.ontology_model.add_object(obj_id, class_name, properties)

            # 관계 매핑
            if link_mappings:
                for link_prop, target_id_col in link_mappings.items():
                    target_class_name = link_prop.split('_to_')[1] # 'works_for_to_Company' -> 'Company'
                    target_obj_id = f"{target_class_name.lower()}_{row[target_id_col]}"
                    self.ontology_model.add_link(obj_id, link_prop, target_obj_id)
        print(f"   -> 매핑 완료.")
