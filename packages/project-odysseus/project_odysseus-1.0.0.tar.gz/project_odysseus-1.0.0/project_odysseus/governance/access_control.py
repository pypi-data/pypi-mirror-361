# project_odysseus/governance/access_control.py
from functools import wraps
from .logger import audit_logger

# 확장된 사용자 및 역할 데이터베이스 (실제 환경에서는 데이터베이스나 외부 인증 시스템 연동)
USERS_DB = {
    "supply_chain_manager": {
        "role": "manager",
        "permissions": ["read", "write", "delete", "execute_actions"],
        "data_access": ["supply_chain", "logistics", "inventory"],
        "department": "operations"
    },
    "analyst": {
        "role": "viewer", 
        "permissions": ["read"],
        "data_access": ["supply_chain", "analytics"],
        "department": "analytics"
    },
    "hr_manager": {
        "role": "manager",
        "permissions": ["read", "write"],
        "data_access": ["hr", "employee_data"],
        "department": "hr"
    },
    "data_scientist": {
        "role": "advanced_user",
        "permissions": ["read", "write", "model_training"],
        "data_access": ["analytics", "ml_models", "supply_chain"],
        "department": "data_science"
    }
}

# 데이터 분류 및 민감도 레벨
DATA_CLASSIFICATION = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3
}

class AccessControlManager:
    """
    고급 접근 제어 관리자 - RBAC, PBAC, 데이터 분류 기반 접근 제어
    """
    
    def __init__(self):
        self.users_db = USERS_DB
        self.data_classification = DATA_CLASSIFICATION
    
    def check_data_access(self, user: str, data_domain: str, operation: str = "read"):
        """
        사용자의 데이터 도메인별 접근 권한 확인
        """
        user_info = self.users_db.get(user, {})
        
        # 사용자 존재 여부 확인
        if not user_info:
            audit_logger.warning(f"알 수 없는 사용자 '{user}'의 접근 시도")
            return False
        
        # 데이터 도메인 접근 권한 확인
        if data_domain not in user_info.get("data_access", []):
            audit_logger.warning(f"사용자 '{user}'가 허용되지 않은 데이터 도메인 '{data_domain}'에 접근 시도")
            return False
        
        # 작업 권한 확인
        if operation not in user_info.get("permissions", []):
            audit_logger.warning(f"사용자 '{user}'가 허용되지 않은 작업 '{operation}' 시도")
            return False
        
        audit_logger.info(f"데이터 접근 승인: 사용자 '{user}' -> 도메인 '{data_domain}' -> 작업 '{operation}'")
        return True
    
    def check_data_classification_access(self, user: str, classification_level: str):
        """
        데이터 분류 레벨 기반 접근 제어
        """
        user_info = self.users_db.get(user, {})
        user_role = user_info.get("role", "")
        
        # 역할별 최대 접근 가능 분류 레벨 설정
        role_max_classification = {
            "viewer": "internal",
            "manager": "confidential", 
            "advanced_user": "confidential",
            "admin": "restricted"
        }
        
        max_level = role_max_classification.get(user_role, "public")
        user_max_level = self.data_classification.get(max_level, 0)
        requested_level = self.data_classification.get(classification_level, 0)
        
        if requested_level <= user_max_level:
            audit_logger.info(f"분류 레벨 접근 승인: 사용자 '{user}' -> 레벨 '{classification_level}'")
            return True
        else:
            audit_logger.warning(f"분류 레벨 접근 거부: 사용자 '{user}' -> 레벨 '{classification_level}' (최대 허용: {max_level})")
            return False

# 전역 접근 제어 관리자 인스턴스
access_control_manager = AccessControlManager()

def check_advanced_permission(required_role: str = None, data_domain: str = None, 
                            operation: str = "read", classification: str = "internal"):
    """
    고급 권한 확인 데코레이터 - 역할, 데이터 도메인, 작업 유형, 분류 레벨을 모두 고려
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 사용자 정보 추출
            user = kwargs.get('user')
            if not user and args:
                if hasattr(args[0], 'user'):
                    user = args[0].user
            
            if not user:
                audit_logger.error(f"사용자 정보 없이 '{func.__name__}' 함수 호출 시도")
                raise PermissionError("사용자 인증이 필요합니다.")
            
            # 다층 권한 검사
            checks_passed = []
            
            # 1. 기본 역할 확인
            if required_role:
                user_role = USERS_DB.get(user, {}).get("role")
                role_hierarchy = {
                    "viewer": 1,
                    "advanced_user": 2, 
                    "manager": 3,
                    "admin": 4
                }
                
                user_level = role_hierarchy.get(user_role, 0)
                required_level = role_hierarchy.get(required_role, 0)
                
                if user_level >= required_level:
                    checks_passed.append("role")
                else:
                    audit_logger.warning(f"역할 권한 부족: 사용자 '{user}'({user_role}) -> 필요 역할 '{required_role}'")
                    raise PermissionError(f"'{required_role}' 이상의 역할이 필요합니다.")
            
            # 2. 데이터 도메인 접근 확인
            if data_domain:
                if access_control_manager.check_data_access(user, data_domain, operation):
                    checks_passed.append("data_domain")
                else:
                    raise PermissionError(f"'{data_domain}' 도메인에 대한 '{operation}' 권한이 없습니다.")
            
            # 3. 데이터 분류 레벨 확인
            if classification:
                if access_control_manager.check_data_classification_access(user, classification):
                    checks_passed.append("classification")
                else:
                    raise PermissionError(f"'{classification}' 분류 레벨에 대한 접근 권한이 없습니다.")
            
            audit_logger.info(f"종합 권한 검사 통과: 사용자 '{user}' -> 함수 '{func.__name__}' (통과한 검사: {checks_passed})")
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# 기존 코드와의 호환성을 위한 단순 권한 확인 함수
def check_permission(required_role: str):
    """
    간단한 권한 확인 데코레이터 (하위 호환성)
    """
    return check_advanced_permission(required_role=required_role, operation='read')

print("✅ AccessControlManager(데코레이터) 설정 완료.")
