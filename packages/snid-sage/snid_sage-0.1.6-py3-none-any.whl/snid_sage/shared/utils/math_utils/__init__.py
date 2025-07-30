"""
Mathematical utility functions for SNID SAGE.

This module provides statistically rigorous weighted calculations including:
- Enhanced redshift estimation with cluster scatter (ChatGPT method)
- Enhanced age estimation with RLAP weighting and cluster scatter
- Legacy functions for backwards compatibility
- Weighted median calculation
- Statistical validation functions
"""

from .weighted_statistics import (
    calculate_hybrid_weighted_redshift,
    calculate_rlap_weighted_age,
    calculate_inverse_variance_weighted_redshift,
    calculate_weighted_median,
    validate_weighted_calculation
)

from .similarity_metrics import (
    cosine_similarity,
    compute_rlap_cos_metric,
    get_best_metric_value,
    get_metric_name_for_match,
    get_metric_display_values
)

__all__ = [
    'calculate_hybrid_weighted_redshift',
    'calculate_rlap_weighted_age',
    'calculate_inverse_variance_weighted_redshift',
    'calculate_weighted_median',
    'validate_weighted_calculation',
    'cosine_similarity',
    'compute_rlap_cos_metric',
    'get_best_metric_value',
    'get_metric_name_for_match',
    'get_metric_display_values'
] 