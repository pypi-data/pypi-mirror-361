# project_odysseus/templates.py
"""
Project template generator for creating new Odysseus projects
"""

import os
import shutil
from typing import Dict, Any

class ProjectTemplate:
    """프로젝트 템플릿 생성기"""
    
    def __init__(self):
        self.templates = {
            "basic": self._create_basic_template,
            "advanced": self._create_advanced_template,
            "enterprise": self._create_enterprise_template
        }
    
    def create_project(self, name: str, template_type: str = "basic") -> None:
        """새로운 프로젝트를 생성합니다."""
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        # 프로젝트 디렉토리 생성
        project_dir = name
        os.makedirs(project_dir, exist_ok=True)
        
        # 템플릿 생성
        template_func = self.templates[template_type]
        template_func(project_dir, name)
        
        print(f"✅ Project '{name}' created with '{template_type}' template")
    
    def _create_basic_template(self, project_dir: str, name: str) -> None:
        """기본 템플릿 생성"""
        
        # main.py 파일 생성
        main_content = f'''#!/usr/bin/env python3
"""
{name} - Basic Odysseus Project
"""

from project_odysseus import (
    OntologyModel, 
    MappingEngine, 
    FileConnector,
    OntologySDK
)

def main():
    """메인 실행 함수"""
    print("🏛️ {name} - Odysseus Project Starting...")
    
    # 1. 온톨로지 모델 생성
    ontology = OntologyModel()
    
    # 2. 기본 클래스 및 속성 정의
    ontology.define_class("Entity", "Basic entity class")
    ontology.define_property("name", "Entity", "http://www.w3.org/2001/XMLSchema#string")
    
    # 3. 매핑 엔진 생성
    mapper = MappingEngine(ontology)
    
    # 4. SDK 초기화
    sdk = OntologySDK(ontology, user="admin")
    
    print("✅ Ontology system initialized successfully!")
    
    # 5. 지식 그래프 저장
    ontology.save("knowledge_graph.ttl")
    
    return ontology

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(main_content)
        
        # requirements.txt 생성
        requirements = """project-odysseus>=1.0.0
pandas>=1.5.0
"""
        
        with open(os.path.join(project_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(requirements)
        
        # README.md 생성
        readme = f"""# {name}

A basic Project Odysseus implementation.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Generated Files

- `knowledge_graph.ttl`: RDF knowledge graph
- `audit_trail.log`: Audit logs

## Next Steps

1. Add your data sources
2. Define your ontology schema
3. Implement data mappings
4. Build your dashboard

For more information, visit: https://odysseus.readthedocs.io
"""
        
        with open(os.path.join(project_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)
    
    def _create_advanced_template(self, project_dir: str, name: str) -> None:
        """고급 템플릿 생성"""
        
        # 기본 템플릿 먼저 생성
        self._create_basic_template(project_dir, name)
        
        # 고급 main.py로 교체
        advanced_main = f'''#!/usr/bin/env python3
"""
{name} - Advanced Odysseus Project
"""

from project_odysseus import (
    AdvancedOntologyModel,
    MappingEngine,
    FileConnector,
    DatabaseConnector,
    OntologySDK,
    AccessControlManager,
    DataLineageTracker,
    PrivacyEnhancingTools
)

