# Project Odysseus SDK
__version__ = "1.0.0"
__author__ = "Project Odysseus Team"
__email__ = "odysseus@example.com"
__description__ = "Palantir-style Ontology Infrastructure Library"

from .connectors.base import BaseConnector
from .connectors.implementations import FileConnector, DatabaseConnector
from .ontology.models import OntologyModel, ODS
from .ontology.advanced_models import AdvancedOntologyModel
from .ontology.engine import MappingEngine
from .governance.access_control import AccessControlManager, check_permission, check_advanced_permission
from .governance.data_lineage import DataLineageTracker
from .governance.privacy_tools import PrivacyEnhancingTools
from .governance.logger import audit_logger
from .applications.sdk import OntologySDK
from .applications.workshop import WorkshopApp

# 편의를 위한 주요 클래스들을 최상위에서 바로 import 가능하도록 설정
__all__ = [
    # Core Classes
    "OntologyModel",
    "AdvancedOntologyModel", 
    "MappingEngine",
    "OntologySDK",
    
    # Data Connectors
    "BaseConnector",
    "FileConnector",
    "DatabaseConnector",
    
    # Governance
    "AccessControlManager",
    "DataLineageTracker",
    "PrivacyEnhancingTools",
    "audit_logger",
    
    # Applications
    "WorkshopApp",
    
    # Decorators
    "check_permission",
    "check_advanced_permission",
    
    # Constants
    "ODS",
]
