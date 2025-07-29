# project_odysseus/ontology/advanced_models.py
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL
from .models import OntologyModel, ODS
from governance.logger import audit_logger

@dataclass
class ObjectProperty:
    """
    온톨로지 객체 속성 정의
    """
    name: str
    value: Any
    data_type: str
    is_required: bool = False
    constraints: Optional[Dict] = None
    provenance: Optional[str] = None
    last_updated: Optional[datetime] = None

@dataclass
class ObjectRelationship:
    """
    객체 간의 관계 정의
    """
    subject: str
    predicate: str
    object: str
    relationship_type: str
    confidence: float = 1.0
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    provenance: Optional[str] = None

class AdvancedOntologyModel(OntologyModel):
    """
    고급 온톨로지 모델 - 상속, 추론, 시계열 데이터 지원
    """
    
    def __init__(self):
        super().__init__()
        # OWL 네임스페이스 추가
        self.graph.bind("owl", OWL)
        
        # 고급 기능을 위한 추가 구조
        self.class_hierarchy = {}
        self.property_constraints = {}
        self.inference_rules = []
        self.temporal_data = {}
        
        audit_logger.info("AdvancedOntologyModel 초기화 완료")
    
    def define_class_hierarchy(self, child_class: str, parent_class: str):
        """
        클래스 상속 관계 정의
        """
        child_uri = ODS[child_class]
        parent_uri = ODS[parent_class]
        
        # OWL 클래스 계층 구조 정의
        self.graph.add((child_uri, RDF.type, OWL.Class))
        self.graph.add((parent_uri, RDF.type, OWL.Class))
        self.graph.add((child_uri, RDFS.subClassOf, parent_uri))
        
        # 내부 계층 구조 저장
        if parent_class not in self.class_hierarchy:
            self.class_hierarchy[parent_class] = []
        self.class_hierarchy[parent_class].append(child_class)
        
        audit_logger.info(f"클래스 계층 정의: {child_class} → {parent_class}")
    
    def define_property_constraints(self, property_name: str, constraints: Dict):
        """
        속성 제약 조건 정의
        """
        prop_uri = ODS[property_name]
        
        # 카디널리티 제약
        if "min_cardinality" in constraints:
            min_card = constraints["min_cardinality"]
            restriction = BNode()
            self.graph.add((restriction, RDF.type, OWL.Restriction))
            self.graph.add((restriction, OWL.onProperty, prop_uri))
            self.graph.add((restriction, OWL.minCardinality, Literal(min_card)))
        
        if "max_cardinality" in constraints:
            max_card = constraints["max_cardinality"]
            restriction = BNode()
            self.graph.add((restriction, RDF.type, OWL.Restriction))
            self.graph.add((restriction, OWL.onProperty, prop_uri))
            self.graph.add((restriction, OWL.maxCardinality, Literal(max_card)))
        
        # 값 제약
        if "allowed_values" in constraints:
            allowed_values = constraints["allowed_values"]
            enumeration = BNode()
            self.graph.add((enumeration, RDF.type, OWL.Class))
            
            # OneOf 제약 생성
            value_list = BNode()
            self.graph.add((enumeration, OWL.oneOf, value_list))
            
            for value in allowed_values:
                value_literal = Literal(value)
                self.graph.add((value_list, RDF.first, value_literal))
                if len(allowed_values) > 1:
                    next_node = BNode()
                    self.graph.add((value_list, RDF.rest, next_node))
                    value_list = next_node
                else:
                    self.graph.add((value_list, RDF.rest, RDF.nil))
        
        self.property_constraints[property_name] = constraints
        audit_logger.info(f"속성 제약 조건 정의: {property_name}")
    
    def add_temporal_property(self, object_id: str, property_name: str, 
                            value: Any, timestamp: datetime, 
                            valid_until: Optional[datetime] = None):
        """
        시계열 속성 추가
        """
        object_uri = ODS[object_id]
        prop_uri = ODS[property_name]
        
        # 시간 기반 속성을 위한 복합 노드 생성
        temporal_node = BNode()
        self.graph.add((object_uri, prop_uri, temporal_node))
        
        # 시간 정보 추가
        self.graph.add((temporal_node, ODS.hasValue, Literal(value)))
        self.graph.add((temporal_node, ODS.validFrom, Literal(timestamp)))
        
        if valid_until:
            self.graph.add((temporal_node, ODS.validUntil, Literal(valid_until)))
        
        # 내부 시계열 데이터 저장
        if object_id not in self.temporal_data:
            self.temporal_data[object_id] = {}
        if property_name not in self.temporal_data[object_id]:
            self.temporal_data[object_id][property_name] = []
        
        self.temporal_data[object_id][property_name].append({
            "value": value,
            "timestamp": timestamp,
            "valid_until": valid_until
        })
        
        audit_logger.info(f"시계열 속성 추가: {object_id}.{property_name} @ {timestamp}")
    
    def add_inference_rule(self, rule_name: str, rule_definition: Dict):
        """
        추론 규칙 추가
        """
        rule = {
            "name": rule_name,
            "conditions": rule_definition.get("conditions", []),
            "conclusions": rule_definition.get("conclusions", []),
            "confidence": rule_definition.get("confidence", 1.0)
        }
        
        self.inference_rules.append(rule)
        audit_logger.info(f"추론 규칙 추가: {rule_name}")
    
    def apply_inference_rules(self) -> List[Dict]:
        """
        추론 규칙 적용하여 새로운 지식 생성
        """
        inferred_facts = []
        
        for rule in self.inference_rules:
            # 간단한 규칙 엔진 구현
            rule_results = self._apply_single_rule(rule)
            inferred_facts.extend(rule_results)
        
        audit_logger.info(f"추론 완료: {len(inferred_facts)}개 새로운 사실 생성")
        return inferred_facts
    
    def _apply_single_rule(self, rule: Dict) -> List[Dict]:
        """
        단일 추론 규칙 적용
        """
        results = []
        
        # SPARQL 쿼리로 조건 확인
        for condition in rule["conditions"]:
            query = condition.get("sparql_query", "")
            if query:
                query_results = self.graph.query(query)
                
                for result in query_results:
                    # 결론 생성
                    for conclusion in rule["conclusions"]:
                        inferred_fact = {
                            "subject": str(result.get("subject", "")),
                            "predicate": conclusion.get("predicate", ""),
                            "object": str(result.get("object", "")),
                            "confidence": rule["confidence"],
                            "rule_name": rule["name"]
                        }
                        results.append(inferred_fact)
        
        return results
    
    def get_class_instances(self, class_name: str) -> List[str]:
        """
        특정 클래스의 모든 인스턴스 반환
        """
        class_uri = ODS[class_name]
        
        query = f"""
        PREFIX ods: <{ODS}>
        SELECT ?instance WHERE {{
            ?instance a ods:{class_name} .
        }}
        """
        
        results = self.graph.query(query)
        instances = [str(result.instance).split("#")[-1] for result in results]
        
        return instances
    
    def get_property_values(self, object_id: str, property_name: str,
                          timestamp: Optional[datetime] = None) -> List[Any]:
        """
        객체의 속성 값 조회 (시계열 데이터 고려)
        """
        if timestamp and object_id in self.temporal_data:
            temporal_props = self.temporal_data[object_id].get(property_name, [])
            
            # 지정된 시간에 유효한 값 찾기
            valid_values = []
            for prop_data in temporal_props:
                valid_from = prop_data["timestamp"]
                valid_until = prop_data.get("valid_until")
                
                if valid_from <= timestamp and (not valid_until or timestamp <= valid_until):
                    valid_values.append(prop_data["value"])
            
            return valid_values
        
        # 일반적인 속성 값 조회
        object_uri = ODS[object_id]
        prop_uri = ODS[property_name]
        
        query = f"""
        PREFIX ods: <{ODS}>
        SELECT ?value WHERE {{
            ods:{object_id} ods:{property_name} ?value .
        }}
        """
        
        results = self.graph.query(query)
        values = [str(result.value) for result in results]
        
        return values
    
    def validate_constraints(self, object_id: str, properties: Dict) -> Dict:
        """
        객체 속성이 제약 조건을 만족하는지 검증
        """
        validation_results = {
            "valid": True,
            "violations": []
        }
        
        for prop_name, value in properties.items():
            if prop_name in self.property_constraints:
                constraints = self.property_constraints[prop_name]
                
                # 허용 값 확인
                if "allowed_values" in constraints:
                    if value not in constraints["allowed_values"]:
                        validation_results["valid"] = False
                        validation_results["violations"].append({
                            "property": prop_name,
                            "violation_type": "invalid_value",
                            "value": value,
                            "allowed_values": constraints["allowed_values"]
                        })
                
                # 데이터 타입 확인
                if "data_type" in constraints:
                    expected_type = constraints["data_type"]
                    if not self._validate_data_type(value, expected_type):
                        validation_results["valid"] = False
                        validation_results["violations"].append({
                            "property": prop_name,
                            "violation_type": "invalid_type",
                            "value": value,
                            "expected_type": expected_type
                        })
        
        return validation_results
    
    def _validate_data_type(self, value: Any, expected_type: str) -> bool:
        """
        데이터 타입 검증
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool
        }
        
        expected_python_type = type_mapping.get(expected_type.lower())
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True
    
    def export_ontology_schema(self) -> Dict:
        """
        온톨로지 스키마를 JSON 형태로 내보내기
        """
        schema = {
            "classes": {},
            "properties": {},
            "class_hierarchy": self.class_hierarchy,
            "property_constraints": self.property_constraints,
            "inference_rules": self.inference_rules
        }
        
        # 클래스 정보 추출
        class_query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?class ?label WHERE {
            ?class a rdfs:Class .
            OPTIONAL { ?class rdfs:label ?label }
        }
        """
        
        class_results = self.graph.query(class_query)
        for result in class_results:
            class_name = str(result["class"]).split("#")[-1]
            schema["classes"][class_name] = {
                "label": str(result["label"]) if result["label"] else "",
                "uri": str(result["class"])
            }
        
        # 속성 정보 추출
        prop_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?property ?domain ?range WHERE {
            ?property a rdf:Property .
            OPTIONAL { ?property rdfs:domain ?domain }
            OPTIONAL { ?property rdfs:range ?range }
        }
        """
        
        prop_results = self.graph.query(prop_query)
        for result in prop_results:
            prop_name = str(result["property"]).split("#")[-1]
            schema["properties"][prop_name] = {
                "domain": str(result["domain"]).split("#")[-1] if result["domain"] else "",
                "range": str(result["range"]).split("#")[-1] if result["range"] else "",
                "uri": str(result["property"])
            }
        
        return schema
