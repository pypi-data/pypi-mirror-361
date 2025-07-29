# project_odysseus/cli.py
"""
Project Odysseus Command Line Interface
"""

import argparse
import sys
import os
from typing import Optional

def create_project(name: str, template: str = "basic") -> None:
    """새로운 Odysseus 프로젝트를 생성합니다."""
    from .templates import ProjectTemplate
    
    print(f"🏛️ Creating new Odysseus project: {name}")
    template_manager = ProjectTemplate()
    template_manager.create_project(name, template)
    print(f"✅ Project '{name}' created successfully!")

def run_demo(demo_type: str = "supply_chain") -> None:
    """데모 시나리오를 실행합니다."""
    if demo_type == "supply_chain":
        from .enhanced_main import main as demo_main
        print("🚀 Running supply chain optimization demo...")
        demo_main()
    elif demo_type == "knowledge":
        from .knoledge_system import KnowledgeSystem
        print("🧠 Running knowledge system demo...")
        ks = KnowledgeSystem()
        ks.run_knowledge_cycle("artificial intelligence machine learning")
    else:
        print(f"❌ Unknown demo type: {demo_type}")

def start_dashboard(port: int = 8501) -> None:
    """Streamlit 대시보드를 시작합니다."""
    import subprocess
    import sys
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "applications", "workshop_app.py")
    
    print(f"🌐 Starting Odysseus dashboard on port {port}...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path, "--server.port", str(port)
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")

def validate_ontology(file_path: str) -> None:
    """온톨로지 파일을 검증합니다."""
    from .ontology.models import OntologyModel
    from rdflib import Graph
    
    print(f"🔍 Validating ontology: {file_path}")
    
    try:
        g = Graph()
        g.parse(file_path)
        print(f"✅ Ontology is valid! Found {len(g)} triples.")
        
        # 기본 통계 정보
        classes = set()
        properties = set()
        
        for s, p, o in g:
            if "Class" in str(p):
                classes.add(str(s))
            elif "Property" in str(p):
                properties.add(str(s))
        
        print(f"📊 Statistics:")
        print(f"   - Classes: {len(classes)}")
        print(f"   - Properties: {len(properties)}")
        print(f"   - Triples: {len(g)}")
        
    except Exception as e:
        print(f"❌ Ontology validation failed: {e}")

def generate_docs(output_dir: str = "docs") -> None:
    """프로젝트 문서를 생성합니다."""
    print(f"📚 Generating documentation in {output_dir}...")
    
    # 간단한 문서 생성기
    os.makedirs(output_dir, exist_ok=True)
    
    # API 참조 생성
    api_docs = """# Project Odysseus API Reference

## Core Classes

### OntologyModel
Base ontology model for knowledge graph management.

### AdvancedOntologyModel  
Extended ontology model with inference and temporal data support.

### MappingEngine
Engine for mapping data sources to ontology objects.

### OntologySDK
Programming SDK for ontology interaction.

## Governance Classes

### AccessControlManager
Advanced access control with RBAC/PBAC support.

### DataLineageTracker
Data lineage tracking and impact analysis.

### PrivacyEnhancingTools
Privacy protection tools including masking and anonymization.

## Connectors

### FileConnector
Connector for file-based data sources (CSV, JSON, etc.).

### DatabaseConnector
Connector for database systems (SQLite, PostgreSQL, etc.).

## For detailed documentation, visit: https://odysseus.readthedocs.io
"""
    
    with open(os.path.join(output_dir, "api_reference.md"), "w", encoding="utf-8") as f:
        f.write(api_docs)
    
    print(f"✅ Documentation generated in {output_dir}/")

def main():
    """메인 CLI 진입점"""
    parser = argparse.ArgumentParser(
        description="🏛️ Project Odysseus - Palantir-style Ontology Infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  odysseus create myproject --template basic
  odysseus demo supply_chain
  odysseus dashboard --port 8080
  odysseus validate knowledge_graph.ttl
  odysseus docs --output docs/
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new Odysseus project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--template", default="basic", 
                              choices=["basic", "advanced", "enterprise"],
                              help="Project template")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demo scenarios")
    demo_parser.add_argument("type", nargs="?", default="supply_chain",
                            choices=["supply_chain", "knowledge"],
                            help="Demo type to run")
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start web dashboard")
    dashboard_parser.add_argument("--port", type=int, default=8501,
                                 help="Port number for dashboard")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate ontology file")
    validate_parser.add_argument("file", help="Ontology file path (.ttl, .rdf, .owl)")
    
    # Docs command
    docs_parser = subparsers.add_parser("docs", help="Generate documentation")
    docs_parser.add_argument("--output", default="docs", help="Output directory")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "create":
            create_project(args.name, args.template)
        elif args.command == "demo":
            run_demo(args.type)
        elif args.command == "dashboard":
            start_dashboard(args.port)
        elif args.command == "validate":
            validate_ontology(args.file)
        elif args.command == "docs":
            generate_docs(args.output)
        elif args.command == "version":
            from . import __version__
            print(f"Project Odysseus v{__version__}")
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
