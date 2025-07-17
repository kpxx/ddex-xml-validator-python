"""DDEX驗證器常數定義"""

import re
from typing import Dict, Pattern

# DDEX版本
DDEX_VERSION_382 = "3.8.2"
DDEX_VERSION_41 = "4.1"

# 命名空間
DDEX_ERN_382_NAMESPACE = "http://ddex.net/xml/ern/382"
DDEX_ERN_41_NAMESPACE = "http://ddex.net/xml/ern/41"

# 訊息類型
MESSAGE_TYPES = {
    "NewReleaseMessage": "新發行訊息",
    "CatalogListMessage": "目錄清單訊息", 
    "PurgeReleaseMessage": "清除發行訊息"
}

# 正規表達式模式
PATTERNS: Dict[str, Pattern] = {
    "GRID": re.compile(r"^A1[A-Z0-9]{5}[A-Z0-9]{10}[A-Z0-9]$"),
    "ISRC": re.compile(r"^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$"),
    "ISAN": re.compile(r"^[A-F0-9]{12}$"),
    "VISAN": re.compile(r"^[A-F0-9]{24}$"),
    "ICPN": re.compile(r"^[0-9]{12,13}$"),
    "DURATION": re.compile(r"^PT(([0-9]+H)?([0-9]+M)?([0-9]+(\.[0-9]+)?S)?)$"),
    "DATE": re.compile(r"^[0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?$"),
    "DATETIME": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"),
    "TERRITORY": re.compile(r"^[A-Z]{2}$|^Worldwide$"),
    "LANGUAGE": re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
}

# 錯誤類型
ERROR_TYPES = {
    "SCHEMA_VALIDATION": "架構驗證錯誤",
    "BUSINESS_RULE": "業務規則錯誤", 
    "FORMAT_VALIDATION": "格式驗證錯誤",
    "IDENTIFIER_VALIDATION": "識別碼驗證錯誤",
    "REQUIRED_FIELD": "必填欄位錯誤"
}

# 嚴重程度
SEVERITY_LEVELS = {
    "ERROR": "錯誤",
    "WARNING": "警告",
    "INFO": "資訊"
}

