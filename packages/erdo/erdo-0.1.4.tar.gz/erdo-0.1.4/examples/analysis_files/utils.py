import json
import pandas as pd
from typing import Dict, Any, List, Optional


def prepare_data(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare dataset for analysis.

    Args:
        dataset: Dataset information from context

    Returns:
        Prepared data structure for analysis
    """
    prepared = {
        "filename": dataset.get("filename", "unknown"),
        "file_type": dataset.get("type", "unknown"),
        "size": dataset.get("size", 0),
        "columns": dataset.get("columns", []),
        "metadata": dataset.get("metadata", {}),
        "prepared": True,
    }

    print(f"Prepared dataset: {prepared['filename']} ({prepared['file_type']})")

    return prepared


def validate_results(
    results: Dict[str, Any], prepared_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate and enhance analysis results.

    Args:
        results: Raw analysis results
        prepared_data: Prepared dataset information

    Returns:
        Validated and enhanced results
    """
    enhanced_results = results.copy()

    # Add data preparation info
    enhanced_results["data_preparation"] = prepared_data

    # Validate confidence score
    confidence = enhanced_results.get("confidence", 0.0)
    if confidence < 0 or confidence > 1:
        enhanced_results["confidence"] = max(0.0, min(1.0, confidence))
        enhanced_results["confidence_adjusted"] = True

    # Ensure required fields exist
    if "insights" not in enhanced_results:
        enhanced_results["insights"] = []
    if "recommendations" not in enhanced_results:
        enhanced_results["recommendations"] = []

    # Add validation metadata
    enhanced_results["validation"] = {
        "validated": True,
        "data_source": prepared_data.get("filename", "unknown"),
        "validation_checks": [
            "confidence_range_check",
            "required_fields_check",
            "data_preparation_check",
        ],
    }

    print(f"Validated results with confidence: {enhanced_results['confidence']:.1%}")

    return enhanced_results


def calculate_data_quality_score(dataset: Dict[str, Any]) -> float:
    """Calculate a data quality score based on available metadata."""
    score = 0.5  # Base score

    # Boost score for known file types
    if dataset.get("type") in ["csv", "json", "xlsx", "parquet"]:
        score += 0.2

    # Boost score if we have column information
    if dataset.get("columns"):
        score += 0.2

    # Boost score if we have size information
    if dataset.get("size", 0) > 0:
        score += 0.1

    return min(1.0, score)


def format_insights(insights: List[str], max_length: int = 100) -> List[str]:
    """Format insights for better readability."""
    formatted = []

    for insight in insights:
        if len(insight) > max_length:
            # Truncate long insights
            formatted.append(insight[: max_length - 3] + "...")
        else:
            formatted.append(insight)

    return formatted


def generate_summary(results: Dict[str, Any]) -> str:
    """Generate a human-readable summary of the analysis."""
    query = results.get("query", "Unknown query")
    confidence = results.get("confidence", 0.0)
    insights_count = len(results.get("insights", []))
    recommendations_count = len(results.get("recommendations", []))

    confidence_desc = (
        "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
    )

    summary = (
        f"Analysis of '{query}' completed with {confidence_desc} confidence ({confidence:.1%}). "
        f"Generated {insights_count} insights and {recommendations_count} recommendations."
    )

    return summary


def export_results(
    results: Dict[str, Any], filename: str = "analysis_results.json"
) -> bool:
    """Export results to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results exported to {filename}")
        return True
    except Exception as e:
        print(f"Failed to export results: {e}")
        return False


def load_analysis_config(config_path: str = "analysis_config.json") -> Dict[str, Any]:
    """Load analysis configuration from file."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"Loaded analysis config from {config_path}")
        return config
    except FileNotFoundError:
        # Return default config
        default_config = {
            "confidence_threshold": 0.7,
            "max_insights": 10,
            "max_recommendations": 5,
            "enable_validation": True,
        }
        print("Using default analysis configuration")
        return default_config
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


if __name__ == "__main__":
    # Test the utility functions
    test_dataset = {
        "filename": "sales_data.csv",
        "type": "csv",
        "size": 1024000,
        "columns": ["date", "sales", "region"],
    }

    # Test data preparation
    prepared = prepare_data(test_dataset)
    print(f"Prepared data: {prepared}")

    # Test quality score
    quality_score = calculate_data_quality_score(test_dataset)
    print(f"Data quality score: {quality_score:.1%}")

    # Test results validation
    mock_results = {
        "query": "Test analysis",
        "confidence": 0.85,
        "insights": ["Test insight 1", "Test insight 2"],
        "recommendations": ["Test recommendation"],
    }

    validated = validate_results(mock_results, prepared)
    print(
        f"Validation complete: {validated.get('validation', {}).get('validated', False)}"
    )

    # Test summary generation
    summary = generate_summary(validated)
    print(f"Summary: {summary}")
