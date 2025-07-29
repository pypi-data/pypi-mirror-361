import sys
import os

sys.path.append(os.path.dirname(__file__))

__version__ = "25.3.0"

from .processor import DocumentProcessor
from .converters import WordConverter, PDFConverter, ExcelConverter, PowerPointConverter
from .factory import ConverterFactory
from .llm_strategy import SaveLocally, LLMFactory
from .license_manager import LicenseManager

__all__ = [
    'DocumentProcessor',
    'WordConverter',
    'PDFConverter',
    'ExcelConverter',
    'PowerPointConverter',
    'ConverterFactory',
    'SaveLocally',
    'LLMFactory',
    'LicenseManager',
]
