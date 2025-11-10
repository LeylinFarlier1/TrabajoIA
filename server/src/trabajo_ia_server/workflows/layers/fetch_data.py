"""
Fetch Data Layer - Obtain GDP data from FRED API.

Integrates with existing fred_client, cache, and rate_limiter infrastructure.
Handles computed variants, population fetching, and missing data gracefully.
"""
from __future__ import annotations

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from trabajo_ia_server.utils.fred_client import fred_client, FredAPIError
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.config import config
from trabajo_ia_server.workflows.utils.gdp_mappings import (
    get_series_id,
    GDP_VARIANT_DEPENDENCIES
)

logger = setup_logger(__name__)


@dataclass
class FetchResult:
    """Result from fetch_gdp_data layer."""
    data: Dict[str, Dict[str, pd.Series]]  # country -> variant -> Series
    metadata: Dict[str, Any]


def fetch_gdp_data(
    countries: List[str],
    variants: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    cache_ttl: Optional[int] = None
) -> FetchResult:
    """
    Fetch GDP data from FRED for multiple countries and variants.
    
    Args:
        countries: List of country codes (e.g., ["usa", "canada"])
        variants: List of GDP variant names
        start_date: Start date YYYY-MM-DD (optional)
        end_date: End date YYYY-MM-DD (optional)
        cache_ttl: Cache TTL in seconds (default: 86400 = 24h)
        Returns:
        FetchResult with data dict and metadata
    
    Workflow:
        1. Determine which series to fetch (direct + dependencies for computed)
        2. Fetch series from FRED with caching
        3. Compute derived variants (growth_rate, per_capita if needed)
        4. Return structured data with metadata
    """
    logger.info(f"Fetching GDP data: {len(countries)} countries, {len(variants)} variants")
    
    if cache_ttl is None:
        cache_ttl = 86400  # 24 hours default
    
    data: Dict[str, Dict[str, pd.Series]] = {country: {} for country in countries}
    metadata = {
        "fetched_series": [],
        "computed_variants": [],
        "missing_series": [],
        "errors": [],
        "source_series": {},
        "fetch_timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Step 1: Determine what to fetch
    series_to_fetch: Dict[str, Tuple[str, str]] = {}  # series_id -> (country, variant)
    computed_variants: Dict[str, List[str]] = {}  # variant -> source variants
    
    for country in countries:
        for variant in variants:
            # Check if variant is computed
            if variant in GDP_VARIANT_DEPENDENCIES:
                dep_info = GDP_VARIANT_DEPENDENCIES[variant]
                
                # IMPORTANT: Check if variant has direct fetch fallback
                if dep_info.get("fallback") == "fetch_direct":
                    # Try direct fetch first
                    series_id = get_series_id(country, variant)
                    if series_id:
                        # Direct series available - use it
                        series_to_fetch[f"{country}:{series_id}"] = (country, variant)
                        logger.debug(f"Using direct fetch for {country}/{variant}: {series_id}")
                        continue  # Skip computed logic
                    else:
                        # Direct not available - fall back to computation
                        logger.debug(f"Direct fetch not available for {country}/{variant}, will compute")
                
                # Compute from sources
                sources = dep_info["source"]
                if isinstance(sources, str):
                    sources = [sources]
                
                computed_variants[variant] = sources
                
                # Fetch source series
                for source_variant in sources:
                    series_id = get_series_id(country, source_variant)
                    if series_id:
                        series_to_fetch[f"{country}:{series_id}"] = (country, source_variant)
                    else:
                        logger.warning(f"Missing series for {country}/{source_variant}")
                        metadata["missing_series"].append(f"{country}/{source_variant}")
            else:
                # Direct fetch
                series_id = get_series_id(country, variant)
                if series_id:
                    series_to_fetch[f"{country}:{series_id}"] = (country, variant)
                else:
                    logger.warning(f"Missing series for {country}/{variant}")
                    metadata["missing_series"].append(f"{country}/{variant}")
    
    logger.info(f"Will fetch {len(series_to_fetch)} series from FRED")
    
    # Step 2: Fetch series from FRED (PARALLEL)
    def _fetch_single_series(
        key: str,
        country: str,
        variant: str,
        start_date: Optional[str],
        end_date: Optional[str],
        cache_ttl: int
    ) -> Tuple[str, str, Optional[pd.Series], Optional[str], Optional[Dict[str, Any]]]:
        """
        Fetch a single series from FRED.
        
        Returns:
            Tuple of (country, variant, series, series_id, error_dict)
        """
        series_id = get_series_id(country, variant)
        if not series_id:
            return (country, variant, None, None, None)
        
        try:
            # Use fred_client.get_json with observations endpoint
            api_key = config.get_fred_api_key()
            url = "https://api.stlouisfed.org/fred/series/observations"
            params: Dict[str, Any] = {
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json"
            }
            
            if start_date:
                params["observation_start"] = start_date
            if end_date:
                params["observation_end"] = end_date
            
            response = fred_client.get_json(
                url=url,
                params=params,
                namespace="gdp_series",
                ttl=cache_ttl
            )
            
            observations = response.payload.get("observations", [])
            
            if not observations:
                logger.warning(f"No data for {series_id} ({country}/{variant})")
                return (country, variant, None, series_id, None)
            
            # Convert to pandas Series
            dates = []
            values = []
            for obs in observations:
                date_str = obs.get("date")
                value_str = obs.get("value")
                
                if date_str and value_str and value_str != ".":
                    try:
                        dates.append(pd.to_datetime(date_str))
                        values.append(float(value_str))
                    except (ValueError, TypeError):
                        continue
            
            if dates:
                series = pd.Series(values, index=pd.DatetimeIndex(dates), name=variant)
                series = series.sort_index()
                logger.debug(f"Fetched {series_id}: {len(series)} observations")
                return (country, variant, series, series_id, None)
            else:
                logger.warning(f"No valid observations for {series_id}")
                return (country, variant, None, series_id, None)
        
        except FredAPIError as e:
            logger.error(f"FRED API error for {series_id}: {e.message}")
            return (country, variant, None, series_id, {
                "series_id": series_id,
                "country": country,
                "variant": variant,
                "error": e.message
            })
        except Exception as e:
            logger.error(f"Unexpected error fetching {series_id}: {str(e)}")
            return (country, variant, None, series_id, {
                "series_id": series_id,
                "country": country,
                "variant": variant,
                "error": str(e)
            })
    
    # Execute parallel fetches with ThreadPoolExecutor
    max_workers = min(10, len(series_to_fetch))  # Max 10 concurrent requests
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all fetch tasks (be defensive: ensure values are (country, variant))
        future_to_key = {}
        for key, val in series_to_fetch.items():
            try:
                country, variant = val
            except Exception:
                logger.error(f"Invalid series_to_fetch entry for {key}: {val}")
                metadata["errors"].append({"key": key, "value": val, "error": "invalid_entry"})
                continue

            future = executor.submit(
                _fetch_single_series,
                key,
                country,
                variant,
                start_date,
                end_date,
                cache_ttl
            )
            future_to_key[future] = key
        
        # Process completed fetches
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                country, variant, series, series_id, error = future.result()
                
                if error:
                    metadata["errors"].append(error)
                elif series is not None and series_id:
                    # Store in data structure
                    if country not in data:
                        data[country] = {}
                    data[country][variant] = series
                    
                    metadata["fetched_series"].append(series_id)
                    metadata["source_series"][f"{country}/{variant}"] = series_id
                elif series_id:
                    metadata["missing_series"].append(f"{country}/{variant}")
            
            except Exception as e:
                logger.error(f"Error processing future for {key}: {str(e)}")
    
    # Step 3: Compute derived variants
    for variant, sources in computed_variants.items():
        metadata["computed_variants"].append(variant)
        
        for country in countries:
            # Skip if already fetched directly
            if country in data and variant in data[country]:
                logger.debug(f"Skipping computation for {country}/{variant} - already fetched directly")
                continue
            
            try:
                if variant == "growth_rate":
                    # Compute from constant_2010
                    if "constant_2010" in data[country]:
                        gdp_series = data[country]["constant_2010"]
                        growth = gdp_series.pct_change() * 100  # Annual % change
                        growth = growth.dropna()
                        data[country]["growth_rate"] = growth
                        logger.debug(f"Computed growth_rate for {country}: {len(growth)} obs")
                    else:
                        logger.warning(f"Cannot compute growth_rate for {country}: missing constant_2010")
                
                elif variant.startswith("per_capita_"):
                    # Compute per capita variant
                    base_variant = variant.replace("per_capita_", "")
                    
                    # Check if we have both GDP and population
                    if base_variant in data[country] and "population" in data[country]:
                        gdp_series = data[country][base_variant]
                        pop_series = data[country]["population"]
                        
                        # Align dates
                        common_dates = gdp_series.index.intersection(pop_series.index)
                        if len(common_dates) > 0:
                            gdp_aligned = gdp_series.loc[common_dates]
                            pop_aligned = pop_series.loc[common_dates]
                            
                            # GDP is in billions, population is in units
                            # per_capita = (gdp_billions * 1e9) / population
                            per_capita = (gdp_aligned * 1e9) / pop_aligned
                            per_capita = per_capita.dropna()
                            
                            data[country][variant] = per_capita
                            logger.debug(f"Computed {variant} for {country}: {len(per_capita)} obs")
                        else:
                            logger.warning(f"No overlapping dates for {country}/{variant} computation")
                    else:
                        missing = []
                        if base_variant not in data[country]:
                            missing.append(base_variant)
                        if "population" not in data[country]:
                            missing.append("population")
                        logger.warning(f"Cannot compute {variant} for {country}: missing {missing}")
            
            except Exception as e:
                logger.error(f"Error computing {variant} for {country}: {str(e)}")
                metadata["errors"].append({
                    "country": country,
                    "variant": variant,
                    "error": f"Computation failed: {str(e)}"
                })
    
    # Summary stats
    total_series = sum(len(v) for v in data.values())
    logger.info(f"Fetch complete: {total_series} series, {len(metadata['missing_series'])} missing")
    
    return FetchResult(data=data, metadata=metadata)
