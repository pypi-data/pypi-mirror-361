# project_odysseus/governance/privacy_tools.py
import hashlib
import random
import string
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .logger import audit_logger

class PrivacyEnhancingTools:
    """
    개인정보보호 강화 도구 모음
    """
    
    def __init__(self):
        self.masking_chars = "*"
        self.hash_salt = "odysseus_privacy_salt"
        audit_logger.info("PrivacyEnhancingTools 초기화 완료")
    
    def mask_data(self, data: Union[str, pd.Series], mask_type: str = "partial", 
                  preserve_chars: int = 2) -> Union[str, pd.Series]:
        """
        데이터 마스킹 - 민감한 정보를 부분적으로 숨김
        """
        def mask_string(s: str) -> str:
            if not s or len(s) <= preserve_chars:
                return s
            
            if mask_type == "partial":
                # 앞뒤 일부 문자만 보여주고 나머지는 마스킹
                return s[:preserve_chars] + self.masking_chars * (len(s) - preserve_chars * 2) + s[-preserve_chars:]
            elif mask_type == "full":
                # 전체 마스킹
                return self.masking_chars * len(s)
            elif mask_type == "email":
                # 이메일 특수 마스킹
                if "@" in s:
                    local, domain = s.split("@", 1)
                    masked_local = local[:1] + self.masking_chars * (len(local) - 1)
                    return f"{masked_local}@{domain}"
                return s
            else:
                return s
        
        if isinstance(data, str):
            result = mask_string(data)
            audit_logger.info(f"문자열 마스킹 완료: 타입 {mask_type}")
            return result
        
        elif isinstance(data, pd.Series):
            result = data.astype(str).apply(mask_string)
            audit_logger.info(f"시리즈 마스킹 완료: {len(data)}개 항목, 타입 {mask_type}")
            return result
        
        else:
            raise ValueError(f"지원하지 않는 데이터 타입: {type(data)}")
    
    def anonymize_data(self, data: Union[str, pd.Series, int, float], 
                      method: str = "hash") -> Union[str, pd.Series]:
        """
        데이터 익명화 - 원본 데이터를 복구 불가능하게 변환
        """
        def anonymize_value(value: Any) -> str:
            if method == "hash":
                # SHA-256 해시 기반 익명화
                hash_input = f"{str(value)}{self.hash_salt}"
                return hashlib.sha256(hash_input.encode()).hexdigest()[:12]
            
            elif method == "pseudonym":
                # 의사 식별자 생성
                random.seed(hash(str(value) + self.hash_salt))
                return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            elif method == "numeric_noise":
                # 숫자 데이터에 노이즈 추가
                if isinstance(value, (int, float)):
                    noise = random.uniform(-0.1, 0.1) * value
                    return value + noise
                return value
            
            else:
                raise ValueError(f"지원하지 않는 익명화 방법: {method}")
        
        if isinstance(data, pd.Series):
            result = data.apply(anonymize_value)
            audit_logger.info(f"시리즈 익명화 완료: {len(data)}개 항목, 방법 {method}")
            return result
        else:
            result = anonymize_value(data)
            audit_logger.info(f"값 익명화 완료: 방법 {method}")
            return result
    
    def k_anonymity(self, df: pd.DataFrame, quasi_identifiers: List[str], 
                   k: int = 5) -> pd.DataFrame:
        """
        k-익명성 구현 - 동일한 준식별자 조합을 가진 레코드가 최소 k개 이상 존재하도록 보장
        """
        # 준식별자 조합별 그룹화
        grouped = df.groupby(quasi_identifiers)
        
        # k개 미만인 그룹 식별
        small_groups = grouped.filter(lambda x: len(x) < k)
        large_groups = grouped.filter(lambda x: len(x) >= k)
        
        # 작은 그룹들을 일반화하여 k-익명성 달성
        if not small_groups.empty:
            audit_logger.warning(f"k-익명성 미달성 그룹 발견: {len(small_groups)} 레코드")
            
            # 간단한 일반화 전략: 준식별자 값을 범위나 카테고리로 변환
            for col in quasi_identifiers:
                if df[col].dtype in ['int64', 'float64']:
                    # 숫자형 데이터는 범위로 일반화
                    df[col] = pd.cut(df[col], bins=5, labels=False)
                else:
                    # 문자형 데이터는 첫 글자로 일반화
                    df[col] = df[col].astype(str).str[0] + '*'
            
            # 재그룹화 후 확인
            regrouped = df.groupby(quasi_identifiers)
            final_small_groups = regrouped.filter(lambda x: len(x) < k)
            
            if final_small_groups.empty:
                audit_logger.info(f"k-익명성 달성: k={k}")
            else:
                audit_logger.warning(f"k-익명성 부분 달성: {len(final_small_groups)} 레코드 여전히 미달")
        
        return df
    
    def differential_privacy_noise(self, data: pd.Series, epsilon: float = 1.0,
                                  sensitivity: float = 1.0) -> pd.Series:
        """
        차분 프라이버시 노이즈 추가
        """
        if not data.dtype in ['int64', 'float64']:
            raise ValueError("차분 프라이버시는 숫자형 데이터에만 적용 가능")
        
        # 라플라스 메커니즘 적용
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale, len(data))
        
        noisy_data = data + noise
        
        audit_logger.info(f"차분 프라이버시 노이즈 추가: epsilon={epsilon}, 민감도={sensitivity}")
        return noisy_data
    
    def data_retention_check(self, df: pd.DataFrame, timestamp_col: str,
                           retention_days: int = 365) -> Dict:
        """
        데이터 보존 기간 확인 및 만료 데이터 식별
        """
        if timestamp_col not in df.columns:
            raise ValueError(f"타임스탬프 컬럼 '{timestamp_col}'을 찾을 수 없습니다")
        
        # 타임스탬프 컬럼을 datetime으로 변환
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        # 보존 기간 계산
        retention_cutoff = datetime.now() - timedelta(days=retention_days)
        
        # 만료된 데이터 식별
        expired_mask = df[timestamp_col] < retention_cutoff
        expired_count = expired_mask.sum()
        
        result = {
            "total_records": len(df),
            "expired_records": expired_count,
            "retention_days": retention_days,
            "cutoff_date": retention_cutoff.strftime("%Y-%m-%d"),
            "expired_percentage": (expired_count / len(df)) * 100 if len(df) > 0 else 0
        }
        
        audit_logger.info(f"데이터 보존 기간 확인: {expired_count}개 레코드 만료 ({result['expired_percentage']:.1f}%)")
        return result
    
    def apply_privacy_policy(self, df: pd.DataFrame, privacy_config: Dict) -> pd.DataFrame:
        """
        개인정보보호 정책을 데이터프레임에 일괄 적용
        """
        result_df = df.copy()
        
        for column, config in privacy_config.items():
            if column not in result_df.columns:
                audit_logger.warning(f"컬럼 '{column}'을 찾을 수 없습니다")
                continue
            
            privacy_level = config.get("privacy_level", "none")
            
            if privacy_level == "mask":
                mask_type = config.get("mask_type", "partial")
                result_df[column] = self.mask_data(result_df[column], mask_type)
            
            elif privacy_level == "anonymize":
                method = config.get("method", "hash")
                result_df[column] = self.anonymize_data(result_df[column], method)
            
            elif privacy_level == "remove":
                result_df = result_df.drop(columns=[column])
                audit_logger.info(f"컬럼 '{column}' 제거")
            
            elif privacy_level == "differential_privacy":
                epsilon = config.get("epsilon", 1.0)
                sensitivity = config.get("sensitivity", 1.0)
                result_df[column] = self.differential_privacy_noise(
                    result_df[column], epsilon, sensitivity
                )
        
        audit_logger.info(f"개인정보보호 정책 적용 완료: {len(privacy_config)}개 컬럼")
        return result_df

# 전역 프라이버시 도구 인스턴스
privacy_tools = PrivacyEnhancingTools()
