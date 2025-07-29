"""
Yield Analysis SDK

A Python SDK for analyzing DeFi vault performance and yield metrics.
"""

__version__ = "0.1.0"
__author__ = "Logarithm Labs"
__email__ = "dev@logarithm.fi"

from .acp import (
    extract_analysis_request,
    extract_analysis_response,
    extract_vault_registration_request,
    extract_vault_registration_response,
)
from .analysis import analyze_yield_with_daily_share_price
from .exceptions import (
    ConfigurationError,
    ConnectionError,
    DataError,
    ValidationError,
    YieldAnalysisError,
)
from .subgraph import get_daily_share_price_history_from_subgraph

# Import main classes and functions for public API
from .type import (
    AnalysisRequest,
    AnalysisResponse,
    AuditStatus,
    Chain,
    PerformanceAnalysis,
    SharePriceHistory,
    StrategyType,
    VaultInfo,
    VaultPerformanceAnalysis,
    VaultRegistrationRequest,
    VaultRegistrationResponse,
)
from .validators import normalize_address

__all__ = [
    # Types and enums
    "Chain",
    "StrategyType",
    "AuditStatus",
    "AnalysisRequest",
    "VaultInfo",
    "PerformanceAnalysis",
    "VaultPerformanceAnalysis",
    "AnalysisResponse",
    "SharePriceHistory",
    "VaultRegistrationRequest",
    "VaultRegistrationResponse",
    # Main functions
    "get_daily_share_price_history_from_subgraph",
    "analyze_yield_with_daily_share_price",
    "extract_analysis_request",
    "extract_analysis_response",
    "extract_vault_registration_request",
    "extract_vault_registration_response",
    "normalize_address",
    # Exceptions
    "YieldAnalysisError",
    "DataError",
    "ConfigurationError",
    "ConnectionError",
    "ValidationError",
]
