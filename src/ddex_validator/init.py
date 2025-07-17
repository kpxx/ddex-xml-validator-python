"""DDEX XML驗證器套件"""

__version__ = "1.0.0"
__author__ = "DDEX Validator Team"
__description__ = "A comprehensive XML validator for DDEX messages"

from .validator import DDEXXMLValidator
from .models import ValidationResult, ValidationIssue, SeverityLevel
from .rules import DDEXBusinessRules

__all__ = [
    'DDEXXMLValidator',
    'ValidationResult', 
    'ValidationIssue',
    'SeverityLevel',
    'DDEXBusinessRules'
]

