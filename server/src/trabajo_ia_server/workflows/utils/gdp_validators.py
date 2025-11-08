"""
GDP Validators - Input validation and variant dependency checking.

Validates user inputs and ensures variant dependencies are met before data fetching.
"""
from typing import List, Dict, Optional, Set
from datetime import datetime

from trabajo_ia_server.workflows.utils.gdp_mappings import (
    GDP_MAPPINGS,
    GDP_PRESETS,
    GDP_VARIANT_DEPENDENCIES,
    expand_preset,
    get_series_id
)


def validate_variants(
    requested_variants: List[str],
    countries: List[str],
    check_availability: bool = True
) -> Dict[str, any]:
    """
    Validate requested GDP variants and check dependencies.
    
    Args:
        requested_variants: List of GDP variants requested by user
        countries: List of country codes to check availability
        check_availability: Whether to check if series exist in mappings
    
    Returns:
        Dict with validation results:
        {
            "valid": List[str],  # Variants that can be used directly
            "computable": List[str],  # Variants that can be computed
            "missing_dependencies": Dict[str, List[str]],  # Variants with missing deps
            "warnings": List[str],  # Warning messages
            "needs_population": bool  # Whether population data is required
        }
    
    Examples:
        >>> validate_variants(["growth_rate"], ["usa"])
        {
            "valid": [],
            "computable": ["growth_rate"],
            "missing_dependencies": {},
            "warnings": ["growth_rate will be computed from constant_2010"],
            "needs_population": False
        }
        
        >>> validate_variants(["per_capita_constant"], ["usa"])
        {
            "valid": ["per_capita_constant"],
            "computable": [],
            "missing_dependencies": {},
            "warnings": [],
            "needs_population": False
        }
    """
    valid = []
    computable = []
    missing_dependencies: Dict[str, List[str]] = {}
    warnings = []
    required_sources: Set[str] = set()
    
    # Known variants
    all_variants = [
        "nominal_usd", "nominal_lcu", "constant_2010",
        "per_capita_nominal", "per_capita_constant", "per_capita_ppp",
        "growth_rate", "ppp_adjusted", "population"
    ]
    
    # Check for invalid variant names
    invalid_variants = [v for v in requested_variants if v not in all_variants]
    if invalid_variants:
        warnings.append(f"Unknown variants: {invalid_variants}")
    
    for variant in requested_variants:
        if variant not in all_variants:
            continue
            
        # Check if variant is computed
        if variant in GDP_VARIANT_DEPENDENCIES:
            dep_info = GDP_VARIANT_DEPENDENCIES[variant]
            sources = dep_info["source"]
            
            if isinstance(sources, str):
                sources = [sources]
            
            # Check if source variants are available
            missing_sources = []
            for source in sources:
                required_sources.add(source)
                
                # Check availability across countries if requested
                if check_availability:
                    unavailable_countries = []
                    for country in countries:
                        if not get_series_id(country, source):
                            unavailable_countries.append(country)
                    
                    if unavailable_countries:
                        missing_sources.append(
                            f"{source} (missing for: {', '.join(unavailable_countries[:3])}{'...' if len(unavailable_countries) > 3 else ''})"
                        )
            
            if missing_sources:
                missing_dependencies[variant] = missing_sources
                warnings.append(
                    f"Cannot compute {variant}: missing {', '.join(missing_sources)}"
                )
            else:
                computable.append(variant)
                if dep_info.get("fallback") == "fetch_direct":
                    warnings.append(
                        f"{variant} will try direct FRED fetch first, compute if unavailable"
                    )
                else:
                    warnings.append(
                        f"{variant} will be computed from {', '.join(sources)}"
                    )
        else:
            # Direct variant - check availability
            if check_availability:
                unavailable_countries = []
                for country in countries:
                    if not get_series_id(country, variant):
                        unavailable_countries.append(country)
                
                if unavailable_countries:
                    warnings.append(
                        f"{variant} not available for: {', '.join(unavailable_countries[:5])}{'...' if len(unavailable_countries) > 5 else ''}"
                    )
                    # Don't add to valid if unavailable for any country
                    continue
            
            valid.append(variant)
    
    # Determine if population is needed
    needs_population = (
        "population" in required_sources or
        "population" in requested_variants or
        any(v.startswith("per_capita_") for v in requested_variants)
    )
    
    return {
        "valid": valid,
        "computable": computable,
        "missing_dependencies": missing_dependencies,
        "warnings": warnings,
        "needs_population": needs_population,
        "required_sources": list(required_sources)
    }


def validate_countries(countries: str | List[str]) -> Dict[str, any]:
    """
    Validate and expand country inputs.
    
    Args:
        countries: Country code(s) or preset name(s)
    
    Returns:
        Dict with:
        {
            "expanded": List[str],  # Expanded country codes
            "invalid": List[str],   # Unknown countries/presets
            "warnings": List[str]
        }
    
    Examples:
        >>> validate_countries("g7")
        {"expanded": ["usa", "canada", ...], "invalid": [], "warnings": []}
        
        >>> validate_countries(["usa", "invalid_country"])
        {"expanded": ["usa"], "invalid": ["invalid_country"], "warnings": [...]}
    """
    expanded = expand_preset(countries)
    available_countries = set(GDP_MAPPINGS.keys())
    
    valid_countries = [c for c in expanded if c in available_countries]
    invalid_countries = [c for c in expanded if c not in available_countries]
    
    warnings = []
    if invalid_countries:
        warnings.append(
            f"Unknown countries (will be skipped): {', '.join(invalid_countries)}"
        )
    
    if not valid_countries:
        warnings.append("No valid countries after validation")
    
    return {
        "expanded": valid_countries,
        "invalid": invalid_countries,
        "warnings": warnings
    }


