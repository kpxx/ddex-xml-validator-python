"""DDEX XML驗證器主類別"""

import os
import time
from typing import List, Optional, Union, Dict, Any  # 添加 Any 導入
from lxml import etree
import xmlschema
from .models import ValidationResult, ValidationIssue, SeverityLevel, DDEXMessage
from .rules import DDEXBusinessRules
from .utils import detect_ddex_version, detect_message_type, find_schema_file
from .constants import DDEX_ERN_382_NAMESPACE, ERROR_TYPES


class DDEXXMLValidator:
    """DDEX XML驗證器"""
    
    def __init__(self, schema_path: Optional[str] = None, schema_dir: Optional[str] = None,
                 enable_business_rules: bool = True, strict_mode: bool = False):
        """
        初始化驗證器
        
        Args:
            schema_path: XSD檔案路徑
            schema_dir: XSD檔案目錄
            enable_business_rules: 是否啟用業務規則驗證
            strict_mode: 嚴格模式，將警告視為錯誤
        """
        self.schema_path = schema_path
        self.schema_dir = schema_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'schemas', 'ddex')
        self.enable_business_rules = enable_business_rules
        self.strict_mode = strict_mode
        self.business_rules = DDEXBusinessRules()
        self._schema_cache: Dict[str, xmlschema.XMLSchema] = {}
    
    def validate_file(self, xml_file_path: str, enable_business_rules: Optional[bool] = None) -> ValidationResult:
        """
        驗證XML檔案
        
        Args:
            xml_file_path: XML檔案路徑
            enable_business_rules: 是否啟用業務規則驗證（覆蓋初始化設定）
            
        Returns:
            ValidationResult: 驗證結果
        """
        try:
            if not os.path.exists(xml_file_path):
                return ValidationResult.failure(
                    f"檔案不存在: {xml_file_path}",
                    "FILE_NOT_FOUND"
                )
            
            # 取得檔案資訊
            file_size = os.path.getsize(xml_file_path)
            
            with open(xml_file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            result = self.validate_string(xml_content, enable_business_rules)
            result.file_path = xml_file_path
            result.file_size = file_size
            
            return result
            
        except UnicodeDecodeError:
            # 嘗試其他編碼
            try:
                with open(xml_file_path, 'r', encoding='utf-8-sig') as f:
                    xml_content = f.read()
                result = self.validate_string(xml_content, enable_business_rules)
                result.file_path = xml_file_path
                result.file_size = os.path.getsize(xml_file_path)
                return result
            except Exception:
                return ValidationResult.failure(
                    f"無法讀取檔案，編碼錯誤: {xml_file_path}",
                    "FILE_ENCODING_ERROR"
                )
        except Exception as e:
            return ValidationResult.failure(
                f"讀取檔案時發生錯誤: {str(e)}",
                "FILE_READ_ERROR"
            )
    
    def validate_string(self, xml_content: str, enable_business_rules: Optional[bool] = None) -> ValidationResult:
        """
        驗證XML字串
        
        Args:
            xml_content: XML內容
            enable_business_rules: 是否啟用業務規則驗證（覆蓋初始化設定）
            
        Returns:
            ValidationResult: 驗證結果
        """
        start_time = time.time()
        
        # 決定是否啟用業務規則驗證
        use_business_rules = enable_business_rules if enable_business_rules is not None else self.enable_business_rules
        
        # 檢測DDEX版本和訊息類型
        ddex_version = detect_ddex_version(xml_content)
        message_type = detect_message_type(xml_content)
        
        errors = []
        warnings = []
        info = []
        
        # 基本XML格式檢查
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            return ValidationResult.failure(
                f"XML語法錯誤: {str(e)}",
                "XML_SYNTAX_ERROR"
            )
        except Exception as e:
            return ValidationResult.failure(
                f"XML解析失敗: {str(e)}",
                "XML_PARSE_ERROR"
            )
        
        # XSD架構驗證
        schema_errors = self._validate_schema(xml_content, ddex_version)
        errors.extend(schema_errors)
        
        # 業務規則驗證（只有在沒有嚴重架構錯誤時才進行）
        if use_business_rules and not self._has_critical_errors(schema_errors):
            try:
                business_issues = self._validate_business_rules(root, message_type)
                
                for issue in business_issues:
                    if issue.severity == SeverityLevel.ERROR:
                        errors.append(issue)
                    elif issue.severity == SeverityLevel.WARNING:
                        if self.strict_mode:
                            issue.severity = SeverityLevel.ERROR
                            errors.append(issue)
                        else:
                            warnings.append(issue)
                    else:
                        info.append(issue)
                        
            except Exception as e:
                errors.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message=f"業務規則驗證失敗: {str(e)}",
                    error_code="BUSINESS_RULE_ERROR",
                    suggestion="請檢查XML結構是否正確"
                ))
        
        # 添加資訊性訊息
        if ddex_version:
            info.append(ValidationIssue(
                severity=SeverityLevel.INFO,
                message=f"檢測到DDEX版本: {ddex_version}",
                error_code="DDEX_VERSION_DETECTED"
            ))
        
        if message_type:
            info.append(ValidationIssue(
                severity=SeverityLevel.INFO,
                message=f"檢測到訊息類型: {message_type}",
                error_code="MESSAGE_TYPE_DETECTED"
            ))
        
        validation_time = time.time() - start_time
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            message_type=message_type,
            ddex_version=ddex_version,
            validation_time=validation_time
        )
    
    def validate_batch(self, file_paths: List[str], 
                      enable_business_rules: Optional[bool] = None) -> List[ValidationResult]:
        """
        批次驗證多個檔案
        
        Args:
            file_paths: XML檔案路徑列表
            enable_business_rules: 是否啟用業務規則驗證
            
        Returns:
            List[ValidationResult]: 驗證結果列表
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.validate_file(file_path, enable_business_rules)
                results.append(result)
            except Exception as e:
                error_result = ValidationResult.failure(
                    f"處理檔案 {file_path} 時發生錯誤: {str(e)}",
                    "BATCH_PROCESSING_ERROR"
                )
                error_result.file_path = file_path
                results.append(error_result)
        
        return results
    
    def get_message_info(self, xml_content: str) -> Optional[DDEXMessage]:
        """
        取得DDEX訊息資訊
        
        Args:
            xml_content: XML內容
            
        Returns:
            DDEXMessage: DDEX訊息資訊
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # 取得基本資訊
            message_type = detect_message_type(xml_content)
            ddex_version = detect_ddex_version(xml_content)
            
            if not message_type or not ddex_version:
                return None
            
            # 取得屬性資訊
            schema_version = root.get('MessageSchemaVersionId')
            business_profile_version = root.get('BusinessProfileVersionId')
            release_profile_version = root.get('ReleaseProfileVersionId')
            language = root.get('{http://www.w3.org/XML/1998/namespace}lang')
            
            # 取得命名空間
            namespace = None
            if root.nsmap:
                for prefix, uri in root.nsmap.items():
                    if prefix is None:  # 預設命名空間
                        namespace = uri
                        break
            
            return DDEXMessage(
                message_type=message_type,
                ddex_version=ddex_version,
                schema_version=schema_version,
                business_profile_version=business_profile_version,
                release_profile_version=release_profile_version,
                language=language,
                namespace=namespace
            )
            
        except Exception:
            return None
    
    def _validate_schema(self, xml_content: str, ddex_version: Optional[str]) -> List[ValidationIssue]:
        """XSD架構驗證"""
        errors = []
        
        try:
            # 取得XSD檔案路徑
            schema_path = self._get_schema_path(ddex_version)
            if not schema_path:
                errors.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message=f"找不到DDEX版本 {ddex_version} 的XSD檔案",
                    error_code="SCHEMA_NOT_FOUND",
                    context=f"搜尋路徑: {self.schema_dir}",
                    suggestion="請確認XSD檔案存在於正確的目錄中，或使用 -Schema 參數指定XSD檔案路徑"
                ))
                return errors
            
            # 載入或取得快取的schema
            schema = self._get_schema(schema_path)
            
            # 驗證XML
            try:
                schema.validate(xml_content)
                
            except xmlschema.XMLSchemaException as e:
                # 提取詳細的錯誤資訊
                error_msg = str(e)
                line_num = getattr(e, 'line', None)
                col_num = getattr(e, 'column', None)
                
                # 嘗試提取元素路徑
                element_path = self._extract_element_path(error_msg)
                
                # 生成修正建議
                suggestion = self._generate_suggestion(error_msg)
                
                errors.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message=f"XSD驗證失敗: {error_msg}",
                    line_number=line_num,
                    column_number=col_num,
                    element_path=element_path,
                    error_code="SCHEMA_VALIDATION_ERROR",
                    context=f"使用XSD: {os.path.basename(schema_path)}",
                    suggestion=suggestion
                ))
                
            except Exception as e:
                # 嘗試使用lxml進行更詳細的錯誤報告
                try:
                    xmlschema_doc = etree.parse(schema_path)
                    xmlschema_parsed = etree.XMLSchema(xmlschema_doc)
                    xml_doc = etree.fromstring(xml_content.encode('utf-8'))
                    xmlschema_parsed.assertValid(xml_doc)
                    
                except etree.DocumentInvalid as lxml_error:
                    error_log = xmlschema_parsed.error_log
                    if error_log:
                        for log_entry in error_log:
                            errors.append(ValidationIssue(
                                severity=SeverityLevel.ERROR,
                                message=f"XSD驗證失敗: {log_entry.message}",
                                line_number=log_entry.line,
                                column_number=log_entry.column,
                                error_code="SCHEMA_VALIDATION_ERROR",
                                context=f"使用XSD: {os.path.basename(schema_path)}",
                                suggestion=self._generate_suggestion(log_entry.message)
                            ))
                    else:
                        errors.append(ValidationIssue(
                            severity=SeverityLevel.ERROR,
                            message=f"XSD驗證失敗: {str(lxml_error)}",
                            error_code="SCHEMA_VALIDATION_ERROR",
                            context=f"使用XSD: {os.path.basename(schema_path)}"
                        ))
                        
                except Exception:
                    errors.append(ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        message=f"XSD驗證失敗: {str(e)}",
                        error_code="SCHEMA_VALIDATION_ERROR",
                        context=f"使用XSD: {os.path.basename(schema_path)}"
                    ))
        
        except Exception as e:
            errors.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                message=f"載入XSD檔案失敗: {str(e)}",
                error_code="SCHEMA_LOAD_ERROR",
                context=f"XSD路徑: {schema_path}",
                suggestion="請檢查XSD檔案是否存在且格式正確"
            ))
        
        return errors
    
    def _validate_business_rules(self, root: etree.Element, message_type: Optional[str]) -> List[ValidationIssue]:
        """業務規則驗證"""
        issues = []
        
        try:
            # 識別碼驗證
            issues.extend(self.business_rules.validate_identifiers(root))
            
            # 時間長度驗證
            issues.extend(self.business_rules.validate_durations(root))
            
            # 日期驗證
            issues.extend(self.business_rules.validate_dates(root))
            
            # 地區代碼驗證
            issues.extend(self.business_rules.validate_territories(root))
            
            # 語言代碼驗證
            issues.extend(self.business_rules.validate_languages(root))
            
            # 必要元素驗證
            if message_type:
                issues.extend(self.business_rules.validate_required_elements(root, message_type))
            
            # 業務邏輯驗證
            issues.extend(self.business_rules.validate_business_logic(root))
            
            # 技術細節驗證
            issues.extend(self.business_rules.validate_technical_details(root))
            
        except Exception as e:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                message=f"業務規則驗證過程中發生錯誤: {str(e)}",
                error_code="BUSINESS_RULE_PROCESSING_ERROR",
                suggestion="請檢查XML結構是否符合DDEX規範"
            ))
        
        return issues
    
    def _get_schema_path(self, ddex_version: Optional[str]) -> Optional[str]:
        """取得XSD檔案路徑"""
        if self.schema_path and os.path.exists(self.schema_path):
            return self.schema_path
        
        if ddex_version and self.schema_dir:
            schema_path = find_schema_file(self.schema_dir, ddex_version)
            if schema_path:
                return schema_path
        
        # 預設使用3.8.2版本
        default_path = find_schema_file(self.schema_dir, "3.8.2")
        if default_path:
            return default_path
        
        # 最後嘗試在根目錄尋找
        root_schema = os.path.join(os.path.dirname(self.schema_dir), "ddex_3-8-2.xsd")
        if os.path.exists(root_schema):
            return root_schema
        
        return None
    
    def _get_schema(self, schema_path: str) -> xmlschema.XMLSchema:
        """取得或載入XSD schema"""
        if schema_path not in self._schema_cache:
            try:
                self._schema_cache[schema_path] = xmlschema.XMLSchema(schema_path)
            except Exception as e:
                raise Exception(f"無法載入XSD檔案 {schema_path}: {str(e)}")
        
        return self._schema_cache[schema_path]
    
    def _extract_element_path(self, error_msg: str) -> Optional[str]:
        """從錯誤訊息中提取元素路徑"""
        import re
        
        # 嘗試匹配常見的元素路徑模式
        patterns = [
            r"element '([^']+)'",
            r"Element '([^']+)'",
            r"tag '([^']+)'",
            r"<([^>]+)>",
            r"path: ([^\s]+)",
            r"at ([^\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_msg, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_suggestion(self, error_msg: str) -> Optional[str]:
        """根據錯誤訊息生成修正建議"""
        suggestions = {
            "required": "請確認所有必要元素都已包含",
            "invalid": "請檢查元素值是否符合規範格式",
            "unexpected": "請移除不應該出現的元素",
            "missing": "請添加缺少的必要元素",
            "namespace": "請檢查XML命名空間是否正確",
            "type": "請檢查資料類型是否正確",
            "format": "請檢查資料格式是否正確",
            "empty": "請提供有效的元素值",
            "duplicate": "請移除重複的元素",
            "reference": "請檢查引用的元素是否存在"
        }
        
        error_lower = error_msg.lower()
        for keyword, suggestion in suggestions.items():
            if keyword in error_lower:
                return suggestion
        
        return "請參考DDEX規範文件檢查XML格式"
    
    def _has_critical_errors(self, errors: List[ValidationIssue]) -> bool:
        """檢查是否有嚴重錯誤，影響後續驗證"""
        critical_error_codes = [
            "SCHEMA_NOT_FOUND",
            "SCHEMA_LOAD_ERROR",
            "XML_SYNTAX_ERROR",
            "XML_PARSE_ERROR"
        ]
        
        return any(error.error_code in critical_error_codes for error in errors)
    
    def clear_cache(self):
        """清除schema快取"""
        self._schema_cache.clear()
    
    def get_supported_versions(self) -> List[str]:
        """取得支援的DDEX版本列表"""
        versions = []
        
        if os.path.exists(self.schema_dir):
            for item in os.listdir(self.schema_dir):
                item_path = os.path.join(self.schema_dir, item)
                if os.path.isdir(item_path):
                    versions.append(item)
        
        return sorted(versions)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """取得快取資訊"""
        return {
            "cached_schemas": len(self._schema_cache),
            "schema_paths": list(self._schema_cache.keys())
        }

