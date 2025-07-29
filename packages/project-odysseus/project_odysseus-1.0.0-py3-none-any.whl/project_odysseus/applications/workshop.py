# project_odysseus/applications/workshop.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdflib import Graph
from ontology.advanced_models import AdvancedOntologyModel
from governance.access_control import check_advanced_permission
from governance.data_lineage import data_lineage_tracker
from governance.privacy_tools import privacy_tools
from governance.logger import audit_logger

class WidgetFactory:
    """
    재사용 가능한 UI 위젯 컴포넌트 팩토리
    """
    
    @staticmethod
    def create_data_table(data: pd.DataFrame, title: str = "Data Table",
                         selectable: bool = True, 
                         privacy_config: Optional[Dict] = None) -> Dict:
        """
        데이터 테이블 위젯 생성
        """
        st.subheader(title)
        
        # 프라이버시 설정 적용
        if privacy_config:
            data = privacy_tools.apply_privacy_policy(data, privacy_config)
        
        # 필터링 옵션
        if len(data.columns) > 0:
            filter_col = st.selectbox(f"Filter by column ({title})", 
                                    ["None"] + list(data.columns))
            if filter_col != "None":
                unique_values = data[filter_col].unique()
                selected_values = st.multiselect(f"Select {filter_col} values",
                                                unique_values, default=unique_values)
                data = data[data[filter_col].isin(selected_values)]
        
        # 테이블 표시
        if selectable:
            selected_rows = st.dataframe(data, use_container_width=True, 
                                       on_select="rerun", selection_mode="multi-row")
            return {"data": data, "selected_rows": selected_rows}
        else:
            st.dataframe(data, use_container_width=True)
            return {"data": data}
    
    @staticmethod
    def create_chart(data: pd.DataFrame, chart_type: str, title: str,
                    x_col: str, y_col: str, color_col: Optional[str] = None) -> go.Figure:
        """
        차트 위젯 생성
        """
        st.subheader(title)
        
        if chart_type == "line":
            fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "bar":
            fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "scatter":
            fig = px.scatter(data, x=x_col, y=y_col, color=color_col, title=title)
        elif chart_type == "pie":
            fig = px.pie(data, names=x_col, values=y_col, title=title)
        else:
            st.error(f"Unsupported chart type: {chart_type}")
            return None
        
        st.plotly_chart(fig, use_container_width=True)
        return fig
    
    @staticmethod
    def create_metric_cards(metrics: Dict[str, Any]) -> None:
        """
        메트릭 카드 위젯 생성
        """
        cols = st.columns(len(metrics))
        
        for i, (metric_name, metric_data) in enumerate(metrics.items()):
            with cols[i]:
                if isinstance(metric_data, dict):
                    value = metric_data.get("value", 0)
                    delta = metric_data.get("delta", None)
                    st.metric(metric_name, value, delta)
                else:
                    st.metric(metric_name, metric_data)
    
    @staticmethod
    def create_action_button(action_name: str, action_config: Dict, 
                           ontology_model: AdvancedOntologyModel) -> bool:
        """
        액션 버튼 위젯 생성
        """
        if st.button(action_name, key=f"action_{action_name}"):
            # 액션 실행
            ActionConfigurator.execute_action(action_config, ontology_model)
            return True
        return False

