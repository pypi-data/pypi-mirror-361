# project_odysseus/applications/workshop_app.py
# 이 파일은 'streamlit run workshop_app.py' 명령으로 실행해야 합니다.
# main.py에서 생성된 knowledge_graph.ttl 파일을 읽어 시각화하는 예제입니다.

import streamlit as st
from rdflib import Graph
import pandas as pd

def run_workshop():
    st.set_page_config(layout="wide")
    st.title("🏛️ 프로젝트 오디세우스 - 워크샵 대시보드")

    try:
        # main.py에서 생성한 지식 그래프 파일을 로드
        g = Graph()
        g.parse("knowledge_graph.ttl", format="turtle")
        st.success("knowledge_graph.ttl 파일을 성공적으로 로드했습니다.")
    except FileNotFoundError:
        st.error("knowledge_graph.ttl 파일을 찾을 수 없습니다. 먼저 main.py를 실행해주세요.")
        return

    st.header("📊 온톨로지 데이터 조회")

    # SPARQL 쿼리를 입력받아 실행하는 인터페이스
    default_query = """
PREFIX ods: <http://project-odysseus.com/ontology#>
SELECT ?truckId ?driverName ?currentLocation
WHERE {
    ?truck a ods:Truck .
    ?truck ods:truckId ?truckId .
    ?truck ods:driverName ?driverName .
    ?truck ods:currentLocation ?currentLocation .
}
    """
    sparql_query = st.text_area("SPARQL 쿼리:", value=default_query, height=200)

    if st.button("쿼리 실행"):
        try:
            results = g.query(sparql_query)
            data = [
                {str(col): str(row[col]) for col in results.vars}
                for row in results
            ]
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.warning("쿼리 결과가 없습니다.")
        except Exception as e:
            st.error(f"쿼리 실행 중 오류 발생: {e}")

# 이 파일이 직접 실행될 때만 Streamlit 앱을 실행
if __name__ == "__main__":
    run_workshop()
