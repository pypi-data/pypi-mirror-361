# project_odysseus/governance/data_lineage.py
from datetime import datetime
from typing import Dict, List, Optional, Set
import json
import networkx as nx
from dataclasses import dataclass, asdict
from .logger import audit_logger

@dataclass
class DataLineageNode:
    """
    데이터 리니지 그래프의 노드를 나타내는 클래스
    """
    node_id: str
    node_type: str  # 'source', 'transformation', 'destination'
    name: str
    metadata: Dict
    created_at: datetime
    created_by: str

@dataclass
class DataLineageEdge:
    """
    데이터 리니지 그래프의 엣지를 나타내는 클래스
    """
    source_node: str
    target_node: str
    transformation_type: str  # 'extract', 'transform', 'load', 'aggregate', etc.
    metadata: Dict
    created_at: datetime
    created_by: str

class DataLineageTracker:
    """
    데이터의 전체 생명주기를 추적하는 데이터 리니지 관리자
    """
    
    def __init__(self):
        self.lineage_graph = nx.DiGraph()
        self.nodes: Dict[str, DataLineageNode] = {}
        self.edges: List[DataLineageEdge] = []
        audit_logger.info("DataLineageTracker 초기화 완료")
    
    def add_data_source(self, source_id: str, source_name: str, source_type: str, 
                       metadata: Dict, created_by: str) -> DataLineageNode:
        """
        데이터 소스 노드를 리니지 그래프에 추가
        """
        node = DataLineageNode(
            node_id=source_id,
            node_type="source",
            name=source_name,
            metadata={
                "source_type": source_type,
                "connection_info": metadata.get("connection_info", {}),
                "schema": metadata.get("schema", {}),
                "data_classification": metadata.get("data_classification", "internal")
            },
            created_at=datetime.now(),
            created_by=created_by
        )
        
        self.nodes[source_id] = node
        self.lineage_graph.add_node(source_id, **asdict(node))
        
        audit_logger.info(f"데이터 소스 추가: {source_name} (ID: {source_id})")
        return node
    
    def add_transformation(self, transformation_id: str, transformation_name: str,
                          input_sources: List[str], metadata: Dict, 
                          created_by: str) -> DataLineageNode:
        """
        데이터 변환 노드를 리니지 그래프에 추가
        """
        node = DataLineageNode(
            node_id=transformation_id,
            node_type="transformation",
            name=transformation_name,
            metadata={
                "transformation_logic": metadata.get("transformation_logic", ""),
                "input_count": len(input_sources),
                "transformation_type": metadata.get("transformation_type", "custom")
            },
            created_at=datetime.now(),
            created_by=created_by
        )
        
        self.nodes[transformation_id] = node
        self.lineage_graph.add_node(transformation_id, **asdict(node))
        
        # 입력 소스들과 연결
        for source_id in input_sources:
            self.add_lineage_edge(source_id, transformation_id, "transform", 
                                {"input_source": source_id}, created_by)
        
        audit_logger.info(f"데이터 변환 추가: {transformation_name} (입력: {len(input_sources)}개)")
        return node
    
    def add_destination(self, destination_id: str, destination_name: str,
                       source_transformation: str, metadata: Dict,
                       created_by: str) -> DataLineageNode:
        """
        데이터 목적지 노드를 리니지 그래프에 추가
        """
        node = DataLineageNode(
            node_id=destination_id,
            node_type="destination", 
            name=destination_name,
            metadata={
                "destination_type": metadata.get("destination_type", "ontology"),
                "ontology_class": metadata.get("ontology_class", ""),
                "storage_location": metadata.get("storage_location", "")
            },
            created_at=datetime.now(),
            created_by=created_by
        )
        
        self.nodes[destination_id] = node
        self.lineage_graph.add_node(destination_id, **asdict(node))
        
        # 변환과 연결
        self.add_lineage_edge(source_transformation, destination_id, "load",
                            {"destination": destination_id}, created_by)
        
        audit_logger.info(f"데이터 목적지 추가: {destination_name}")
        return node
    
    def add_lineage_edge(self, source_id: str, target_id: str, transformation_type: str,
                        metadata: Dict, created_by: str) -> DataLineageEdge:
        """
        리니지 그래프에 엣지 추가
        """
        edge = DataLineageEdge(
            source_node=source_id,
            target_node=target_id,
            transformation_type=transformation_type,
            metadata=metadata,
            created_at=datetime.now(),
            created_by=created_by
        )
        
        self.edges.append(edge)
        self.lineage_graph.add_edge(source_id, target_id, **asdict(edge))
        
        return edge
    
    def get_upstream_lineage(self, node_id: str, depth: int = None) -> List[str]:
        """
        특정 노드의 업스트림 데이터 리니지를 추적
        """
        if node_id not in self.lineage_graph:
            return []
        
        upstream_nodes = []
        visited = set()
        
        def dfs_upstream(current_node, current_depth):
            if depth is not None and current_depth >= depth:
                return
            if current_node in visited:
                return
            
            visited.add(current_node)
            predecessors = list(self.lineage_graph.predecessors(current_node))
            upstream_nodes.extend(predecessors)
            
            for pred in predecessors:
                dfs_upstream(pred, current_depth + 1)
        
        dfs_upstream(node_id, 0)
        return upstream_nodes
    
    def get_downstream_lineage(self, node_id: str, depth: int = None) -> List[str]:
        """
        특정 노드의 다운스트림 데이터 리니지를 추적
        """
        if node_id not in self.lineage_graph:
            return []
        
        downstream_nodes = []
        visited = set()
        
        def dfs_downstream(current_node, current_depth):
            if depth is not None and current_depth >= depth:
                return
            if current_node in visited:
                return
            
            visited.add(current_node)
            successors = list(self.lineage_graph.successors(current_node))
            downstream_nodes.extend(successors)
            
            for succ in successors:
                dfs_downstream(succ, current_depth + 1)
        
        dfs_downstream(node_id, 0)
        return downstream_nodes
    
    def get_data_impact_analysis(self, node_id: str) -> Dict:
        """
        특정 데이터 변경이 미치는 영향을 분석
        """
        downstream = self.get_downstream_lineage(node_id)
        
        impact_summary = {
            "affected_nodes": len(downstream),
            "affected_sources": [],
            "affected_transformations": [],
            "affected_destinations": []
        }
        
        for node in downstream:
            node_info = self.nodes.get(node)
            if node_info:
                if node_info.node_type == "source":
                    impact_summary["affected_sources"].append(node)
                elif node_info.node_type == "transformation":
                    impact_summary["affected_transformations"].append(node)
                elif node_info.node_type == "destination":
                    impact_summary["affected_destinations"].append(node)
        
        audit_logger.info(f"영향 분석 완료: {node_id} -> {impact_summary['affected_nodes']}개 노드 영향")
        return impact_summary
    
    def export_lineage_graph(self, format: str = "json") -> str:
        """
        리니지 그래프를 다양한 형식으로 내보내기
        """
        if format == "json":
            graph_data = {
                "nodes": [asdict(node) for node in self.nodes.values()],
                "edges": [asdict(edge) for edge in self.edges]
            }
            return json.dumps(graph_data, indent=2, default=str)
        
        elif format == "graphml":
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
                nx.write_graphml(self.lineage_graph, f.name)
                return f.name
        
        else:
            raise ValueError(f"지원하지 않는 형식: {format}")
    
    def search_lineage(self, query: str, search_type: str = "name") -> List[str]:
        """
        리니지 그래프에서 노드 검색
        """
        results = []
        
        for node_id, node in self.nodes.items():
            if search_type == "name" and query.lower() in node.name.lower():
                results.append(node_id)
            elif search_type == "type" and query.lower() == node.node_type.lower():
                results.append(node_id)
            elif search_type == "metadata":
                if any(query.lower() in str(v).lower() for v in node.metadata.values()):
                    results.append(node_id)
        
        return results

# 전역 데이터 리니지 추적기 인스턴스
data_lineage_tracker = DataLineageTracker()
