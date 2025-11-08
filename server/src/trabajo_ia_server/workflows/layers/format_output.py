"""
Format Layer for GDP Analysis Tool

Transforms analysis results into different output formats optimized for various use cases.
Default format ('analysis') is AI-optimized for token efficiency and interpretability.

Output Formats:
    - 'analysis': Compact JSON, AI-optimized (DEFAULT)
    - 'dataset': Tidy DataFrame format for further analysis
    - 'summary': Markdown report for human reading
    - 'both': Combines 'analysis' + serialized 'dataset'

Author: GDP Analysis Tool v1.0.0
Date: 2025-11-05
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd
from datetime import datetime

from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class FormatResult:
    """Result from format layer."""
    output: str  # JSON string for MCP compatibility
    format_type: str
    metadata: Dict[str, Any]


def format_analysis(
    analysis_result: Any,
    fetch_metadata: Dict[str, Any]
) -> FormatResult:
    """
    Format as compact JSON optimized for AI consumption (DEFAULT).
    
    This is the recommended format for LLM interaction:
    - Minimal token usage
    - Clear hierarchical structure
    - Essential metadata only
    - No redundant information
    - Direct numerical values (no verbose descriptions)
    
    Args:
        analysis_result: AnalysisResult from analysis layer
        fetch_metadata: Metadata from fetch layer
    
    Returns:
        FormatResult with compact JSON output
    """
    logger.info("Formatting output: analysis (AI-optimized)")
    
    # Extract data from analysis result
    by_country = analysis_result.by_country
    cross_country = analysis_result.cross_country
    rankings = analysis_result.rankings
    analysis_metadata = analysis_result.metadata
    
    # Build compact structure
    output = {
        "tool": "analyze_gdp_cross_country",
        "results": {
            "countries": {},
            "cross_country": {},
            "rankings": {}
        },
        "metadata": {
            "period": {
                "start": fetch_metadata.get("observation_start"),
                "end": fetch_metadata.get("observation_end"),
                "years": analysis_metadata.get("period_years")
            },
            "coverage": {
                "countries": analysis_metadata.get("countries_analyzed"),
                "variants": fetch_metadata.get("variants_requested"),
                "series_fetched": fetch_metadata.get("series_fetched"),
                "series_missing": fetch_metadata.get("series_missing")
            },
            "computed_variants": fetch_metadata.get("computed_variants", []),
            "limitations": _get_limitations(analysis_metadata)
        }
    }
    
    # Format country-level results (compact)
    for country, variants_data in by_country.items():
        country_data = {}
        
        # Iterate over variants for this country
        for variant, data in variants_data.items():
            variant_data = {}
            
            # Growth metrics
            if "growth_metrics" in data:
                metrics = data["growth_metrics"]
                variant_data["growth"] = {
                    "cagr_pct": round(metrics.get("cagr", 0), 2) if metrics.get("cagr") is not None else None,
                    "volatility": round(metrics.get("volatility", 0), 2) if metrics.get("volatility") is not None else None,
                    "stability_index": round(metrics.get("stability_index", 0), 3) if metrics.get("stability_index") is not None else None
                }
            
            # Structural breaks (if detected)
            if "structural_breaks" in data and data["structural_breaks"]:
                variant_data["structural_breaks"] = [
                    {
                        "date": b["date"],
                        "type": b.get("type", "unknown"),
                        "ratio": round(b.get("ratio", 0), 2)
                    }
                    for b in data["structural_breaks"][:3]  # Top 3 only
                ]
            
            # Latest values
            if "latest_value" in data and data["latest_value"] is not None:
                variant_data["latest"] = {
                    "date": data.get("last_date"),
                    "value": round(data["latest_value"], 2),
                    "unit": _get_unit_for_variant(variant)
                }
            
            # Add basic stats
            if "observations" in data:
                variant_data["stats"] = {
                    "observations": data["observations"],
                    "first_date": data["first_date"],
                    "last_date": data["last_date"],
                    "mean": round(data["mean"], 2) if data.get("mean") is not None else None,
                    "min": round(data["min"], 2) if data.get("min") is not None else None,
                    "max": round(data["max"], 2) if data.get("max") is not None else None
                }
            
            country_data[variant] = variant_data
        
        output["results"]["countries"][country] = country_data
    
    # Format cross-country analysis (compact)
    if cross_country:
        cross_country_output = {}
        
        # Iterate over variants
        for variant, variant_data in cross_country.items():
            variant_cross = {}
            
            # Basic statistics
            if "latest_snapshot" in variant_data:
                stats = variant_data["latest_snapshot"]
                variant_cross["statistics"] = {
                    "mean": round(stats.get("mean", 0), 2) if stats.get("mean") is not None else None,
                    "median": round(stats.get("median", 0), 2) if stats.get("median") is not None else None,
                    "std": round(stats.get("std", 0), 2) if stats.get("std") is not None else None,
                    "cv": round(stats.get("coefficient_of_variation", 0), 3) if stats.get("coefficient_of_variation") is not None else None,
                    "min": round(stats.get("min", 0), 2) if stats.get("min") is not None else None,
                    "max": round(stats.get("max", 0), 2) if stats.get("max") is not None else None
                }
            
            # Convergence (only if computed)
            if "convergence" in variant_data:
                convergence = variant_data["convergence"]
                conv_data = {}
                
                if "sigma" in convergence:
                    sigma = convergence["sigma"]
                    conv_data["sigma"] = {
                        "trend": "converging" if sigma["slope"] < 0 else "diverging",
                        "slope": round(sigma["slope"], 4),
                        "r_squared": round(sigma["r_squared"], 3),
                        "p_value": round(sigma["p_value"], 4),
                        "significant": sigma["p_value"] < 0.05
                    }
                
                if "beta" in convergence:
                    beta = convergence["beta"]
                    conv_data["beta"] = {
                        "coefficient": round(beta["coefficient"], 4),
                        "r_squared": round(beta["r_squared"], 3),
                        "p_value": round(beta["p_value"], 4),
                        "significant": beta["p_value"] < 0.05,
                        "interpretation": "catch-up growth" if beta["coefficient"] < 0 else "no catch-up"
                    }
                
                if conv_data:
                    variant_cross["convergence"] = conv_data
            
            cross_country_output[variant] = variant_cross
        
        output["results"]["cross_country"] = cross_country_output
    
    # Format rankings (compact)
    if rankings:
        rankings_output = {}
        
        for ranking_type, ranking_list in rankings.items():
            # ranking_list is a list of tuples (country, value)
            rankings_output[ranking_type] = [
                {
                    "rank": i + 1,
                    "country": country,
                    "value": round(value, 2) if value is not None else None
                }
                for i, (country, value) in enumerate(ranking_list[:10])  # Top 10
            ]
        
        output["results"]["rankings"] = rankings_output
    
    # Add interpretation hints (AI-friendly)
    output["interpretation"] = _generate_interpretation_hints(
        output["results"],
        analysis_metadata
    )
    
    # Serialize to JSON
    output_str = json.dumps(output, indent=2)
    
    metadata = {
        "format": "analysis",
        "optimized_for": "ai_consumption",
        "token_estimate": len(output_str) // 4,  # Rough estimate
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Formatted output: ~{metadata['token_estimate']} tokens")
    
    return FormatResult(
        output=output_str,
        format_type="analysis",
        metadata=metadata
    )


def format_dataset(
    analysis_result: Any,
    fetch_metadata: Dict[str, Any],
    raw_data: Dict[str, Dict[str, pd.Series]]
) -> FormatResult:
    """
    Format as tidy dataset (long format) for further analysis.
    
    Returns time series data in tidy format:
    - Each row: one observation
    - Columns: date, country, variant, value, unit
    - Ready for pandas, R, or statistical software
    
    Args:
        analysis_result: AnalysisResult from analysis layer
        fetch_metadata: Metadata from fetch layer
        raw_data: Raw time series data from fetch layer (nested dict: country -> variant -> Series)
    
    Returns:
        FormatResult with serialized DataFrame
    """
    logger.info("Formatting output: dataset (tidy format)")
    
    # Build tidy DataFrame
    rows = []
    
    # Handle nested structure: country -> variant -> Series
    for country, variants_dict in raw_data.items():
        for variant, series in variants_dict.items():
            for date, value in series.items():
                rows.append({
                    "date": date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date),
                    "country": country,
                    "variant": variant,
                    "value": float(value),
                    "unit": _get_unit_for_variant(variant)
                })
    
    df = pd.DataFrame(rows)
    
    # Sort by date, country, variant
    df = df.sort_values(["date", "country", "variant"]).reset_index(drop=True)
    
    # Serialize to JSON (records format)
    dataset_json = df.to_json(orient="records", date_format="iso")
    
    output = {
        "tool": "analyze_gdp_cross_country",
        "dataset": json.loads(dataset_json),
        "metadata": {
            "format": "tidy",
            "rows": len(df),
            "countries": df["country"].nunique(),
            "variants": df["variant"].nunique(),
            "period": {
                "start": df["date"].min(),
                "end": df["date"].max()
            }
        }
    }
    
    output_str = json.dumps(output, indent=2)
    
    metadata = {
        "format": "dataset",
        "rows": len(df),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Formatted dataset: {len(df)} rows")
    
    return FormatResult(
        output=output_str,
        format_type="dataset",
        metadata=metadata
    )


def format_summary(
    analysis_result: Any,
    fetch_metadata: Dict[str, Any]
) -> FormatResult:
    """
    Format as human-readable markdown summary.
    
    Generates a concise report with:
    - Key findings
    - Rankings
    - Convergence analysis
    - Recommendations
    
    Args:
        analysis_result: AnalysisResult from analysis layer
        fetch_metadata: Metadata from fetch layer
    
    Returns:
        FormatResult with markdown text
    """
    logger.info("Formatting output: summary (markdown)")
    
    lines = []
    
    # Header
    lines.append("# GDP Cross-Country Analysis Summary\n")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    lines.append(f"**Period:** {fetch_metadata.get('observation_start')} to {fetch_metadata.get('observation_end')}\n")
    lines.append(f"**Countries:** {len(analysis_result.by_country)}\n")
    lines.append(f"**Variants:** {', '.join(fetch_metadata.get('variants_requested', []))}\n")
    
    # Rankings
    if analysis_result.rankings:
        lines.append("\n## Rankings\n")
        
        if "by_growth" in analysis_result.rankings:
            lines.append("### Top 5 by Growth Rate (CAGR)\n")
            for i, r in enumerate(analysis_result.rankings["by_growth"][:5]):
                lines.append(f"{i+1}. **{r['country'].upper()}**: {r['cagr']:.2f}% per year\n")
        
        if "by_level" in analysis_result.rankings:
            lines.append("\n### Top 5 by Current Level\n")
            for i, r in enumerate(analysis_result.rankings["by_level"][:5]):
                lines.append(f"{i+1}. **{r['country'].upper()}**: {r['value']:.2f}\n")
    
    # Convergence
    if analysis_result.cross_country and "convergence" in analysis_result.cross_country:
        lines.append("\n## Convergence Analysis\n")
        
        conv = analysis_result.cross_country["convergence"]
        
        if "sigma" in conv:
            sigma = conv["sigma"]
            trend = "converging" if sigma["slope"] < 0 else "diverging"
            sig = " (significant)" if sigma["p_value"] < 0.05 else ""
            lines.append(f"- **Sigma Convergence:** Countries are **{trend}**{sig} (slope: {sigma['slope']:.4f}, p={sigma['p_value']:.3f})\n")
        
        if "beta" in conv:
            beta = conv["beta"]
            catchup = "Yes" if beta["coefficient"] < 0 and beta["p_value"] < 0.05 else "No"
            lines.append(f"- **Beta Convergence (Catch-up Growth):** **{catchup}** (β={beta['coefficient']:.4f}, p={beta['p_value']:.3f})\n")
    
    # Key Findings
    lines.append("\n## Key Findings\n")
    
    # Highest/lowest growth
    if analysis_result.rankings and "by_growth" in analysis_result.rankings:
        growth_ranks = analysis_result.rankings["by_growth"]
        if growth_ranks:
            highest = growth_ranks[0]
            lowest = growth_ranks[-1]
            lines.append(f"- **Fastest growing:** {highest['country'].upper()} ({highest['cagr']:.2f}% CAGR)\n")
            lines.append(f"- **Slowest growing:** {lowest['country'].upper()} ({lowest['cagr']:.2f}% CAGR)\n")
    
    # Cross-country stats
    if analysis_result.cross_country and "statistics" in analysis_result.cross_country:
        stats = analysis_result.cross_country["statistics"]
        lines.append(f"- **Average growth:** {stats.get('mean', 0):.2f}%\n")
        lines.append(f"- **Variability (CV):** {stats.get('cv', 0):.3f}\n")
    
    # Limitations
    lines.append("\n## Limitations\n")
    limitations = _get_limitations(analysis_result.metadata)
    for lim in limitations:
        lines.append(f"- {lim}\n")
    
    output = "".join(lines)
    
    # Wrap in JSON for MCP
    output_json = {
        "tool": "analyze_gdp_cross_country",
        "summary": output,
        "format": "markdown"
    }
    
    output_str = json.dumps(output_json, indent=2)
    
    metadata = {
        "format": "summary",
        "lines": len(lines),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Formatted summary: {len(lines)} lines")
    
    return FormatResult(
        output=output_str,
        format_type="summary",
        metadata=metadata
    )


def format_both(
    analysis_result: Any,
    fetch_metadata: Dict[str, Any],
    raw_data: Dict[str, pd.Series]
) -> FormatResult:
    """
    Format as combined analysis + dataset.
    
    Returns both the AI-optimized analysis AND the tidy dataset
    in a single JSON structure. Useful for comprehensive exports.
    
    Args:
        analysis_result: AnalysisResult from analysis layer
        fetch_metadata: Metadata from fetch layer
        raw_data: Raw time series data from fetch layer
    
    Returns:
        FormatResult with combined output
    """
    logger.info("Formatting output: both (analysis + dataset)")
    
    # Get analysis format
    analysis_format = format_analysis(analysis_result, fetch_metadata)
    analysis_data = json.loads(analysis_format.output)
    
    # Get dataset format
    dataset_format = format_dataset(analysis_result, fetch_metadata, raw_data)
    dataset_data = json.loads(dataset_format.output)
    
    # Combine
    output = {
        "tool": "analyze_gdp_cross_country",
        "analysis": analysis_data["results"],
        "dataset": dataset_data["dataset"],
        "metadata": {
            **analysis_data["metadata"],
            "dataset_rows": dataset_data["metadata"]["rows"],
            "format": "both"
        },
        "interpretation": analysis_data.get("interpretation")
    }
    
    output_str = json.dumps(output, indent=2)
    
    metadata = {
        "format": "both",
        "dataset_rows": dataset_data["metadata"]["rows"],
        "token_estimate": len(output_str) // 4,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Formatted both: analysis + {dataset_data['metadata']['rows']} dataset rows")
    
    return FormatResult(
        output=output_str,
        format_type="both",
        metadata=metadata
    )


# Helper functions

def _get_limitations(metadata: Dict[str, Any]) -> List[str]:
    """Generate list of analysis limitations."""
    limitations = []
    
    # Missing data
    if metadata.get("countries_with_missing_data", 0) > 0:
        limitations.append(
            f"{metadata['countries_with_missing_data']} countries have incomplete data"
        )
    
    # Short period
    if metadata.get("period_years", 0) < 5:
        limitations.append(
            "Analysis period < 5 years - growth metrics may be unstable"
        )
    
    # Few countries
    countries_analyzed = metadata.get("countries_analyzed", [])
    if isinstance(countries_analyzed, list):
        num_countries = len(countries_analyzed)
    else:
        num_countries = countries_analyzed if isinstance(countries_analyzed, int) else 0
    
    if num_countries < 3:
        limitations.append(
            "Cross-country analysis requires 3+ countries for meaningful convergence tests"
        )
    
    # Computed variants
    if metadata.get("has_computed_variants", False):
        limitations.append(
            "Some variants computed from other series (see metadata.computed_variants)"
        )
    
    return limitations


def _generate_interpretation_hints(
    results: Dict[str, Any],
    metadata: Dict[str, Any]
) -> List[str]:
    """Generate AI-friendly interpretation hints."""
    hints = []
    
    # Convergence interpretation
    cross = results.get("cross_country", {})
    if "convergence" in cross:
        conv = cross["convergence"]
        
        if "sigma" in conv:
            if conv["sigma"]["significant"]:
                trend = conv["sigma"]["trend"]
                hints.append(
                    f"Sigma convergence: Countries are significantly {trend} "
                    f"(p={conv['sigma']['p_value']:.3f})"
                )
        
        if "beta" in conv:
            if conv["beta"]["significant"]:
                hints.append(
                    f"Beta convergence: {conv['beta']['interpretation']} detected "
                    f"(β={conv['beta']['coefficient']:.4f}, p={conv['beta']['p_value']:.3f})"
                )
    
    # Growth spread
    rankings = results.get("rankings", {})
    if "by_growth" in rankings and len(rankings["by_growth"]) >= 2:
        top = rankings["by_growth"][0]
        bottom = rankings["by_growth"][-1]
        spread = top["cagr_pct"] - bottom["cagr_pct"]
        
        if spread > 5:
            hints.append(
                f"Large growth spread: {spread:.1f}pp between fastest ({top['country']}) "
                f"and slowest ({bottom['country']})"
            )
    
    # Volatility
    countries = results.get("countries", {})
    high_volatility = [
        c for c, data in countries.items()
        if data.get("growth", {}).get("volatility", 0) > 3
    ]
    
    if high_volatility:
        hints.append(
            f"High volatility (>3%): {', '.join(high_volatility[:3])}"
        )
    
    # Data quality
    if metadata.get("countries_with_missing_data", 0) > 0:
        hints.append(
            f"Data quality: {metadata['countries_with_missing_data']} countries "
            "have missing observations"
        )
    
    return hints


def _get_unit_for_variant(variant: str) -> str:
    """Get unit string for GDP variant."""
    units = {
        "nominal_usd": "Billions USD",
        "nominal_lcu": "Billions LCU",
        "constant_2010": "Billions USD (2010)",
        "constant_2015": "Billions USD (2015)",
        "ppp": "Billions USD (PPP)",
        "per_capita_nominal": "USD per capita",
        "per_capita_constant": "USD per capita (2010)",
        "per_capita_ppp": "USD per capita (PPP)",
        "growth_rate": "Percent"
    }
    return units.get(variant, "Unknown")
