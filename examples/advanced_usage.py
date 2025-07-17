#!/usr/bin/env python3
"""進階使用範例"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ddex_validator.validator import DDEXXMLValidator
from ddex_validator.models import SeverityLevel


def validate_directory(directory_path: str, output_file: str = None):
    """批次驗證目錄中的所有XML檔案"""
    validator = DDEXXMLValidator()
    results = []
    
    xml_files = list(Path(directory_path).glob("*.xml"))
    
    print(f"找到 {len(xml_files)} 個XML檔案")
    
    for xml_file in xml_files:
        print(f"驗證: {xml_file.name}")
        result = validator.validate_file(str(xml_file))
        
        results.append({
            "file": xml_file.name,
            "result": result.get_summary(),
            "errors": [str(error) for error in result.errors],
            "warnings": [str(warning) for warning in result.warnings]
        })
    
    # 輸出結果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"結果已儲存至: {output_file}")
    
    # 統計
    total_files = len(results)
    valid_files = sum(1 for r in results if r["result"]["is_valid"])
    
    print(f"\n統計結果:")
    print(f"總檔案數: {total_files}")
    print(f"有效檔案: {valid_files}")
    print(f"無效檔案: {total_files - valid_files}")


def custom_validation_example():
    """自定義驗證範例"""
    
    class CustomDDEXValidator(DDEXXMLValidator):
        """自定義DDEX驗證器"""
        
        def validate_string(self, xml_content: str, enable_business_rules: bool = True):
            # 呼叫父類別的驗證
            result = super().validate_string(xml_content, enable_business_rules)
            
            # 添加自定義驗證邏輯
            custom_issues = self._custom_validation(xml_content)
            result.warnings.extend(custom_issues)
            
            return result
        
        def _custom_validation(self, xml_content: str):
            """自定義驗證邏輯"""
            from lxml import etree
            from ddex_validator.models import ValidationIssue, SeverityLevel
            
            issues = []
            
            try:
                root = etree.fromstring(xml_content.encode('utf-8'))
                
                # 檢查是否有DisplayArtistName
                releases = root.xpath(".//Release")
                for release in releases:
                    if not release.xpath(".//DisplayArtistName"):
                        issues.append(ValidationIssue(
                            severity=SeverityLevel.WARNING,
                            message="建議為Release提供DisplayArtistName",
                            error_code="MISSING_DISPLAY_ARTIST"
                        ))
                
                # 檢查Genre是否存在
                if not root.xpath(".//Genre"):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        message="建議提供Genre資訊",
                        error_code="MISSING_GENRE"
                    ))
                
            except Exception as e:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    message=f"自定義驗證失敗: {str(e)}",
                    error_code="CUSTOM_VALIDATION_ERROR"
                ))
            
            return issues
    
    # 使用自定義驗證器
    validator = CustomDDEXValidator()
    
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <NewReleaseMessage xmlns="http://ddex.net/xml/ern/382" MessageSchemaVersionId="3.8.2">
        <!-- 簡化的XML內容 -->
    </NewReleaseMessage>"""
    
    result = validator.validate_string(sample_xml)
    result.print_summary()


def main():
    print("DDEX XML驗證器 - 進階使用範例")
    print("=" * 50)
    
    # 範例1: 批次驗證
    print("\n1. 批次驗證範例")
    # validate_directory("test_data/xml_files", "validation_results.json")
    
    # 範例2: 自定義驗證
    print("\n2. 自定義驗證範例")
    custom_validation_example()


if __name__ == "__main__":
    main()