def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> Dict[str, any]:
    """
    Validate date range inputs.
    
    Args:
        start_date: Start date (YYYY-MM-DD) or None
        end_date: End date (YYYY-MM-DD) or None
    
    Returns:
        Dict with:
        {
            "start_parsed": datetime | None,
            "end_parsed": datetime | None,
            "valid": bool,
            "warnings": List[str]
        }
    """
    warnings = []
    start_parsed = None
    end_parsed = None
    valid = True
    
    if start_date:
        try:
            start_parsed = datetime.strptime(start_date, "%Y-%m-%d")
            if start_parsed.year < 1960:
                warnings.append("start_date before 1960 - limited data availability")
        except ValueError:
            warnings.append(f"Invalid start_date format: {start_date} (expected YYYY-MM-DD)")
            valid = False
    
    if end_date:
        try:
            end_parsed = datetime.strptime(end_date, "%Y-%m-%d")
            if end_parsed > datetime.now():
                warnings.append("end_date is in the future - will use latest available")
        except ValueError:
            warnings.append(f"Invalid end_date format: {end_date} (expected YYYY-MM-DD)")
            valid = False
    
    if start_parsed and end_parsed and start_parsed >= end_parsed:
        warnings.append("start_date must be before end_date")
        valid = False
    
    return {
        "start_parsed": start_parsed,
        "end_parsed": end_parsed,
        "valid": valid,
        "warnings": warnings
    }


def validate_comparison_mode(mode: str) -> Dict[str, any]:
    """Validate comparison mode parameter."""
    valid_modes = ["absolute", "indexed", "per_capita", "growth_rates", "ppp", "relative_to_benchmark"]
    
    if mode not in valid_modes:
        return {
            "valid": False,
            "warnings": [f"Invalid comparison_mode: {mode}. Valid options: {', '.join(valid_modes)}"]
        }
    
    return {"valid": True, "warnings": []}


def validate_output_format(format: str) -> Dict[str, any]:
    """Validate output format parameter."""
    valid_formats = ["analysis", "dataset", "summary", "both"]
    
    if format not in valid_formats:
        return {
            "valid": False,
            "warnings": [f"Invalid output_format: {format}. Valid options: {', '.join(valid_formats)}"]
        }
    
    return {"valid": True, "warnings": []}


def validate_all_inputs(
    countries: str | List[str],
    gdp_variants: Optional[List[str]],
    start_date: Optional[str],
    end_date: Optional[str],
    comparison_mode: str,
    output_format: str,
    base_year: Optional[int],
    validate_variants_flag: bool
) -> Dict[str, any]:
    """
    Comprehensive input validation.
    
    Args:
        countries: Country codes or preset
        gdp_variants: GDP variants to analyze
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        comparison_mode: Comparison mode
        output_format: Output format
        base_year: Base year for indexed mode
        validate_variants_flag: Whether to validate variants
    
    Returns:
        Dict with:
        {
            "valid": bool,
            "countries": List[str],
            "variants": List[str],
            "warnings": List[str],
            "errors": List[str],
            "validation_details": Dict
        }
    
    Raises:
        ValueError: If critical validation fails
    """
    all_warnings = []
    all_errors = []
    
    # Validate countries
    country_validation = validate_countries(countries)
    validated_countries = country_validation["expanded"]
    all_warnings.extend(country_validation["warnings"])
    
    if not validated_countries:
        all_errors.append("No valid countries provided")
        raise ValueError("No valid countries provided")
    
    # Default variants if None
    if gdp_variants is None:
        gdp_variants = ["per_capita_constant"]  # Most common/available
        all_warnings.append("No variants specified, using default: per_capita_constant")
    
    # Validate variants
    variant_validation = {"valid": gdp_variants, "computable": [], "warnings": []}
    if validate_variants_flag:
        variant_validation = validate_variants(
            gdp_variants,
            validated_countries,
            check_availability=True
        )
        all_warnings.extend(variant_validation["warnings"])
        
        if variant_validation["missing_dependencies"]:
            all_errors.append(
                f"Missing dependencies: {variant_validation['missing_dependencies']}"
            )
    
    # Validate date range
    date_validation = validate_date_range(start_date, end_date)
    all_warnings.extend(date_validation["warnings"])
    if not date_validation["valid"]:
        all_errors.append("Invalid date range")
    
    # Validate comparison mode
    mode_validation = validate_comparison_mode(comparison_mode)
    all_warnings.extend(mode_validation["warnings"])
    if not mode_validation["valid"]:
        all_errors.append("Invalid comparison_mode")
    
    # Validate output format
    format_validation = validate_output_format(output_format)
    all_warnings.extend(format_validation["warnings"])
    if not format_validation["valid"]:
        all_errors.append("Invalid output_format")
    
    # Validate base_year if indexed mode
    if comparison_mode == "indexed" and base_year is None:
        all_warnings.append("indexed mode requires base_year - will use start_date year")
    
    # Check for conflicting parameters
    if comparison_mode == "ppp" and not any("ppp" in v for v in gdp_variants):
        all_warnings.append("ppp comparison mode but no PPP variants requested")
    
    return {
        "valid": len(all_errors) == 0,
        "countries": validated_countries,
        "variants": gdp_variants,
        "warnings": all_warnings,
        "errors": all_errors,
        "validation_details": {
            "country_validation": country_validation,
            "variant_validation": variant_validation,
            "date_validation": date_validation,
            "mode_validation": mode_validation,
            "format_validation": format_validation
        }
    }
