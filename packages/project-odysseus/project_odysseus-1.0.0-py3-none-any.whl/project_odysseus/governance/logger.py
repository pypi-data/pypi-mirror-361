# project_odysseus/governance/logger.py
import logging

def setup_audit_logger():
    """
    모든 데이터 접근 및 수정 기록을 남기는 감사 로거를 설정합니다.
    """
    logger = logging.getLogger('AuditLogger')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('audit_trail.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    print("✅ AuditLogger 설정 완료. 모든 활동은 'audit_trail.log'에 기록됩니다.")
    return logger

# 싱글톤처럼 사용하기 위해 모듈 레벨에서 로거 생성
audit_logger = setup_audit_logger()
