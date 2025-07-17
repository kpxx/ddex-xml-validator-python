"""驗證結果模型"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class SeverityLevel(Enum):
    """嚴重程度等級"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    """驗證問題"""
    severity: SeverityLevel
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    element_path: Optional[str] = None
    error_code: Optional[str] = None
    context: Optional[str] = None
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        """格式化輸出驗證問題"""
        parts = []
        
        # 嚴重程度和錯誤代碼
        severity_part = f"[{self.severity.value}"
        if self.error_code:
            severity_part += f":{self.error_code}"
        severity_part += "]"
        parts.append(severity_part)
        
        # 位置資訊
        if self.line_number and self.column_number:
            parts.append(f"行 {self.line_number}, 列 {self.column_number}")
        elif self.element_path:
            parts.append(f"元素: {self.element_path}")
        
        # 組合基本資訊
        basic_info = " ".join(parts) + f": {self.message}"
        
        # 添加上下文和建議
        full_message = basic_info
        if self.context:
            full_message += f"\n    上下文: {self.context}"
        if self.suggestion:
            full_message += f"\n    建議: {self.suggestion}"
            
        return full_message
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式，便於JSON輸出"""
        return {
            "severity": self.severity.value,
            "message": self.message,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "element_path": self.element_path,
            "error_code": self.error_code,
            "context": self.context,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationResult:
    """驗證結果"""
    is_valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    message_type: Optional[str] = None
    ddex_version: Optional[str] = None
    validation_time: Optional[float] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    @property
    def has_errors(self) -> bool:
        """是否有錯誤"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0
    
    @property
    def has_info(self) -> bool:
        """是否有資訊"""
        return len(self.info) > 0
    
    @property
    def total_issues(self) -> int:
        """總問題數量"""
        return len(self.errors) + len(self.warnings) + len(self.info)
    
    def get_summary(self) -> Dict[str, Any]:
        """取得驗證摘要"""
        return {
            "is_valid": self.is_valid,
            "message_type": self.message_type,
            "ddex_version": self.ddex_version,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "info_count": len(self.info),
            "total_issues": self.total_issues,
            "validation_time": self.validation_time,
            "file_path": self.file_path,
            "file_size": self.file_size
        }
    
    def get_issues_by_severity(self, severity: SeverityLevel) -> List[ValidationIssue]:
        """根據嚴重程度取得問題列表"""
        if severity == SeverityLevel.ERROR:
            return self.errors
        elif severity == SeverityLevel.WARNING:
            return self.warnings
        elif severity == SeverityLevel.INFO:
            return self.info
        return []
    
    def get_issues_by_error_code(self, error_code: str) -> List[ValidationIssue]:
        """根據錯誤代碼取得問題列表"""
        all_issues = self.errors + self.warnings + self.info
        return [issue for issue in all_issues if issue.error_code == error_code]
    
    def to_json(self, indent: int = 2) -> str:
        """轉換為JSON格式"""
        data = {
            "summary": self.get_summary(),
            "errors": [error.to_dict() for error in self.errors],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "info": [info.to_dict() for info in self.info]
        }
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    def print_summary(self, show_details: bool = True, show_warnings: bool = True):
        """列印驗證摘要"""
        print(f"\n{'='*60}")
        print(f"DDEX XML 驗證結果")
        print(f"{'='*60}")
        print(f"狀態: {'✅ 通過' if self.is_valid else '❌ 失敗'}")
        
        if self.file_path:
            print(f"檔案: {self.file_path}")
        if self.file_size:
            print(f"檔案大小: {self.file_size:,} bytes")
        
        print(f"訊息類型: {self.message_type or '未知'}")
        print(f"DDEX版本: {self.ddex_version or '未知'}")
        print(f"錯誤: {len(self.errors)}")
        print(f"警告: {len(self.warnings)}")
        print(f"資訊: {len(self.info)}")
        
        if self.validation_time:
            print(f"驗證時間: {self.validation_time:.3f}秒")
        
        print(f"{'='*60}")
        
        # 顯示錯誤詳情
        if show_details and self.errors:
            print(f"\n🔴 錯誤詳情 ({len(self.errors)}):")
            print("-" * 40)
            for i, error in enumerate(self.errors, 1):
                print(f"\n{i}. {error}")
        
        # 顯示警告詳情
        if show_details and show_warnings and self.warnings:
            print(f"\n🟡 警告詳情 ({len(self.warnings)}):")
            print("-" * 40)
            for i, warning in enumerate(self.warnings, 1):
                print(f"\n{i}. {warning}")
        
        # 顯示資訊
        if show_details and self.info:
            print(f"\n🔵 資訊 ({len(self.info)}):")
            print("-" * 40)
            for i, info in enumerate(self.info, 1):
                print(f"\n{i}. {info}")
        
        # 顯示修正建議摘要
        if self.errors:
            print(f"\n💡 修正建議:")
            print("-" * 40)
            print("1. 請根據上述錯誤訊息逐一修正XML內容")
            print("2. 參考DDEX官方文檔確認元素格式")
            print("3. 使用XML編輯器檢查語法錯誤")
            print("4. 確認所有必要元素都已包含")
    
    @classmethod
    def success(cls, message_type: str = None, ddex_version: str = None, 
                validation_time: float = None) -> 'ValidationResult':
        """創建成功的驗證結果"""
        return cls(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[],
            message_type=message_type,
            ddex_version=ddex_version,
            validation_time=validation_time
        )
    
    @classmethod
    def failure(cls, error_message: str, error_code: str = None) -> 'ValidationResult':
        """創建失敗的驗證結果"""
        error = ValidationIssue(
            severity=SeverityLevel.ERROR,
            message=error_message,
            error_code=error_code or "VALIDATION_FAILED"
        )
        return cls(
            is_valid=False,
            errors=[error],
            warnings=[],
            info=[]
        )


@dataclass
class DDEXMessage:
    """DDEX訊息資訊"""
    message_type: str
    ddex_version: str
    schema_version: Optional[str] = None
    business_profile_version: Optional[str] = None
    release_profile_version: Optional[str] = None
    language: Optional[str] = None
    namespace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "message_type": self.message_type,
            "ddex_version": self.ddex_version,
            "schema_version": self.schema_version,
            "business_profile_version": self.business_profile_version,
            "release_profile_version": self.release_profile_version,
            "language": self.language,
            "namespace": self.namespace
        }


class ValidationStatistics:
    """驗證統計資訊"""
    
    def __init__(self):
        self.total_files = 0
        self.valid_files = 0
        self.invalid_files = 0
        self.total_errors = 0
        self.total_warnings = 0
        self.error_codes: Dict[str, int] = {}
        self.message_types: Dict[str, int] = {}
        self.ddex_versions: Dict[str, int] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def add_result(self, result: ValidationResult):
        """添加驗證結果到統計中"""
        self.total_files += 1
        
        if result.is_valid:
            self.valid_files += 1
        else:
            self.invalid_files += 1
        
        self.total_errors += len(result.errors)
        self.total_warnings += len(result.warnings)
        
        # 統計錯誤代碼
        for error in result.errors:
            if error.error_code:
                self.error_codes[error.error_code] = self.error_codes.get(error.error_code, 0) + 1
        
        # 統計訊息類型
        if result.message_type:
            self.message_types[result.message_type] = self.message_types.get(result.message_type, 0) + 1
        
        # 統計DDEX版本
        if result.ddex_version:
            self.ddex_versions[result.ddex_version] = self.ddex_versions.get(result.ddex_version, 0) + 1
    
    def start_timing(self):
        """開始計時"""
        self.start_time = datetime.now()
    
    def end_timing(self):
        """結束計時"""
        self.end_time = datetime.now()
    
    @property
    def total_time(self) -> Optional[float]:
        """總處理時間（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_files == 0:
            return 0.0
        return (self.valid_files / self.total_files) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """取得統計摘要"""
        return {
            "total_files": self.total_files,
            "valid_files": self.valid_files,
            "invalid_files": self.invalid_files,
            "success_rate": round(self.success_rate, 2),
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "total_time": self.total_time,
            "error_codes": dict(sorted(self.error_codes.items(), key=lambda x: x[1], reverse=True)),
            "message_types": self.message_types,
            "ddex_versions": self.ddex_versions
        }
    
    def print_summary(self):
        """列印統計摘要"""
        print(f"\n{'='*60}")
        print(f"驗證統計摘要")
        print(f"{'='*60}")
        print(f"總檔案數: {self.total_files}")
        print(f"有效檔案: {self.valid_files}")
        print(f"無效檔案: {self.invalid_files}")
        print(f"成功率: {self.success_rate:.1f}%")
        print(f"總錯誤數: {self.total_errors}")
        print(f"總警告數: {self.total_warnings}")
        
        if self.total_time:
            print(f"總處理時間: {self.total_time:.2f}秒")
            if self.total_files > 0:
                print(f"平均處理時間: {self.total_time/self.total_files:.3f}秒/檔案")
        
        if self.error_codes:
            print(f"\n最常見的錯誤:")
            for error_code, count in list(self.error_codes.items())[:5]:
                print(f"  {error_code}: {count}次")
        
        if self.message_types:
            print(f"\n訊息類型分布:")
            for msg_type, count in self.message_types.items():
                print(f"  {msg_type}: {count}個")
        
        if self.ddex_versions:
            print(f"\nDDEX版本分布:")
            for version, count in self.ddex_versions.items():
                print(f"  {version}: {count}個")

