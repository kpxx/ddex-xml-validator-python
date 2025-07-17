#!/usr/bin/env python3
"""DDEX XML驗證器命令列工具"""

import click
import sys
import os
import json
from pathlib import Path
from typing import List

# 添加src目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ddex_validator.validator import DDEXXMLValidator
from ddex_validator.models import ValidationResult


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """DDEX XML驗證器命令列工具"""
    pass


@cli.command()
@click.argument('xml_file', type=click.Path(exists=True))
@click.option('--schema', '-s', help='XSD檔案路徑')
@click.option('--schema-dir', '-d', help='XSD檔案目錄')
@click.option('--no-business-rules', is_flag=True, help='停用業務規則驗證')
@click.option('--output', '-o', type=click.Choice(['text', 'json', 'xml']), default='text', help='輸出格式')
@click.option('--output-file', '-f', help='輸出檔案路徑')
@click.option('--verbose', '-v', is_flag=True, help='詳細輸出')
def validate(xml_file, schema, schema_dir, no_business_rules, output, output_file, verbose):
    """驗證單個XML檔案"""
    
    # 建立驗證器
    validator = DDEXXMLValidator(schema_path=schema, schema_dir=schema_dir)
    
    # 執行驗證
    click.echo(f"正在驗證檔案: {xml_file}")
    result = validator.validate_file(xml_file, enable_business_rules=not no_business_rules)
    
    # 輸出結果
    if output == 'json':
        output_json(result, output_file, verbose)
    elif output == 'xml':
        output_xml(result, output_file, verbose)
    else:
        output_text(result, output_file, verbose)
    
    # 設定退出代碼
    sys.exit(0 if result.is_valid else 1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--schema', '-s', help='XSD檔案路徑')
@click.option('--schema-dir', '-d', help='XSD檔案目錄')
@click.option('--pattern', '-p', default='*.xml', help='檔案模式 (預設: *.xml)')
@click.option('--recursive', '-r', is_flag=True, help='遞迴搜尋子目錄')
@click.option('--no-business-rules', is_flag=True, help='停用業務規則驗證')
@click.option('--output', '-o', type=click.Choice(['text', 'json', 'csv']), default='text', help='輸出格式')
@click.option('--output-file', '-f', help='輸出檔案路徑')
@click.option('--continue-on-error', is_flag=True, help='遇到錯誤時繼續處理')
def batch(directory, schema, schema_dir, pattern, recursive, no_business_rules, output, output_file, continue_on_error):
    """批次驗證目錄中的XML檔案"""
    
    # 建立驗證器
    validator = DDEXXMLValidator(schema_path=schema, schema_dir=schema_dir)
    
    # 尋找XML檔案
    directory_path = Path(directory)
    if recursive:
        xml_files = list(directory_path.rglob(pattern))
    else:
        xml_files = list(directory_path.glob(pattern))
    
    if not xml_files:
        click.echo(f"在目錄 {directory} 中找不到符合模式 {pattern} 的檔案")
        sys.exit(1)
    
    click.echo(f"找到 {len(xml_files)} 個檔案")
    
    results = []
    failed_count = 0
    
    # 處理每個檔案
    with click.progressbar(xml_files, label='驗證進度') as files:
        for xml_file in files:
            try:
                result = validator.validate_file(str(xml_file), enable_business_rules=not no_business_rules)
                results.append({
                    'file': str(xml_file.relative_to(directory_path)),
                    'result': result
                })
                
                if not result.is_valid:
                    failed_count += 1
                    
            except Exception as e:
                if continue_on_error:
                    click.echo(f"\n錯誤處理檔案 {xml_file}: {e}", err=True)
                    failed_count += 1
                else:
                    click.echo(f"\n處理檔案 {xml_file} 時發生錯誤: {e}", err=True)
                    sys.exit(1)
    
    # 輸出結果
    if output == 'json':
        output_batch_json(results, output_file)
    elif output == 'csv':
        output_batch_csv(results, output_file)
    else:
        output_batch_text(results, output_file)
    
    # 顯示統計
    click.echo(f"\n統計結果:")
    click.echo(f"總檔案數: {len(results)}")
    click.echo(f"有效檔案: {len(results) - failed_count}")
    click.echo(f"無效檔案: {failed_count}")
    
    sys.exit(0 if failed_count == 0 else 1)


@cli.command()
@click.argument('xml_file', type=click.Path(exists=True))
def info(xml_file):
    """顯示XML檔案資訊"""
    from ddex_validator.utils import detect_ddex_version, detect_message_type
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        ddex_version = detect_ddex_version(xml_content)
        message_type = detect_message_type(xml_content)
        
        click.echo(f"檔案: {xml_file}")
        click.echo(f"DDEX版本: {ddex_version or '未知'}")
        click.echo(f"訊息類型: {message_type or '未知'}")
        
        # 檔案大小
        file_size = os.path.getsize(xml_file)
        click.echo(f"檔案大小: {file_size:,} bytes")
        
        # 行數統計
        line_count = xml_content.count('\n') + 1
        click.echo(f"行數: {line_count:,}")
        
    except Exception as e:
        click.echo(f"讀取檔案時發生錯誤: {e}", err=True)
        sys.exit(1)

def output_text(result: ValidationResult, output_file: str = None, verbose: bool = False):
    """文字格式輸出 - 改進版本"""
    output_lines = []
    
    # 基本資訊
    output_lines.append("DDEX XML驗證結果")
    output_lines.append("=" * 60)
    output_lines.append(f"狀態: {'✅ 通過' if result.is_valid else '❌ 失敗'}")
    output_lines.append(f"訊息類型: {result.message_type or '未知'}")
    output_lines.append(f"DDEX版本: {result.ddex_version or '未知'}")
    output_lines.append(f"錯誤數量: {len(result.errors)}")
    output_lines.append(f"警告數量: {len(result.warnings)}")
    
    if result.validation_time:
        output_lines.append(f"驗證時間: {result.validation_time:.3f}秒")
    
    # 詳細錯誤資訊
    if result.errors:
        output_lines.append("\n" + "🔴 錯誤詳情:")
        output_lines.append("-" * 40)
        for i, error in enumerate(result.errors, 1):
            output_lines.append(f"\n{i}. {error}")
            
            # 如果有多個錯誤，添加分隔線
            if i < len(result.errors):
                output_lines.append("")
    
    # 警告資訊
    if result.warnings:
        output_lines.append("\n" + "🟡 警告:")
        output_lines.append("-" * 40)
        for i, warning in enumerate(result.warnings, 1):
            output_lines.append(f"\n{i}. {warning}")
    
    # 摘要建議
    if result.errors:
        output_lines.append("\n" + "💡 修正建議:")
        output_lines.append("-" * 40)
        output_lines.append("1. 請根據上述錯誤訊息逐一修正XML內容")
        output_lines.append("2. 參考DDEX官方文檔確認元素格式")
        output_lines.append("3. 使用XML編輯器檢查語法錯誤")
        output_lines.append("4. 確認所有必要元素都已包含")
    
    output_content = "\n".join(output_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        click.echo(f"結果已儲存至: {output_file}")
    else:
        click.echo(output_content)

def output_json(result: ValidationResult, output_file: str = None, verbose: bool = False):
    """JSON格式輸出"""
    data = {
        "summary": result.get_summary(),
        "errors": [
            {
                "severity": error.severity.value,
                "message": error.message,
                "line_number": error.line_number,
                "column_number": error.column_number,
                "element_path": error.element_path,
                "error_code": error.error_code
            }
            for error in result.errors
        ]
    }
    
    if verbose:
        data["warnings"] = [
            {
                "severity": warning.severity.value,
                "message": warning.message,
                "line_number": warning.line_number,
                "column_number": warning.column_number,
                "element_path": warning.element_path,
                "error_code": warning.error_code
            }
            for warning in result.warnings
        ]
    
    json_content = json.dumps(data, ensure_ascii=False, indent=2)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_content)
        click.echo(f"結果已儲存至: {output_file}")
    else:
        click.echo(json_content)


def output_xml(result: ValidationResult, output_file: str = None, verbose: bool = False):
    """XML格式輸出"""
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom
    
    root = Element("ValidationResult")
    
    # 摘要
    summary = SubElement(root, "Summary")
    SubElement(summary, "IsValid").text = str(result.is_valid).lower()
    SubElement(summary, "MessageType").text = result.message_type or ""
    SubElement(summary, "DDEXVersion").text = result.ddex_version or ""
    SubElement(summary, "ErrorsCount").text = str(len(result.errors))
    SubElement(summary, "WarningsCount").text = str(len(result.warnings))
    
    if result.validation_time:
        SubElement(summary, "ValidationTime").text = str(result.validation_time)
    
    # 錯誤
    if result.errors:
        errors_elem = SubElement(root, "Errors")
        for error in result.errors:
            error_elem = SubElement(errors_elem, "Error")
            SubElement(error_elem, "Severity").text = error.severity.value
            SubElement(error_elem, "Message").text = error.message
            if error.line_number:
                SubElement(error_elem, "LineNumber").text = str(error.line_number)
            if error.column_number:
                SubElement(error_elem, "ColumnNumber").text = str(error.column_number)
            if error.element_path:
                SubElement(error_elem, "ElementPath").text = error.element_path
            if error.error_code:
                SubElement(error_elem, "ErrorCode").text = error.error_code
    
    # 警告
    if result.warnings and verbose:
        warnings_elem = SubElement(root, "Warnings")
        for warning in result.warnings:
            warning_elem = SubElement(warnings_elem, "Warning")
            SubElement(warning_elem, "Severity").text = warning.severity.value
            SubElement(warning_elem, "Message").text = warning.message
            if warning.line_number:
                SubElement(warning_elem, "LineNumber").text = str(warning.line_number)
            if warning.element_path:
                SubElement(warning_elem, "ElementPath").text = warning.element_path
            if warning.error_code:
                SubElement(warning_elem, "ErrorCode").text = warning.error_code
    
    # 格式化XML
    rough_string = tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    xml_content = reparsed.toprettyxml(indent="  ")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        click.echo(f"結果已儲存至: {output_file}")
    else:
        click.echo(xml_content)


def output_batch_text(results: List[dict], output_file: str = None):
    """批次結果文字輸出"""
    output_lines = []
    
    output_lines.append("DDEX XML批次驗證結果")
    output_lines.append("=" * 60)
    
    for item in results:
        file_name = item['file']
        result = item['result']
        status = "✓" if result.is_valid else "✗"
        
        output_lines.append(f"{status} {file_name}")
        if not result.is_valid:
            output_lines.append(f"    錯誤: {len(result.errors)}, 警告: {len(result.warnings)}")
    
    output_content = "\n".join(output_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        click.echo(f"結果已儲存至: {output_file}")
    else:
        click.echo(output_content)


def output_batch_json(results: List[dict], output_file: str = None):
    """批次結果JSON輸出"""
    data = []
    
    for item in results:
        file_name = item['file']
        result = item['result']
        
        data.append({
            "file": file_name,
            "summary": result.get_summary(),
            "errors": [str(error) for error in result.errors],
            "warnings": [str(warning) for warning in result.warnings]
        })
    
    json_content = json.dumps(data, ensure_ascii=False, indent=2)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_content)
        click.echo(f"結果已儲存至: {output_file}")
    else:
        click.echo(json_content)


def output_batch_csv(results: List[dict], output_file: str = None):
    """批次結果CSV輸出"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 標題行
    writer.writerow(['檔案', '狀態', '訊息類型', 'DDEX版本', '錯誤數', '警告數', '驗證時間'])
    
    # 資料行
    for item in results:
        file_name = item['file']
        result = item['result']
        
        writer.writerow([
            file_name,
            '通過' if result.is_valid else '失敗',
            result.message_type or '',
            result.ddex_version or '',
            len(result.errors),
            len(result.warnings),
            f"{result.validation_time:.3f}" if result.validation_time else ''
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_content)
        click.echo(f"結果已儲存至: {output_file}")
    else:
        click.echo(csv_content)


if __name__ == '__main__':
    cli()

