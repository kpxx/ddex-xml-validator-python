"""工具函數"""

import os
from typing import Optional
from lxml import etree


def detect_ddex_version(xml_content: str) -> Optional[str]:
    """檢測DDEX版本"""
    try:
        root = etree.fromstring(xml_content.encode('utf-8'))
        
        # 檢查命名空間
        nsmap = root.nsmap
        for prefix, uri in nsmap.items():
            if 'ddex.net/xml/ern' in uri:
                if '382' in uri:
                    return "3.8.2"
                elif '41' in uri:
                    return "4.1"
        
        # 檢查MessageSchemaVersionId屬性
        version_attr = root.get('MessageSchemaVersionId')
        if version_attr:
            return version_attr
        
        return None
    except Exception:
        return None


def detect_message_type(xml_content: str) -> Optional[str]:
    """檢測訊息類型"""
    try:
        root = etree.fromstring(xml_content.encode('utf-8'))
        tag = root.tag
        if '}' in tag:
            tag = tag.split('}')[1]  # 移除命名空間
        return tag
    except Exception:
        return None


def find_schema_file(schema_dir: str, version: str) -> Optional[str]:
    """尋找對應版本的XSD檔案"""
    possible_files = [
        f"ddex_{version.replace('.', '-')}.xsd",
        f"ern-main-{version}.xsd",
        f"ern-main.xsd",
        "ddex_3-8-2.xsd"  # 預設檔案名
    ]
    
    version_dir = os.path.join(schema_dir, version)
    if os.path.exists(version_dir):
        for filename in possible_files:
            filepath = os.path.join(version_dir, filename)
            if os.path.exists(filepath):
                return filepath
    
    # 在根目錄尋找
    for filename in possible_files:
        filepath = os.path.join(schema_dir, filename)
        if os.path.exists(filepath):
            return filepath
    
    return None


def format_xml(xml_content: str, indent: str = "  ") -> str:
    """格式化XML內容"""
    try:
        root = etree.fromstring(xml_content.encode('utf-8'))
        return etree.tostring(root, pretty_print=True, encoding='unicode')
    except Exception:
        return xml_content


def get_element_text_safe(element: etree.Element, xpath: str) -> Optional[str]:
    """安全地取得元素文字內容"""
    try:
        elements = element.xpath(xpath)
        return elements[0].text if elements and elements[0].text else None
    except Exception:
        return None

