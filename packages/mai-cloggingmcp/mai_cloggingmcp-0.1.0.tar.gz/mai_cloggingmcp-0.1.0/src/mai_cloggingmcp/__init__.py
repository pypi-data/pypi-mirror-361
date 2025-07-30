# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Central Logging Pipeline Capacity Estimator")


@mcp.tool()
def estimate_logagent_capacity(
    log_rate_per_node: float,  # Y: Maximum log generation rate per node (MB/s)
    ignore_older: int = 600,   # ignore_older setting in seconds, default 10 minutes
    refresh_interval: int = 10  # refresh_interval in seconds, default 10 seconds
) -> dict:
    """
    Estimate LogAgent capacity and provide resource recommendations, LogAgent is the major service of Central Logging Pipeline.
    
    Args:
        log_rate_per_node: Y - Maximum log generation rate per node in MB/s
        ignore_older: ignore_older setting in seconds (default: 600s = 10 minutes)
        refresh_interval: refresh_interval in seconds (default: 10s)
    
    Returns:
        dict: Estimated capacity and recommendations
    """
    # Convert ignore_older from seconds to minutes for calculation
    ignore_older_minutes = ignore_older / 60
    
    # Calculate memory usage: Memory (MB) ≈ Y × ignore_older × 15
    memory_usage = log_rate_per_node * ignore_older_minutes * 15
    
    # Generate recommendations
    recommendations = []
    
    # CPU Usage evaluation based on log rate and refresh interval
    cpu_warning_reasons = []
    if log_rate_per_node > 5:
        cpu_warning_reasons.append("log rate > 5MB/s")
    if refresh_interval < 10:
        cpu_warning_reasons.append("refresh_interval < 10s")
    
    if cpu_warning_reasons:
        recommendations.append(
            "Increase ProcessorRateControlHardCapPercentage from default 1% due to: " +
            " and ".join(cpu_warning_reasons)
        )
    
    # Memory Usage warning
    if log_rate_per_node > 6.5:
        recommendations.append(
            "High log rate detected: Increase memory limit from default 1024MB "
            "due to log rate > 6.5MB/s"
        )
    
    return {
        "estimated_memory_usage_mb": round(memory_usage, 2),
        "cpu_usage_estimate": "~0.3% baseline (increases with log rate and lower refresh_interval)",
        "recommendations": recommendations,
        "input_parameters": {
            "log_rate_per_node_mbs": log_rate_per_node,
            "ignore_older_seconds": ignore_older,
            "refresh_interval_seconds": refresh_interval
        }
    }


@mcp.tool()
def estimate_kafka_capacity(
    num_nodes: int,  # N: Number of nodes sending logs
    write_speed_per_node: float,  # Y: Maximum write speed per node (MB/s)
    kafka_retention_hours: float = 0.5  # Kafka retention period in hours, default 30 minutes
) -> dict:
    """
    Estimate Kafka capacity requirements for central logging pipeline.
    
    Args:
        num_nodes: N - Number of nodes sending logs
        write_speed_per_node: Y - Maximum write speed per node in MB/s
        kafka_retention_hours: Kafka log retention period in hours (default: 30 minutes)
    
    Returns:
        dict: Estimated capacity requirements and recommendations
    """
    # Calculate total Kafka Gen8 machines needed
    total_machines = (num_nodes * write_speed_per_node) / 1000
    
    # Calculate storage requirements (in GB) based on retention period
    # Storage = (N * Y * kafka_retention_hours * 3600) / 1024 GB
    storage_gb = (num_nodes * write_speed_per_node * kafka_retention_hours * 3600) / 1024
    
    # Generate recommendations
    recommendations = []
    
    if kafka_retention_hours > 0.5:  # More than 30 minutes
        recommendations.append(
            "Consider using HDFS for persistent storage instead of increasing Kafka retention period "
            "beyond 30 minutes to optimize resource usage."
        )
    
    if num_nodes > 1000:
        recommendations.append(
            "Large node count detected. Ensure Kafka proxy is enabled on the same machine "
            "function as your namespace for multi-region deployments."
        )
    
    return {
        "kafka_gen8_machines": round(total_machines, 2),
        "estimated_storage_gb": round(storage_gb, 2),
        "recommendations": recommendations,
        "input_parameters": {
            "num_nodes": num_nodes,
            "write_speed_per_node_mbs": write_speed_per_node,
            "kafka_retention_hours": kafka_retention_hours
        }
    }

@mcp.tool()
def estimate_hdfs_capacity(
    raw_log_size_per_day: float,  # X: Total raw log size per day in TB
    retention_days: int,          # T: Data retention period in days
    compression_format: str = "parquet_uncompressed"  # Format/encoding affecting compression ratio
) -> dict:
    """
    Estimate HDFS capacity requirements for central logging pipeline.
    
    Args:
        raw_log_size_per_day: X - Total raw log size per day in TB
        retention_days: T - Data retention period in days
        compression_format: Format affecting compression ratio (default: parquet_uncompressed)
            Supported formats:
            - parquet_uncompressed: Uncompressed AP logs in Parquet (10-20% ratio)
            - parquet_base64: Base64 encoded logs in Parquet (50% ratio)
            - custom: For other formats (uses 50% as safe default)
    
    Returns:
        dict: Estimated capacity requirements and recommendations
    """
    # Determine compression ratio based on format
    compression_ratios = {
        "parquet_uncompressed": 0.15,  # Using 15% as middle ground for 10-20% range
        "parquet_base64": 0.50,
        "custom": 0.50  # Conservative default for unknown formats
    }
    
    compression_ratio = compression_ratios.get(compression_format, 0.50)
    
    # Calculate HDFS physical size in TiB
    # Formula: HDFS Physical size (TiB) = 3 × X × T × R
    hdfs_size_tib = 3 * raw_log_size_per_day * retention_days * compression_ratio
    
    # Generate recommendations
    recommendations = []
    
    if compression_format == "parquet_base64":
        recommendations.append(
            "Consider using uncompressed AP logs instead of Base64 encoding to achieve "
            "better compression ratio (10-20% vs 50%)"
        )
    
    if compression_format == "custom":
        recommendations.append(
            "Consider testing with sample data to determine actual compression ratio "
            "for your specific format/encoding"
        )
    
    if retention_days > 90:
        recommendations.append(
            "Long retention period detected. Consider implementing data lifecycle "
            "management policies for cost-effective storage"
        )
    
    return {
        "estimated_hdfs_size_tib": round(hdfs_size_tib, 2),
        "effective_compression_ratio": f"{compression_ratio:.1%}",
        "recommendations": recommendations,
        "input_parameters": {
            "raw_log_size_per_day_tb": raw_log_size_per_day,
            "retention_days": retention_days,
            "compression_format": compression_format
        }
    }

def main() -> None:
    mcp.run(transport='stdio')
