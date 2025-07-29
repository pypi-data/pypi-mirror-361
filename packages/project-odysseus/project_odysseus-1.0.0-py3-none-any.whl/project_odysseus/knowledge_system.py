# project_odysseus/knowledge_system.py
import os
import pickle
import re
import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
from ddgs import DDGS

# 1. 검색 및 스크레이핑 모듈
def search_all_engines(query: str, num_results: int = 1000) -> list[str]:
    """여러 검색 엔진을 통해 검색 결과를 얻어와 URL 리스트를 반환합니다."""
    print(f"🔍 '{query}'에 대한 다중 엔진 검색 중...")
    urls = set()
    try:
        # DuckDuckGo API 사용
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                urls.add(r['href'])
        
        # (여기에 Google, Bing 등 다른 검색 엔진 API 클라이언트 추가 가능)

    except Exception as e:
        print(f"Error during search: {e}")
        
    print(f"    -> {len(urls)}개의 고유 URL 발견.")
    return list(urls)

def scrape_url_content(url: str) -> str:
    """단일 URL의 텍스트 콘텐츠를 스크레이핑합니다."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # HTTP 오류 시 예외 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 방해 요소(네비게이션 바, 푸터 등) 제거
        for element in soup(['nav', 'footer', 'header', 'script', 'style']):
            element.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        return re.sub(r'\s+', ' ', text) # 여러 공백을 하나로 축소
    except requests.RequestException as e:
        print(f"    ❗️ URL 스크레이핑 실패: {url} ({e})")
        return ""

# 2. 지식 추출 및 그래프 처리 모듈
class KnowledgeSystem:
    def __init__(self, graph_file_path="knowledge_graph.pkl"):
        self.graph_file_path = graph_file_path
        self.nlp = spacy.load("en_core_web_sm") # 영어 모델 로드
        self.graph = self._load_graph()

    def _load_graph(self) -> nx.DiGraph:
        """로컬 파일에서 지식 그래프를 로드하거나 새로 생성합니다."""
        if os.path.exists(self.graph_file_path):
            print(f"💾 기존 지식 그래프 로드 중: '{self.graph_file_path}'")
            with open(self.graph_file_path, 'rb') as f:
                return pickle.load(f)
        else:
            print("✨ 새로운 지식 그래프 생성.")
            return nx.DiGraph()

    def _save_graph(self):
        """지식 그래프를 로컬 파일에 저장합니다."""
        print(f"💾 지식 그래프 저장 중: '{self.graph_file_path}'")
        with open(self.graph_file_path, 'wb') as f:
            pickle.dump(self.graph, f)

    def extract_knowledge_from_text(self, text: str, source_url: str) -> nx.DiGraph:
        """텍스트에서 개체와 관계를 추출하여 임시 지식 그래프를 생성합니다."""
        doc = self.nlp(text)
        temp_graph = nx.DiGraph()
        
        # (PERSON) --[VERB]--> (ORG) 같은 단순 관계 추출
        for token in doc:
            if token.pos_ == "VERB":
                subject, obj = None, None
                for child in token.children:
                    if child.dep_ == "nsubj" and child.ent_type_: # 주어
                        subject = child.text
                    if child.dep_ == "dobj" and child.ent_type_: # 목적어
                        obj = child.text
                
                if subject and obj:
                    temp_graph.add_node(subject, type=doc.ents[0].label_ if doc.ents else 'UNKNOWN')
                    temp_graph.add_node(obj, type=doc.ents[0].label_ if doc.ents else 'UNKNOWN')
                    temp_graph.add_edge(subject, obj, label=token.lemma_, source=source_url)
        return temp_graph

    def merge_and_resolve(self, new_graph: nx.DiGraph):
        """신규 그래프를 기존 그래프와 병합하고 충돌을 해결합니다."""
        conflicts = []
        for u, v, data in new_graph.edges(data=True):
            # u(주어)와 data['label'](관계)이 동일한데 v(목적어)가 다른 경우 충돌로 간주
            if self.graph.has_node(u):
                for _, existing_v, existing_data in self.graph.out_edges(u, data=True):
                    if existing_data['label'] == data['label'] and existing_v != v:
                        conflict = {
                            "node": u,
                            "relation": data['label'],
                            "old_value": existing_v,
                            "new_value": v,
                            "new_source": data['source']
                        }
                        conflicts.append(conflict)
                        print(f"💥 충돌 발견: {u} -> {data['label']} -> {existing_v} vs {v}")
        
        # 충돌 해결 로직
        for conflict in conflicts:
            self._resolve_conflict(conflict)
            
        # 충돌 해결 후 최종 병합
        self.graph.add_nodes_from(new_graph.nodes(data=True))
        self.graph.add_edges_from(new_graph.edges(data=True))

    def _resolve_conflict(self, conflict: dict):
        """특정 충돌에 대해 재검색을 통해 정보를 업데이트합니다."""
        node, rel = conflict['node'], conflict['relation']
        val1, val2 = conflict['old_value'], conflict['new_value']
        
        # 매우 구체적인 쿼리 생성
        resolution_query = f'"{node}" {rel} "{val1}" or "{val2}"'
        print(f"⚔️ 충돌 해결 시작: '{resolution_query}'")
        
        urls = search_all_engines(resolution_query, num_results=3)
        resolution_text = " ".join([scrape_url_content(url) for url in urls])
        
        # 재검색한 텍스트에서 어느 쪽이 더 많이 언급되는지 확인
        count1 = resolution_text.lower().count(val1.lower())
        count2 = resolution_text.lower().count(val2.lower())

        if count1 > count2:
            print(f"    -> 해결: 기존 정보 '{val1}' 유지.")
            # 기존 정보 유지, 아무것도 안 함
        elif count2 > count1:
            print(f"    -> 해결: 새로운 정보 '{val2}'로 업데이트.")
            # 기존의 잘못된 엣지 제거
            if self.graph.has_edge(node, val1):
                self.graph.remove_edge(node, val1)
            # 새로운 엣지 추가 (병합 시 자동으로 됨)
        else:
            print("    -> 해결 실패: 정보 부족으로 현 상태 유지.")

    def answer_from_graph(self, query: str) -> str:
        """그래프에서 쿼리 주제와 관련된 정보를 종합하여 답변합니다."""
        # 쿼리에서 핵심 개체 찾기
        doc = self.nlp(query)
        subjects = [ent.text for ent in doc.ents]
        if not subjects:
            subjects = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]
        
        if not subjects:
            return "질문에서 핵심 주제를 찾을 수 없습니다."

        main_subject = subjects[0]
        if not self.graph.has_node(main_subject):
            return f"'{main_subject}'에 대한 지식이 아직 없습니다."

        print(f"📖 지식 그래프 기반 답변 생성 (주제: {main_subject})")
        info = [f"'{main_subject}'에 대한 종합 정보:"]
        for u, v, data in self.graph.out_edges(main_subject, data=True):
            info.append(f" - {u} --[{data['label']}]--> {v}")
        for u, v, data in self.graph.in_edges(main_subject, data=True):
            info.append(f" - {u} --[{data['label']}]--> {v}")
            
        return "\n".join(info)

    def run_knowledge_cycle(self, query: str):
        """사용자 쿼리에 대한 전체 지식 처리 사이클을 실행합니다."""
        # 1. 검색 및 스크레이핑
        urls = search_all_engines(query)
        scraped_contents = [scrape_url_content(url) for url in urls]
        
        # 2. 신규 지식 추출
        print("\n🌀 신규 지식 추출 및 병합 시작...")
        combined_new_graph = nx.DiGraph()
        for i, text in enumerate(scraped_contents):
            if text:
                source_url = urls[i]
                temp_graph = self.extract_knowledge_from_text(text, source_url)
                combined_new_graph.add_nodes_from(temp_graph.nodes(data=True))
                combined_new_graph.add_edges_from(temp_graph.edges(data=True))
        
        # 3. 병합 및 충돌 해결
        self.merge_and_resolve(combined_new_graph)
        
        # 4. 저장
        self._save_graph()
        
        # 5. 답변
        print("\n" + "="*50)
        answer = self.answer_from_graph(query)
        print(answer)
        print("="*50 + "\n")


# 3. 메인 실행 로직
if __name__ == "__main__":
    ks = KnowledgeSystem()
    
    # 예시: 'Apple Inc'에 대한 정보를 검색하고 지식 그래프를 구축/업데이트
    # 처음 실행하면 그래프가 생성되고, 두 번째 실행하면 기존 그래프와 병합/충돌 해결을 시도합니다.
    try:
        ks.run_knowledge_cycle("Apple Inc. history founders")
    except Exception as e:
        print(f"An error occurred during the cycle: {e}")