def main():
    """고급 기능을 포함한 메인 실행 함수"""
    print("🏛️ {name} - Advanced Odysseus Project Starting...")
    
    # 1. 고급 온톨로지 모델 생성
    ontology = AdvancedOntologyModel()
    
    # 2. 클래스 계층 구조 정의
    ontology.define_class("Entity", "Base entity class")
    ontology.define_class("Person", "A human being")
    ontology.define_class_hierarchy("Person", "Entity")
    
    # 3. 속성 제약 조건 정의
    ontology.define_property_constraints("status", {{
        "allowed_values": ["active", "inactive", "pending"],
        "data_type": "string"
    }})
    
    # 4. 접근 제어 설정
    access_manager = AccessControlManager()
    
    # 5. 데이터 리니지 추적
    lineage_tracker = DataLineageTracker()
    
    # 6. 개인정보보호 도구
    privacy_tools = PrivacyEnhancingTools()
    
    # 7. SDK 초기화
    sdk = OntologySDK(ontology, user="admin")
    
    print("✅ Advanced ontology system initialized!")
    
    # 8. 스키마 내보내기
    schema = ontology.export_ontology_schema()
    with open("ontology_schema.json", "w", encoding="utf-8") as f:
        import json
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    # 9. 지식 그래프 저장
    ontology.save("knowledge_graph.ttl")
    
    return ontology

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(advanced_main)
        
        # config.py 생성
        config_content = f'''"""
{name} Configuration
"""

# 데이터베이스 설정
DATABASE_CONFIG = {{
    "host": "localhost",
    "port": 5432,
    "database": "{name.lower()}_db",
    "username": "odysseus",
    "password": "your_password"
}}

# 접근 제어 설정
ACCESS_CONTROL = {{
    "admin": {{
        "role": "admin",
        "permissions": ["read", "write", "delete", "admin"],
        "data_access": ["all"]
    }},
    "analyst": {{
        "role": "analyst", 
        "permissions": ["read"],
        "data_access": ["analytics", "reports"]
    }}
}}

# 개인정보보호 정책
PRIVACY_CONFIG = {{
    "email": {{
        "privacy_level": "mask",
        "mask_type": "email"
    }},
    "phone": {{
        "privacy_level": "anonymize",
        "method": "hash"
    }},
    "salary": {{
        "privacy_level": "differential_privacy",
        "epsilon": 1.0
    }}
}}
'''
        
        with open(os.path.join(project_dir, "config.py"), "w", encoding="utf-8") as f:
            f.write(config_content)
    
    def _create_enterprise_template(self, project_dir: str, name: str) -> None:
        """엔터프라이즈 템플릿 생성"""
        
        # 고급 템플릿 먼저 생성
        self._create_advanced_template(project_dir, name)
        
        # 디렉토리 구조 생성
        dirs_to_create = [
            "src",
            "tests", 
            "docs",
            "config",
            "scripts",
            "data"
        ]
        
        for dir_name in dirs_to_create:
            os.makedirs(os.path.join(project_dir, dir_name), exist_ok=True)
        
        # Docker 설정
        dockerfile = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "main.py"]
'''
        
        with open(os.path.join(project_dir, "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(dockerfile)
        
        # docker-compose.yml
        docker_compose = f'''version: '3.8'

services:
  {name.lower()}:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
    
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: {name.lower()}_db
      POSTGRES_USER: odysseus
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
'''
        
        with open(os.path.join(project_dir, "docker-compose.yml"), "w", encoding="utf-8") as f:
            f.write(docker_compose)
        
        # 테스트 파일
        test_content = f'''import unittest
from src.main import main

class Test{name.replace("-", "_").replace(" ", "_").title()}(unittest.TestCase):
    
    def test_ontology_creation(self):
        """온톨로지 생성 테스트"""
        ontology = main()
        self.assertIsNotNone(ontology)
        
    def test_basic_functionality(self):
        """기본 기능 테스트"""
        # 테스트 구현
        pass

if __name__ == "__main__":
    unittest.main()
'''
        
        with open(os.path.join(project_dir, "tests", "test_main.py"), "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # main.py를 src/로 이동
        shutil.move(
            os.path.join(project_dir, "main.py"),
            os.path.join(project_dir, "src", "main.py")
        )
        
        # 엔터프라이즈용 requirements.txt 업데이트
        enterprise_requirements = """project-odysseus[enterprise]>=1.0.0
pandas>=1.5.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
redis>=4.0.0
celery>=5.0.0
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
"""
        
        with open(os.path.join(project_dir, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(enterprise_requirements)
