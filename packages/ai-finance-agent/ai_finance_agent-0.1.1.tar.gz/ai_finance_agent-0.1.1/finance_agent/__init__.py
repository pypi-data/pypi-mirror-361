"""
Finance Agent - An agentic AI library for receipt processing and financial data extraction.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .agent import FinanceAgent
from .models import ReceiptData, ExtractionResult, ReceiptItem, ItemCategory
from .ocr_processor import OCRProcessor
from .exceptions import FinanceAgentError, OCRProcessingError, LLMExtractionError

__all__ = [
    "FinanceAgent",
    "ReceiptData",
    "ExtractionResult",
    "ReceiptItem",
    "ItemCategory",
    "OCRProcessor",
    "FinanceAgentError",
    "OCRProcessingError",
    "LLMExtractionError"
]

