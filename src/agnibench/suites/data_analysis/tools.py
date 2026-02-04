"""
Tools for the data analysis benchmark suite.

Provides 8 tools for data exploration, querying, and insight generation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import random

from agentbuilder.Tools.base import Tool


# Storage for simulated data
_data_state: Dict[str, Any] = {
    "datasets": [],
    "query_results": [],
    "visualizations": [],
    "insights": [],
}


def set_data_state(data: Dict[str, Any]) -> None:
    """Set the data state (called by environment)."""
    global _data_state
    _data_state = data


def get_data_state() -> Dict[str, Any]:
    """Get current data state."""
    return _data_state


# Pydantic models

class ListDatasetsParams(BaseModel):
    """Parameters for listing datasets."""
    category: Optional[str] = Field(default=None, description="Filter by category")
    include_archived: bool = Field(default=False, description="Include archived/deprecated datasets (default: False)")


class DescribeDatasetParams(BaseModel):
    """Parameters for describing a dataset."""
    dataset_id: str = Field(description="ID of the dataset to describe")


class QueryDataParams(BaseModel):
    """Parameters for querying data."""
    dataset_id: str = Field(description="ID of the dataset to query")
    select: List[str] = Field(default_factory=lambda: ["*"], description="Columns to select")
    where: Optional[str] = Field(default=None, description="Filter condition (e.g., 'region = North')")
    group_by: Optional[str] = Field(default=None, description="Column to group by")
    order_by: Optional[str] = Field(default=None, description="Column to order by")
    limit: int = Field(default=10, description="Maximum rows to return")


class ComputeStatisticsParams(BaseModel):
    """Parameters for computing statistics."""
    dataset_id: str = Field(description="ID of the dataset")
    column: str = Field(description="Column to compute statistics for")
    statistic: str = Field(default="summary", description="Type: summary, mean, median, std, min, max, count, percentiles")
    group_by: Optional[str] = Field(default=None, description="Optional grouping column")


class CreateVisualizationParams(BaseModel):
    """Parameters for creating a visualization."""
    dataset_id: str = Field(description="ID of the dataset")
    chart_type: str = Field(description="Type: bar, line, scatter, pie, histogram, heatmap")
    x_column: str = Field(description="Column for X axis")
    y_column: Optional[str] = Field(default=None, description="Column for Y axis")
    group_by: Optional[str] = Field(default=None, description="Column to group/color by")
    title: Optional[str] = Field(default=None, description="Chart title")


class DetectAnomaliesParams(BaseModel):
    """Parameters for anomaly detection."""
    dataset_id: str = Field(description="ID of the dataset")
    column: str = Field(description="Column to check for anomalies")
    method: str = Field(default="zscore", description="Method: zscore, iqr, isolation_forest")
    threshold: float = Field(default=3.0, description="Threshold for anomaly detection")


class CorrelateColumnsParams(BaseModel):
    """Parameters for correlation analysis."""
    dataset_id: str = Field(description="ID of the dataset")
    columns: Optional[List[str]] = Field(default=None, description="Columns to correlate (default: all numeric)")
    method: str = Field(default="pearson", description="Method: pearson, spearman, kendall")


class SaveInsightParams(BaseModel):
    """Parameters for saving an insight."""
    title: str = Field(description="Title of the insight")
    description: str = Field(description="Detailed description of the finding")
    dataset_id: Optional[str] = Field(default=None, description="Related dataset")
    evidence: Optional[Dict[str, Any]] = Field(default=None, description="Supporting data/metrics")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


# Tool implementations

def list_datasets(params: ListDatasetsParams) -> Dict[str, Any]:
    """List available datasets."""
    datasets = _data_state.get("datasets", [])
    results = []

    for ds in datasets:
        # Filter out archived datasets by default
        if not params.include_archived and ds.get("status") == "archived":
            continue

        if params.category:
            if ds.get("category", "").lower() != params.category.lower():
                continue

        result = {
            "id": ds.get("id"),
            "name": ds.get("name"),
            "category": ds.get("category"),
            "num_rows": ds.get("num_rows"),
            "num_columns": ds.get("num_columns"),
            "description": ds.get("description"),
        }

        # Include data quality warnings if present
        if ds.get("data_quality_issues"):
            result["has_quality_issues"] = True

        # Include empty dataset indicator
        if ds.get("num_rows", 0) == 0:
            result["is_empty"] = True

        results.append(result)

    return {
        "datasets": results,
        "count": len(results),
    }


def describe_dataset(params: DescribeDatasetParams) -> Dict[str, Any]:
    """Get detailed dataset description including schema and statistics."""
    datasets = _data_state.get("datasets", [])

    for ds in datasets:
        if ds.get("id") == params.dataset_id:
            return {
                "found": True,
                "dataset": {
                    "id": ds.get("id"),
                    "name": ds.get("name"),
                    "description": ds.get("description"),
                    "num_rows": ds.get("num_rows"),
                    "num_columns": ds.get("num_columns"),
                    "columns": ds.get("columns"),
                    "sample_data": ds.get("sample_data", [])[:5],
                    "created_at": ds.get("created_at"),
                    "updated_at": ds.get("updated_at"),
                },
            }

    return {
        "found": False,
        "error": f"Dataset '{params.dataset_id}' not found",
    }


def query_data(params: QueryDataParams) -> Dict[str, Any]:
    """Query data from a dataset."""
    datasets = _data_state.get("datasets", [])

    for ds in datasets:
        if ds.get("id") == params.dataset_id:
            # Simulated query results based on dataset
            data = ds.get("data", [])

            # Apply simple filtering if where clause provided
            if params.where and data:
                # Simple parsing of where clause
                filtered_data = []
                for row in data:
                    # Very simplified where parsing
                    if "=" in params.where:
                        parts = params.where.split("=")
                        col = parts[0].strip()
                        val = parts[1].strip().strip("'\"")
                        if str(row.get(col, "")).lower() == val.lower():
                            filtered_data.append(row)
                    elif ">" in params.where:
                        parts = params.where.split(">")
                        col = parts[0].strip()
                        val = float(parts[1].strip())
                        if row.get(col, 0) > val:
                            filtered_data.append(row)
                    elif "<" in params.where:
                        parts = params.where.split("<")
                        col = parts[0].strip()
                        val = float(parts[1].strip())
                        if row.get(col, 0) < val:
                            filtered_data.append(row)
                    else:
                        filtered_data.append(row)
                data = filtered_data

            # Apply grouping if specified
            if params.group_by and data:
                groups = {}
                for row in data:
                    key = row.get(params.group_by, "Unknown")
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(row)

                # Aggregate (simple count)
                data = [
                    {params.group_by: k, "count": len(v)}
                    for k, v in groups.items()
                ]

            # Apply limit
            data = data[:params.limit]

            # Select columns
            if params.select and params.select != ["*"] and data:
                data = [
                    {k: v for k, v in row.items() if k in params.select}
                    for row in data
                ]

            # Store query result
            query_result = {
                "query_id": f"query_{len(_data_state.get('query_results', []))+1}",
                "dataset_id": params.dataset_id,
                "parameters": {
                    "select": params.select,
                    "where": params.where,
                    "group_by": params.group_by,
                },
                "row_count": len(data),
                "data": data,
            }

            if "query_results" not in _data_state:
                _data_state["query_results"] = []
            _data_state["query_results"].append(query_result)

            return {
                "success": True,
                "query_id": query_result["query_id"],
                "row_count": len(data),
                "data": data,
            }

    return {
        "success": False,
        "error": f"Dataset '{params.dataset_id}' not found",
    }


def compute_statistics(params: ComputeStatisticsParams) -> Dict[str, Any]:
    """Compute statistics for a column."""
    datasets = _data_state.get("datasets", [])

    for ds in datasets:
        if ds.get("id") == params.dataset_id:
            # Get column statistics from pre-computed data
            col_stats = ds.get("column_statistics", {}).get(params.column, {})

            if not col_stats:
                return {
                    "success": False,
                    "error": f"Column '{params.column}' not found or has no statistics",
                }

            # If group_by specified, return grouped stats
            if params.group_by:
                grouped_stats = ds.get("grouped_statistics", {}).get(
                    f"{params.column}_by_{params.group_by}", {}
                )
                return {
                    "success": True,
                    "dataset_id": params.dataset_id,
                    "column": params.column,
                    "grouped_by": params.group_by,
                    "statistics": grouped_stats,
                }

            # Return requested statistic type
            if params.statistic == "summary":
                return {
                    "success": True,
                    "dataset_id": params.dataset_id,
                    "column": params.column,
                    "statistics": col_stats,
                }
            elif params.statistic in col_stats:
                return {
                    "success": True,
                    "dataset_id": params.dataset_id,
                    "column": params.column,
                    "statistic": params.statistic,
                    "value": col_stats[params.statistic],
                }
            else:
                return {
                    "success": True,
                    "dataset_id": params.dataset_id,
                    "column": params.column,
                    "statistics": col_stats,
                }

    return {
        "success": False,
        "error": f"Dataset '{params.dataset_id}' not found",
    }


def create_visualization(params: CreateVisualizationParams) -> Dict[str, Any]:
    """Create a visualization specification."""
    datasets = _data_state.get("datasets", [])

    for ds in datasets:
        if ds.get("id") == params.dataset_id:
            viz = {
                "id": f"viz_{len(_data_state.get('visualizations', []))+1}",
                "dataset_id": params.dataset_id,
                "chart_type": params.chart_type,
                "x_column": params.x_column,
                "y_column": params.y_column,
                "group_by": params.group_by,
                "title": params.title or f"{params.chart_type.title()} chart of {params.x_column}",
                "created_at": datetime.now().isoformat(),
                "spec": {
                    "type": params.chart_type,
                    "encoding": {
                        "x": {"field": params.x_column},
                        "y": {"field": params.y_column} if params.y_column else None,
                        "color": {"field": params.group_by} if params.group_by else None,
                    },
                },
            }

            if "visualizations" not in _data_state:
                _data_state["visualizations"] = []
            _data_state["visualizations"].append(viz)

            return {
                "success": True,
                "visualization_id": viz["id"],
                "chart_type": params.chart_type,
                "message": f"Created {params.chart_type} visualization",
                "spec": viz["spec"],
            }

    return {
        "success": False,
        "error": f"Dataset '{params.dataset_id}' not found",
    }


def detect_anomalies(params: DetectAnomaliesParams) -> Dict[str, Any]:
    """Detect anomalies in a column."""
    datasets = _data_state.get("datasets", [])

    for ds in datasets:
        if ds.get("id") == params.dataset_id:
            # Get pre-computed anomalies
            anomalies = ds.get("anomalies", {}).get(params.column, [])

            return {
                "success": True,
                "dataset_id": params.dataset_id,
                "column": params.column,
                "method": params.method,
                "threshold": params.threshold,
                "anomaly_count": len(anomalies),
                "anomalies": anomalies[:10],  # Return top 10
                "percentage": round(len(anomalies) / ds.get("num_rows", 1) * 100, 2),
            }

    return {
        "success": False,
        "error": f"Dataset '{params.dataset_id}' not found",
    }


def correlate_columns(params: CorrelateColumnsParams) -> Dict[str, Any]:
    """Compute correlations between columns."""
    datasets = _data_state.get("datasets", [])

    for ds in datasets:
        if ds.get("id") == params.dataset_id:
            # Get pre-computed correlations
            correlations = ds.get("correlations", {})

            if params.columns:
                # Filter to requested columns
                filtered = {}
                for col1 in params.columns:
                    if col1 in correlations:
                        filtered[col1] = {
                            k: v for k, v in correlations[col1].items()
                            if k in params.columns
                        }
                correlations = filtered

            # Find strongest correlations
            strong_correlations = []
            for col1, corrs in correlations.items():
                for col2, value in corrs.items():
                    if col1 < col2 and abs(value) > 0.5:
                        strong_correlations.append({
                            "column1": col1,
                            "column2": col2,
                            "correlation": value,
                            "strength": "strong" if abs(value) > 0.7 else "moderate",
                        })

            return {
                "success": True,
                "dataset_id": params.dataset_id,
                "method": params.method,
                "correlation_matrix": correlations,
                "strong_correlations": sorted(
                    strong_correlations,
                    key=lambda x: abs(x["correlation"]),
                    reverse=True,
                ),
            }

    return {
        "success": False,
        "error": f"Dataset '{params.dataset_id}' not found",
    }


def save_insight(params: SaveInsightParams) -> Dict[str, Any]:
    """Save a data insight/finding."""
    insight = {
        "id": f"insight_{len(_data_state.get('insights', []))+1}",
        "title": params.title,
        "description": params.description,
        "dataset_id": params.dataset_id,
        "evidence": params.evidence,
        "tags": params.tags,
        "created_at": datetime.now().isoformat(),
    }

    if "insights" not in _data_state:
        _data_state["insights"] = []
    _data_state["insights"].append(insight)

    return {
        "success": True,
        "insight_id": insight["id"],
        "message": "Insight saved successfully",
    }


# Tool creation

def get_data_analysis_tools() -> List[Tool]:
    """Get all data analysis tools."""
    return [
        Tool(
            name="list_datasets",
            description="List all available datasets with basic metadata. Archived datasets are excluded by default. Returns quality warnings for datasets with issues.",
            parameters={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category"},
                    "include_archived": {"type": "boolean", "description": "Include archived/deprecated datasets", "default": False}
                },
                "required": []
            },
            function=lambda **kwargs: list_datasets(ListDatasetsParams(**kwargs))
        ),
        Tool(
            name="describe_dataset",
            description="Get detailed schema, statistics, and sample data for a dataset.",
            parameters={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of the dataset"}
                },
                "required": ["dataset_id"]
            },
            function=lambda **kwargs: describe_dataset(DescribeDatasetParams(**kwargs))
        ),
        Tool(
            name="query_data",
            description="Query data with filtering, grouping, and sorting. SQL-like syntax.",
            parameters={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of the dataset"},
                    "select": {"type": "array", "items": {"type": "string"}, "description": "Columns to select"},
                    "where": {"type": "string", "description": "Filter condition (e.g., 'region = North')"},
                    "group_by": {"type": "string", "description": "Column to group by"},
                    "order_by": {"type": "string", "description": "Column to order by"},
                    "limit": {"type": "integer", "description": "Maximum rows", "default": 10}
                },
                "required": ["dataset_id"]
            },
            function=lambda **kwargs: query_data(QueryDataParams(**kwargs))
        ),
        Tool(
            name="compute_statistics",
            description="Calculate statistics for a column: mean, median, std, min, max, percentiles.",
            parameters={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of the dataset"},
                    "column": {"type": "string", "description": "Column to analyze"},
                    "statistic": {"type": "string", "enum": ["summary", "mean", "median", "std", "min", "max", "count", "percentiles"], "description": "Statistic type"},
                    "group_by": {"type": "string", "description": "Optional grouping column"}
                },
                "required": ["dataset_id", "column"]
            },
            function=lambda **kwargs: compute_statistics(ComputeStatisticsParams(**kwargs))
        ),
        Tool(
            name="create_visualization",
            description="Create a chart/visualization. Types: bar, line, scatter, pie, histogram, heatmap.",
            parameters={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of the dataset"},
                    "chart_type": {"type": "string", "enum": ["bar", "line", "scatter", "pie", "histogram", "heatmap"], "description": "Chart type"},
                    "x_column": {"type": "string", "description": "Column for X axis"},
                    "y_column": {"type": "string", "description": "Column for Y axis"},
                    "group_by": {"type": "string", "description": "Column to group/color by"},
                    "title": {"type": "string", "description": "Chart title"}
                },
                "required": ["dataset_id", "chart_type", "x_column"]
            },
            function=lambda **kwargs: create_visualization(CreateVisualizationParams(**kwargs))
        ),
        Tool(
            name="detect_anomalies",
            description="Find outliers and anomalies in a column using statistical methods.",
            parameters={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of the dataset"},
                    "column": {"type": "string", "description": "Column to check"},
                    "method": {"type": "string", "enum": ["zscore", "iqr", "isolation_forest"], "description": "Detection method"},
                    "threshold": {"type": "number", "description": "Anomaly threshold", "default": 3.0}
                },
                "required": ["dataset_id", "column"]
            },
            function=lambda **kwargs: detect_anomalies(DetectAnomaliesParams(**kwargs))
        ),
        Tool(
            name="correlate_columns",
            description="Compute correlation coefficients between numeric columns.",
            parameters={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "ID of the dataset"},
                    "columns": {"type": "array", "items": {"type": "string"}, "description": "Columns to correlate"},
                    "method": {"type": "string", "enum": ["pearson", "spearman", "kendall"], "description": "Correlation method"}
                },
                "required": ["dataset_id"]
            },
            function=lambda **kwargs: correlate_columns(CorrelateColumnsParams(**kwargs))
        ),
        Tool(
            name="save_insight",
            description="Record an analysis insight or finding for the report.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Insight title"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "dataset_id": {"type": "string", "description": "Related dataset"},
                    "evidence": {"type": "object", "description": "Supporting metrics"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"}
                },
                "required": ["title", "description"]
            },
            function=lambda **kwargs: save_insight(SaveInsightParams(**kwargs))
        ),
    ]
