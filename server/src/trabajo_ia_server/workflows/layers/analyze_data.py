"""
Analysis Layer - Perform GDP analysis calculations.

Includes growth metrics, convergence tests, structural breaks, rankings.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from scipy import stats

from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class AnalysisResult:
    """Result from analyze_gdp_data layer."""
    by_country: Dict[str, Dict[str, Any]]  # country -> metrics
    cross_country: Dict[str, Any]  # cross-country analysis
    rankings: Dict[str, List[Tuple[str, float]]]  # rankings by different criteria
    metadata: Dict[str, Any]


def _apply_indexed_transformation(
    data: Dict[str, Dict[str, pd.Series]],
    variants: List[str],
    base_year: int
) -> Dict[str, Dict[str, pd.Series]]:
    """
    Transform data to indexed values (base_year = 100).
    
    Args:
        data: Dict[country][variant] = pd.Series
        variants: Variants to transform
        base_year: Year to use as base (value = 100)
    
    Returns:
        Transformed data with indexed values
    """
    indexed_data = {}
    
    for country, country_data in data.items():
        indexed_data[country] = {}
        
        for variant in variants:
            if variant not in country_data:
                continue
            
            series = country_data[variant]
            
            # Find base year value
            base_year_date = pd.Timestamp(f"{base_year}-01-01")
            
            if base_year_date not in series.index:
                # Try to find closest year
                year_values = series[series.index.year == base_year]
                if len(year_values) > 0:
                    base_value = year_values.iloc[0]
                else:
                    logger.warning(f"Base year {base_year} not found for {country}/{variant}, skipping indexed transformation")
                    indexed_data[country][variant] = series
                    continue
            else:
                base_value = series[base_year_date]
            
            if base_value == 0 or pd.isna(base_value):
                logger.warning(f"Base year value is 0 or NaN for {country}/{variant}, skipping indexed transformation")
                indexed_data[country][variant] = series
                continue
            
            # Transform to index (base = 100)
            indexed_series = (series / base_value) * 100
            indexed_data[country][variant] = indexed_series
            logger.debug(f"Indexed {country}/{variant} to base_year={base_year} (base_value={base_value:.2f})")
    
    return indexed_data


def analyze_gdp_data(
    data: Dict[str, Dict[str, pd.Series]],
    variants: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    compute_convergence: bool = False,
    detect_structural_breaks: bool = False,
    include_rankings: bool = False,
    include_growth_metrics: bool = False,
    comparison_mode: str = "absolute",
    base_year: Optional[int] = None
) -> AnalysisResult:
    """
    Analyze GDP data across countries.
    
    Args:
        data: Dict[country][variant] = pd.Series
        variants: List of variants to analyze
        start_date: Optional date filter
        end_date: Optional date filter
        compute_convergence: Whether to compute sigma/beta convergence
        detect_structural_breaks: Whether to detect structural breaks
        include_rankings: Whether to compute rankings
        include_growth_metrics: Whether to compute growth metrics
        comparison_mode: Analysis mode ("absolute", "indexed", "growth_rates", "ppp")
        base_year: Base year for indexed mode (required if comparison_mode="indexed")
    
    Returns:
        AnalysisResult with by_country and cross_country analysis
    """
    logger.info(f"Analyzing GDP data: {len(data)} countries, {len(variants)} variants")
    
    # Calculate period years if dates provided
    period_years = None
    if start_date and end_date:
        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if isinstance(start_date, str) else start_date
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if isinstance(end_date, str) else end_date
            period_years = round((end_dt - start_dt).days / 365.25, 1)
        except:
            period_years = None
    
    # Apply comparison mode transformation
    if comparison_mode == "indexed" and base_year is not None:
        logger.info(f"Applying indexed transformation with base_year={base_year}")
        data = _apply_indexed_transformation(data, variants, base_year)
    
    by_country: Dict[str, Dict[str, Any]] = {}
    cross_country: Dict[str, Any] = {}
    rankings: Dict[str, List[Tuple[str, float]]] = {}
    metadata: Dict[str, Any] = {
        "countries_analyzed": list(data.keys()),
        "variants_analyzed": variants,
        "period_years": period_years,
        "analysis_flags": {
            "convergence": compute_convergence,
            "structural_breaks": detect_structural_breaks,
            "rankings": include_rankings,
            "growth_metrics": include_growth_metrics
        }
    }
    
    # Analyze each country
    for country, country_data in data.items():
        by_country[country] = {}
        
        for variant in variants:
            if variant not in country_data:
                logger.warning(f"Variant {variant} not available for {country}")
                continue
            
            series = country_data[variant]
            
            # Skip if series is None or empty
            if series is None or len(series) == 0:
                logger.warning(f"Empty or None series for {country} - {variant}")
                continue
            
            # Basic stats
            by_country[country][variant] = {
                "observations": len(series),
                "first_date": series.index[0].strftime("%Y-%m-%d"),
                "last_date": series.index[-1].strftime("%Y-%m-%d"),
                "latest_value": float(series.iloc[-1]),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max())
            }
            
            # Growth metrics
            if include_growth_metrics and len(series) > 1:
                by_country[country][variant]["growth_metrics"] = _compute_growth_metrics(series, variant)
            
            # Structural breaks
            if detect_structural_breaks and len(series) > 20:
                by_country[country][variant]["structural_breaks"] = _detect_structural_breaks(series)
    
    # Cross-country analysis
    if len(data) > 1:
        for variant in variants:
            # Collect latest values for all countries
            latest_values = {}
            all_series = {}
            
            for country, country_data in data.items():
                if variant in country_data:
                    series = country_data[variant]
                    if len(series) > 0:
                        latest_values[country] = float(series.iloc[-1])
                        all_series[country] = series
            
            if len(latest_values) < 2:
                continue
            
            # Initialize cross_country dict for variant
            if variant not in cross_country:
                cross_country[variant] = {}
            
            # Basic cross-country stats
            values_list = list(latest_values.values())
            cross_country[variant]["latest_snapshot"] = {
                "mean": float(np.mean(values_list)),
                "median": float(np.median(values_list)),
                "std": float(np.std(values_list)),
                "min": float(np.min(values_list)),
                "max": float(np.max(values_list)),
                "coefficient_of_variation": float(np.std(values_list) / np.mean(values_list)) if np.mean(values_list) != 0 else None
            }
            
            # Rankings
            if include_rankings:
                sorted_countries = sorted(latest_values.items(), key=lambda x: x[1], reverse=True)
                rankings[f"{variant}_level"] = sorted_countries
                
                # Growth rankings if we have growth_rate
                if variant == "growth_rate" or include_growth_metrics:
                    growth_ranks = {}
                    for country, series in all_series.items():
                        if len(series) > 1:
                            cagr = _compute_cagr(series)
                            if cagr is not None:
                                growth_ranks[country] = cagr
                    
                    if growth_ranks:
                        # Filter out None values before sorting
                        valid_growth = {k: v for k, v in growth_ranks.items() if v is not None}
                        if valid_growth:
                            sorted_growth = sorted(valid_growth.items(), key=lambda x: x[1], reverse=True)
                            rankings[f"{variant}_growth"] = sorted_growth
            
            # Convergence analysis
            if compute_convergence and len(all_series) > 2:
                cross_country[variant]["convergence"] = _compute_convergence(all_series)
    
    logger.info(f"Analysis complete: {len(by_country)} countries analyzed")
    
    return AnalysisResult(
        by_country=by_country,
        cross_country=cross_country,
        rankings=rankings,
        metadata=metadata
    )


def _compute_growth_metrics(series: pd.Series, variant: str = None) -> Dict[str, Any]:
    """Compute growth metrics for a time series."""
    if len(series) < 2:
        return {}
    
    # Skip CAGR for growth_rate variant (CAGR of growth rates doesn't make sense)
    cagr = None if variant == "growth_rate" else _compute_cagr(series)
    
    # Year-over-year growth
    yoy_growth = series.pct_change() * 100
    
    # Volatility
    volatility = float(yoy_growth.std()) if len(yoy_growth) > 1 else None
    
    # Stability index (1 / (1 + volatility))
    stability_index = 1 / (1 + volatility) if volatility is not None else None
    
    return {
        "cagr": cagr,
        "volatility": volatility,
        "stability_index": stability_index,
        "total_growth_pct": float(((series.iloc[-1] / series.iloc[0]) - 1) * 100) if series.iloc[0] != 0 else None
    }


def _compute_cagr(series: pd.Series) -> Optional[float]:
    """Compute Compound Annual Growth Rate."""
    if len(series) < 2:
        return None
    
    start_value = series.iloc[0]
    end_value = series.iloc[-1]
    
    if start_value <= 0 or end_value <= 0:
        return None
    
    # Calculate years between first and last observation
    years = (series.index[-1] - series.index[0]).days / 365.25
    
    if years <= 0:
        return None
    
    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
    return float(cagr)


def _detect_structural_breaks(series: pd.Series, threshold: float = 0.05) -> List[Dict[str, Any]]:
    """
    Detect structural breaks using rolling variance method.
    
    For MVP, use simple rolling variance. Full Chow test requires statsmodels.
    """
    if len(series) < 20:
        return []
    
    breaks = []
    
    # Rolling variance with 12-observation window
    window = min(12, len(series) // 3)
    rolling_var = series.rolling(window=window).var()
    rolling_var = rolling_var.dropna()
    
    if len(rolling_var) < 2:
        return breaks
    
    # Detect when variance doubles or halves
    for i in range(1, len(rolling_var)):
        if rolling_var.iloc[i] > 2 * rolling_var.iloc[i-1]:
            breaks.append({
                "date": rolling_var.index[i].strftime("%Y-%m-%d"),
                "type": "variance_increase",
                "ratio": float(rolling_var.iloc[i] / rolling_var.iloc[i-1])
            })
        elif rolling_var.iloc[i] < 0.5 * rolling_var.iloc[i-1]:
            breaks.append({
                "date": rolling_var.index[i].strftime("%Y-%m-%d"),
                "type": "variance_decrease",
                "ratio": float(rolling_var.iloc[i] / rolling_var.iloc[i-1])
            })
    
    logger.debug(f"Detected {len(breaks)} potential structural breaks")
    return breaks[:5]  # Limit to top 5


def _compute_convergence(all_series: Dict[str, pd.Series]) -> Dict[str, Any]:
    """
    Compute sigma and beta convergence.
    
    Sigma convergence: dispersion decreasing over time
    Beta convergence: poor countries grow faster than rich
    """
    result = {}
    
    # Sigma convergence: coefficient of variation over time
    common_dates = None
    for series in all_series.values():
        if common_dates is None:
            common_dates = set(series.index)
        else:
            common_dates = common_dates.intersection(series.index)
    
    if not common_dates or len(common_dates) < 5:  # Reduced from 10 to 5
        logger.warning(f"Convergence: insufficient dates. Common dates: {len(common_dates) if common_dates else 0}")
        return {"sigma": None, "beta": None, "note": "Insufficient overlapping data"}
    
    common_dates = sorted(list(common_dates))
    logger.info(f"Convergence: {len(common_dates)} common dates across {len(all_series)} series")
    
    # Calculate CV at each time point
    cvs = []
    for date in common_dates:
        values = [series.loc[date] for series in all_series.values() if date in series.index]
        if len(values) > 1:
            mean_val = np.mean(values)
            if mean_val != 0:
                cv = np.std(values) / mean_val
                cvs.append(cv)
    
    logger.info(f"Convergence: calculated {len(cvs)} CVs from {len(common_dates)} dates")
    
    if len(cvs) > 1:
        # Linear regression of CV over time
        x = np.arange(len(cvs))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, cvs)
        
        result["sigma"] = {
            "slope": float(slope),  # Changed from trend_slope to match format layer
            "r_squared": float(r_value ** 2),
            "p_value": float(p_value),
            "trend": "converging" if slope < 0 else "diverging",  # Added for format layer
            "significant": p_value < 0.05  # Changed from significance string to boolean
        }
    else:
        result["sigma"] = None
    
    # Beta convergence: initial level vs growth rate
    initial_values = []
    growth_rates = []
    
    for country, series in all_series.items():
        if len(series) > 1:
            initial = series.iloc[0]
            cagr = _compute_cagr(series)
            
            if initial > 0 and cagr is not None:
                initial_values.append(np.log(initial))  # Log of initial value
                growth_rates.append(cagr)
    
    if len(initial_values) > 2:
        # Regress growth on initial value
        slope, intercept, r_value, p_value, std_err = stats.linregress(initial_values, growth_rates)
        
        result["beta"] = {
            "coefficient": float(slope),
            "r_squared": float(r_value ** 2),
            "p_value": float(p_value),
            "interpretation": "catch-up growth" if slope < 0 else "no catch-up",  # Changed for format layer
            "significant": p_value < 0.05  # Changed to boolean
        }
    else:
        result["beta"] = None
    
    return result
