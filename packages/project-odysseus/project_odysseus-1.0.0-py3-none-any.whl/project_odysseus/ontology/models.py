# project_odysseus/ontology/models.py
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD

# 프로젝트 전반에서 사용할 네임스페이스 정의
ODS = Namespace("http://project-odysseus.com/ontology#")

class OntologyModel:
    """
    온톨로지의 핵심 구성요소(그래프, 스키마)를 관리하는 중앙 클래스입니다.
    모든 데이터는 이 클래스를 통해 RDF 그래프로 통합됩니다.
    """
    def __init__(self):
        self.graph = Graph()
        # 네임스페이스 바인딩으로 가독성 높은 TTL 파일 생성
        self.graph.bind("ods", ODS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)
        print("✅ OntologyModel (지식 그래프) 초기화 완료.")

    def define_class(self, class_name: str, label: str):
        """온톨로지에 '클래스(객체 타입)'를 정의합니다."""
        class_uri = ODS[class_name]
        self.graph.add((class_uri, RDF.type, RDFS.Class))
        self.graph.add((class_uri, RDFS.label, Literal(label, lang='en')))
        print(f"   -> 온톨로지 클래스 정의: {class_name}")

    def define_property(self, prop_name: str, domain_class: str, range_type: URIRef):
        """온톨로지에 '속성'을 정의합니다."""
        prop_uri = ODS[prop_name]
        domain_uri = ODS[domain_class]
        self.graph.add((prop_uri, RDF.type, RDF.Property))
        self.graph.add((prop_uri, RDFS.domain, domain_uri))
        self.graph.add((prop_uri, RDFS.range, range_type))
        print(f"   -> 온톨로지 속성 정의: {prop_name}")

    def add_object(self, object_id: str, class_name: str, properties: dict):
        """
        실제 데이터 '객체(인스턴스)'를 그래프에 추가합니다.
        """
        object_uri = ODS[object_id]
        class_uri = ODS[class_name]
        self.graph.add((object_uri, RDF.type, class_uri))
        for prop_name, value in properties.items():
            prop_uri = ODS[prop_name]
            # 데이터 타입에 맞게 Literal 생성
            if isinstance(value, int):
                literal_value = Literal(value, datatype=XSD.integer)
            elif isinstance(value, float):
                literal_value = Literal(value, datatype=XSD.double)
            else:
                literal_value = Literal(value, datatype=XSD.string)
            self.graph.add((object_uri, prop_uri, literal_value))
        return object_uri

    def add_link(self, subject_id: str, link_prop_name: str, object_id: str):
        """두 객체 간의 '관계(Link)'를 설정합니다."""
        subject_uri = ODS[subject_id]
        link_prop_uri = ODS[link_prop_name]
        object_uri = ODS[object_id]
        self.graph.add((subject_uri, link_prop_uri, object_uri))

    def save(self, file_path: str, format: str = "turtle"):
        """현재 그래프 상태를 파일로 저장합니다."""
        self.graph.serialize(destination=file_path, format=format)
        print(f"\n💾 지식 그래프가 '{file_path}' 파일로 저장되었습니다.")