class ActionConfigurator:
    """
    온톨로지 액션 설정 및 실행 관리자
    """
    
    @staticmethod
    def execute_action(action_config: Dict, ontology_model: AdvancedOntologyModel) -> Dict:
        """
        액션 실행
        """
        action_type = action_config.get("type", "")
        action_params = action_config.get("parameters", {})
        
        try:
            if action_type == "create_object":
                return ActionConfigurator._create_object(action_params, ontology_model)
            elif action_type == "update_object":
                return ActionConfigurator._update_object(action_params, ontology_model)
            elif action_type == "delete_object":
                return ActionConfigurator._delete_object(action_params, ontology_model)
            elif action_type == "sparql_query":
                return ActionConfigurator._execute_sparql(action_params, ontology_model)
            elif action_type == "api_call":
                return ActionConfigurator._make_api_call(action_params)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
        
        except Exception as e:
            audit_logger.error(f"액션 실행 실패: {action_type} - {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _create_object(params: Dict, ontology_model: AdvancedOntologyModel) -> Dict:
        """
        온톨로지 객체 생성
        """
        object_id = params.get("object_id")
        class_name = params.get("class_name")
        properties = params.get("properties", {})
        
        # 제약 조건 검증
        validation_result = ontology_model.validate_constraints(object_id, properties)
        if not validation_result["valid"]:
            return {"success": False, "error": "Constraint validation failed", 
                   "violations": validation_result["violations"]}
        
        # 객체 생성
        ontology_model.add_object(object_id, class_name, properties)
        
        # 데이터 리니지 추적
        data_lineage_tracker.add_destination(
            object_id, f"{class_name} object", "workshop_action",
            {"action_type": "create_object", "class": class_name},
            "workshop_user"
        )
        
        audit_logger.info(f"객체 생성: {object_id} ({class_name})")
        return {"success": True, "object_id": object_id}
    
    @staticmethod
    def _update_object(params: Dict, ontology_model: AdvancedOntologyModel) -> Dict:
        """
        온톨로지 객체 업데이트
        """
        object_id = params.get("object_id")
        properties = params.get("properties", {})
        
        # 기존 객체 존재 확인
        existing_values = ontology_model.get_property_values(object_id, "rdf:type")
        if not existing_values:
            return {"success": False, "error": f"Object {object_id} not found"}
        
        # 속성 업데이트 (기존 속성 제거 후 새로 추가)
        for prop_name, value in properties.items():
            # 시계열 속성인 경우 시간 정보 포함
            if params.get("is_temporal", False):
                ontology_model.add_temporal_property(
                    object_id, prop_name, value, datetime.now()
                )
            else:
                # 기존 속성 제거 후 새로 추가 로직 필요
                pass
        
        audit_logger.info(f"객체 업데이트: {object_id}")
        return {"success": True, "object_id": object_id}
    
    @staticmethod
    def _delete_object(params: Dict, ontology_model: AdvancedOntologyModel) -> Dict:
        """
        온톨로지 객체 삭제
        """
        object_id = params.get("object_id")
        
        # 영향 분석
        impact_analysis = data_lineage_tracker.get_data_impact_analysis(object_id)
        
        # 삭제 실행 (실제 구현에서는 그래프에서 관련 트리플 제거)
        # 현재는 로그만 남김
        audit_logger.warning(f"객체 삭제: {object_id} (영향받는 노드: {impact_analysis['affected_nodes']}개)")
        
        return {"success": True, "object_id": object_id, "impact": impact_analysis}
    
    @staticmethod
    def _execute_sparql(params: Dict, ontology_model: AdvancedOntologyModel) -> Dict:
        """
        SPARQL 쿼리 실행
        """
        query = params.get("query", "")
        
        try:
            results = ontology_model.graph.query(query)
            result_data = []
            
            for result in results:
                row = {}
                for var in results.vars:
                    row[str(var)] = str(result[var])
                result_data.append(row)
            
            return {"success": True, "results": result_data, "count": len(result_data)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _make_api_call(params: Dict) -> Dict:
        """
        외부 API 호출
        """
        import requests
        
        url = params.get("url", "")
        method = params.get("method", "GET")
        headers = params.get("headers", {})
        data = params.get("data", {})
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                return {"success": False, "error": f"Unsupported HTTP method: {method}"}
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.content else {}
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}

class WorkshopApp:
    """
    메인 워크샵 애플리케이션
    """
    
    def __init__(self, ontology_model: AdvancedOntologyModel):
        self.ontology_model = ontology_model
        self.widget_factory = WidgetFactory()
        self.action_configurator = ActionConfigurator()
    
    def run(self):
        """
        워크샵 앱 실행
        """
        st.set_page_config(
            page_title="Project Odysseus Workshop",
            page_icon="🏛️",
            layout="wide"
        )
        
        st.title("🏛️ Project Odysseus - Advanced Workshop")
        
        # 사이드바 네비게이션
        page = st.sidebar.selectbox(
            "Navigate",
            ["Dashboard", "Data Explorer", "Ontology Browser", "Actions", "Analytics"]
        )
        
        if page == "Dashboard":
            self._render_dashboard()
        elif page == "Data Explorer":
            self._render_data_explorer()
        elif page == "Ontology Browser":
            self._render_ontology_browser()
        elif page == "Actions":
            self._render_actions()
        elif page == "Analytics":
            self._render_analytics()
    
    def _render_dashboard(self):
        """
        대시보드 페이지 렌더링
        """
        st.header("📊 Dashboard")
        
        # 메트릭 카드
        metrics = {
            "Total Objects": len(self.ontology_model.get_class_instances("Truck") + 
                                self.ontology_model.get_class_instances("Order")),
            "Active Rules": len(self.ontology_model.inference_rules),
            "Data Sources": len(data_lineage_tracker.nodes),
            "Privacy Policies": "Active"
        }
        
        self.widget_factory.create_metric_cards(metrics)
        
        # 최근 활동 로그
        st.subheader("🔍 Recent Activity")
        try:
            with open("audit_trail.log", "r", encoding="utf-8") as f:
                recent_logs = f.readlines()[-10:]  # 최근 10개 로그
            
            for log in recent_logs:
                st.text(log.strip())
        except FileNotFoundError:
            st.info("No audit logs found")
    
    def _render_data_explorer(self):
        """
        데이터 탐색 페이지 렌더링
        """
        st.header("🔍 Data Explorer")
        
        # SPARQL 쿼리 인터페이스
        st.subheader("SPARQL Query Interface")
        
        default_query = """
        PREFIX ods: <http://project-odysseus.com/ontology#>
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object .
        }
        LIMIT 100
        """
        
        query = st.text_area("SPARQL Query", value=default_query, height=150)
        
        if st.button("Execute Query"):
            action_config = {
                "type": "sparql_query",
                "parameters": {"query": query}
            }
            
            result = self.action_configurator.execute_action(action_config, self.ontology_model)
            
            if result["success"]:
                if result["results"]:
                    df = pd.DataFrame(result["results"])
                    st.success(f"Query executed successfully. {result['count']} results found.")
                    self.widget_factory.create_data_table(df, "Query Results")
                else:
                    st.info("Query executed successfully but returned no results.")
            else:
                st.error(f"Query failed: {result['error']}")
    
    def _render_ontology_browser(self):
        """
        온톨로지 브라우저 페이지 렌더링
        """
        st.header("🌐 Ontology Browser")
        
        # 온톨로지 스키마 표시
        schema = self.ontology_model.export_ontology_schema()
        
        # 클래스 계층 구조
        st.subheader("Class Hierarchy")
        if schema["class_hierarchy"]:
            for parent, children in schema["class_hierarchy"].items():
                st.write(f"**{parent}**")
                for child in children:
                    st.write(f"  └── {child}")
        else:
            st.info("No class hierarchy defined")
        
        # 클래스 및 속성 정보
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Classes")
            for class_name, class_info in schema["classes"].items():
                with st.expander(f"Class: {class_name}"):
                    st.write(f"Label: {class_info.get('label', 'N/A')}")
                    st.write(f"URI: {class_info.get('uri', 'N/A')}")
                    
                    # 인스턴스 수
                    instances = self.ontology_model.get_class_instances(class_name)
                    st.write(f"Instances: {len(instances)}")
        
        with col2:
            st.subheader("Properties")
            for prop_name, prop_info in schema["properties"].items():
                with st.expander(f"Property: {prop_name}"):
                    st.write(f"Domain: {prop_info.get('domain', 'N/A')}")
                    st.write(f"Range: {prop_info.get('range', 'N/A')}")
                    st.write(f"URI: {prop_info.get('uri', 'N/A')}")
                    
                    # 제약 조건
                    if prop_name in schema["property_constraints"]:
                        constraints = schema["property_constraints"][prop_name]
                        st.write("Constraints:")
                        for constraint_type, constraint_value in constraints.items():
                            st.write(f"  - {constraint_type}: {constraint_value}")
    
    def _render_actions(self):
        """
        액션 페이지 렌더링
        """
        st.header("⚡ Actions")
        
        action_type = st.selectbox(
            "Select Action Type",
            ["Create Object", "Update Object", "Delete Object", "Execute SPARQL", "API Call"]
        )
        
        if action_type == "Create Object":
            st.subheader("Create New Object")
            
            object_id = st.text_input("Object ID")
            class_name = st.selectbox("Class", ["Truck", "Order", "Driver", "Route"])
            
            # 속성 입력
            properties = {}
            if class_name == "Truck":
                properties["truckId"] = st.text_input("Truck ID")
                properties["driverName"] = st.text_input("Driver Name")
                properties["currentLocation"] = st.text_input("Current Location")
            elif class_name == "Order":
                properties["orderId"] = st.number_input("Order ID", min_value=1)
                properties["productName"] = st.text_input("Product Name")
                properties["quantity"] = st.number_input("Quantity", min_value=1)
            
            if st.button("Create Object"):
                action_config = {
                    "type": "create_object",
                    "parameters": {
                        "object_id": object_id,
                        "class_name": class_name,
                        "properties": properties
                    }
                }
                
                result = self.action_configurator.execute_action(action_config, self.ontology_model)
                
                if result["success"]:
                    st.success(f"Object {object_id} created successfully!")
                else:
                    st.error(f"Failed to create object: {result['error']}")
    
    def _render_analytics(self):
        """
        분석 페이지 렌더링
        """
        st.header("📈 Analytics")
        
        # 데이터 리니지 분석
        st.subheader("Data Lineage Analysis")
        
        if data_lineage_tracker.nodes:
            # 노드 통계
            node_stats = {
                "Source": len([n for n in data_lineage_tracker.nodes.values() if n.node_type == "source"]),
                "Transformation": len([n for n in data_lineage_tracker.nodes.values() if n.node_type == "transformation"]),
                "Destination": len([n for n in data_lineage_tracker.nodes.values() if n.node_type == "destination"])
            }
            
            # 파이 차트로 표시
            if sum(node_stats.values()) > 0:
                fig = px.pie(
                    values=list(node_stats.values()),
                    names=list(node_stats.keys()),
                    title="Data Lineage Node Distribution"
                )
                st.plotly_chart(fig)
        else:
            st.info("No data lineage information available")
        
        # 온톨로지 통계
        st.subheader("Ontology Statistics")
        
        truck_count = len(self.ontology_model.get_class_instances("Truck"))
        order_count = len(self.ontology_model.get_class_instances("Order"))
        
        if truck_count > 0 or order_count > 0:
            stats_df = pd.DataFrame({
                "Class": ["Truck", "Order"],
                "Count": [truck_count, order_count]
            })
            
            fig = px.bar(stats_df, x="Class", y="Count", title="Object Count by Class")
            st.plotly_chart(fig)

# 전역 워크샵 앱 인스턴스 생성 함수
def create_workshop_app(ontology_model: AdvancedOntologyModel) -> WorkshopApp:
    """
    워크샵 앱 인스턴스 생성
    """
    return WorkshopApp(ontology_model)
