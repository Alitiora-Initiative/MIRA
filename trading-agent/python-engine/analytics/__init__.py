"""
Analytics module for advanced statistical modeling and portfolio optimization
"""

from .julia_client import JuliaAnalyticsClient
from .r_client import RAnalyticsClient

__all__ = ['JuliaAnalyticsClient', 'RAnalyticsClient']
