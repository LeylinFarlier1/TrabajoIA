"""
Analyze GDP Cross-Country - Main workflow implementation.

Complete GDP analysis tool with 3-layer architecture:
- fetch_data_layer: FRED/World Bank data retrieval
- analysis_layer: Economic analysis (convergence, breaks, rankings)
- format_layer: Output formatting (JSON, tidy dataset, summary)
"""
import json
from typing import Dict, List, Optional, Union
from datetime import datetime

from trabajo_ia_server.config import config, ConfigError
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.workflows.utils.gdp_mappings import expand_preset
from trabajo_ia_server.workflows.utils.gdp_validators import validate_all_inputs
from trabajo_ia_server.workflows.layers.fetch_data import fetch_gdp_data
from trabajo_ia_server.workflows.layers.analyze_data import analyze_gdp_data
from trabajo_ia_server.workflows.layers.format_output import (
    format_analysis,
    format_dataset,
    format_summary,
    format_both,
)

logger = setup_logger(__name__)


def analyze_gdp_cross_country(
    # === PAÍSES ===
    countries: Union[List[str], str],
    
    # === QUÉ ANALIZAR ===
    gdp_variants: Optional[List[str]] = None,
    include_population: bool = True,
    
    # === PERÍODO ===
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period_split: Optional[str] = None,
    
    # === MODO DE COMPARACIÓN ===
    comparison_mode: str = "absolute",
    base_year: Optional[int] = None,
    
    # === ANÁLISIS ===
    include_rankings: bool = True,
    include_convergence: bool = True,
    include_growth_analysis: bool = True,
    calculate_productivity: bool = False,
    detect_structural_breaks: bool = True,
    
    # === OUTPUT ===
    output_format: str = "analysis",
    frequency: str = "annual",
    
    # === TÉCNICO ===
    fill_missing: str = "interpolate",
    align_method: str = "inner",
    benchmark_against: Optional[str] = None,
    validate_variants: bool = True
) -> str:
    """
    Analyze GDP across countries with deep economic analysis.
    
    MCP-compatible tool that returns comprehensive JSON with rankings,
    convergence analysis, structural breaks, volatility metrics, and datasets.
    
    Args:
        countries: Country code(s) or preset name ("g7", "latam", etc.)
        gdp_variants: GDP variants to analyze (default: ["per_capita_constant"])
            Options: "nominal_usd", "constant_2010", "per_capita_constant",
                     "per_capita_ppp", "growth_rate", "ppp_adjusted"
        include_population: Include population data (required for per_capita)
        start_date: Start date YYYY-MM-DD (default: "1960-01-01")
        end_date: End date YYYY-MM-DD (default: latest available)
        period_split: Split analysis by periods ("decade", "5y", None)
        comparison_mode: "absolute", "indexed", "per_capita", "growth_rates", "ppp"
        base_year: Base year for indexed mode
        include_rankings: Include country rankings
        include_convergence: Compute sigma/beta convergence
        include_growth_analysis: CAGR, volatility, stability_index
        calculate_productivity: GDP per hour worked (requires labor data)
        detect_structural_breaks: Chow test + rolling variance
        output_format: "analysis" (JSON), "dataset" (tidy), "summary", "both"
        frequency: "annual" or "quarterly"
        fill_missing: "interpolate", "forward", "drop"
        align_method: "inner" or "outer"
        benchmark_against: "usa", "world", "oecd_avg", None
        validate_variants: Validate variant dependencies before fetch
    
    Returns:
        JSON string with analysis results and metadata (MCP-compatible)
    
    Examples:
        >>> analyze_gdp_cross_country(["g7"], ["per_capita_constant"])
        >>> analyze_gdp_cross_country("latam", output_format="both")
        >>> analyze_gdp_cross_country(
        ...     ["usa", "china"], 
        ...     ["per_capita_constant", "growth_rate"],
        ...     start_date="2000-01-01",
        ...     detect_structural_breaks=True
        ... )
    """
    start_time = datetime.utcnow()
    
    try:
        # === PHASE 0: VALIDATE FRED API KEY ===
        try:
            config.get_fred_api_key()
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            return json.dumps({
                "tool": "analyze_gdp_cross_country",
                "error": "FRED_API_KEY_MISSING",
                "error_message": str(e),
                "metadata": {
                    "fetch_timestamp": start_time.isoformat() + "Z"
                }
            }, separators=(",", ":"))
        
        logger.info(
            f"GDP Analysis Request: countries={countries}, "
            f"variants={gdp_variants}, format={output_format}"
        )
        
        # === PHASE 1: INPUT VALIDATION ===
        validation_result = validate_all_inputs(
            countries=countries,
            gdp_variants=gdp_variants,
            start_date=start_date,
            end_date=end_date,
            comparison_mode=comparison_mode,
            output_format=output_format,
            base_year=base_year,
            validate_variants_flag=validate_variants
        )
        
        if not validation_result["valid"]:
            logger.error(f"Validation failed: {validation_result['errors']}")
            return json.dumps({
                "tool": "analyze_gdp_cross_country",
                "error": "Input validation failed",
                "validation_errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
                "metadata": {
                    "fetch_timestamp": start_time.isoformat() + "Z"
                }
            }, separators=(",", ":"))
        
        validated_countries = validation_result["countries"]
        validated_variants = validation_result["variants"]
        
        logger.info(
            f"Validation passed: {len(validated_countries)} countries, "
            f"{len(validated_variants)} variants"
        )
        
        # Log warnings
        for warning in validation_result["warnings"]:
            logger.warning(f"Validation warning: {warning}")
        
        # === PHASE 2: FETCH DATA (Layer 1) ===
        logger.info("Starting fetch_data_layer...")
        
        fetch_result = fetch_gdp_data(
            countries=validated_countries,
            variants=validated_variants,
            start_date=start_date or "1960-01-01",
            end_date=end_date,
            cache_ttl=86400  # Default 24h
        )
        
        logger.info(
            f"Fetch complete: {len(fetch_result.metadata['fetched_series'])} series, "
            f"{len(fetch_result.metadata['missing_series'])} missing"
        )
        
        # === CHECK: Early-exit if no data fetched ===
        if not fetch_result.data or all(not country_data for country_data in fetch_result.data.values()):
            logger.error("No data fetched for any country/variant")
            return json.dumps({
                "tool": "analyze_gdp_cross_country",
                "error": "NO_DATA_FETCHED",
                "error_message": "Could not fetch any data from FRED for the requested countries/variants",
                "details": {
                    "requested_countries": validated_countries,
                    "requested_variants": validated_variants,
                    "missing_series": fetch_result.metadata["missing_series"],
                    "errors": fetch_result.metadata["errors"]
                },
                "metadata": {
                    "fetch_timestamp": start_time.isoformat() + "Z",
                    "fetched_series_count": len(fetch_result.metadata["fetched_series"])
                }
            }, separators=(",", ":"))
        
        # === PHASE 3: ANALYSIS (Layer 2) ===
        logger.info("Starting analysis_layer...")
        
        analysis_result = analyze_gdp_data(
            data=fetch_result.data,
            variants=validated_variants,
            start_date=start_date,
            end_date=end_date,
            compute_convergence=include_convergence,
            detect_structural_breaks=detect_structural_breaks,
            include_rankings=include_rankings,
            include_growth_metrics=include_growth_analysis,
            comparison_mode=comparison_mode
        )
        
        logger.info("Analysis complete")
        
        # === PHASE 4: FORMAT OUTPUT (Layer 3) ===
        logger.info(f"Formatting output: format={output_format}")
        
        # Route to appropriate formatter
        format_metadata = {
            "observation_start": start_date or "1960-01-01",
            "observation_end": end_date or "latest",
            "variants_requested": validated_variants,
            "series_fetched": len(fetch_result.metadata["fetched_series"]),
            "series_missing": len(fetch_result.metadata["missing_series"]),
            "computed_variants": fetch_result.metadata["computed_variants"],
        }
        
        if output_format == "analysis":
            # AI-optimized compact JSON (DEFAULT)
            format_result = format_analysis(analysis_result, format_metadata)
        elif output_format == "dataset":
            # Tidy DataFrame format
            format_result = format_dataset(
                analysis_result, 
                format_metadata, 
                fetch_result.data
            )
        elif output_format == "summary":
            # Human-readable markdown
            format_result = format_summary(analysis_result, format_metadata)
        elif output_format == "both":
            # Analysis + Dataset combined
            format_result = format_both(
                analysis_result,
                format_metadata,
                fetch_result.data
            )
        else:
            # Fallback to analysis format
            logger.warning(f"Unknown format '{output_format}', using 'analysis'")
            format_result = format_analysis(analysis_result, format_metadata)
        
        end_time = datetime.utcnow()
        elapsed = (end_time - start_time).total_seconds()
        
        logger.info(
            f"GDP analysis completed in {elapsed:.2f}s "
            f"(format: {format_result.format_type})"
        )
        
        # Return formatted output (already JSON string for MCP)
        return format_result.output
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return json.dumps({
            "tool": "analyze_gdp_cross_country",
            "error": f"Invalid input: {str(e)}",
            "input_parameters": {
                "countries": countries,
                "gdp_variants": gdp_variants,
                "start_date": start_date,
                "end_date": end_date
            },
            "metadata": {
                "fetch_timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }, separators=(",", ":"))
        
    except Exception as e:
        logger.error(f"Unexpected error in GDP analysis: {e}", exc_info=True)
        return json.dumps({
            "tool": "analyze_gdp_cross_country",
            "error": f"Internal error: {str(e)}",
            "metadata": {
                "fetch_timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }, separators=(",", ":"))
