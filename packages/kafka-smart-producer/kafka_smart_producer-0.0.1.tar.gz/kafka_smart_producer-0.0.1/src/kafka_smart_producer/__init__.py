"""
Kafka Smart Producer - Intelligent Kafka producer with real-time, lag-aware partition
selection.

This library extends confluent-kafka-python with smart partition selection based on
consumer lag monitoring to avoid "hot partitions" and improve throughput.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Health management
from .async_partition_health_monitor import AsyncPartitionHealthMonitor

# Main producer classes
from .async_producer import AsyncSmartProducer

# Caching system
from .caching import (
    CacheConfig,
    CacheEntry,
    CacheFactory,
    CacheTimeoutError,
    CacheUnavailableError,
    DefaultHybridCache,
    DefaultLocalCache,
    DefaultRemoteCache,
    HybridCache,
    LocalCache,
    RemoteCache,
)

# Exception classes
from .exceptions import (
    CacheError,
    ConfigurationError,
    HealthManagerError,
    LagDataUnavailableError,
    PartitionSelectionError,
    SmartProducerError,
)

# Configuration
from .health_config import HealthManagerConfig
from .partition_health_monitor import PartitionHealthMonitor
from .producer_config import SmartProducerConfig

# Core protocol interfaces
from .protocols import LagDataCollector
from .sync_producer import SmartProducer

# # Threading utilities
# from .threading import (
#     SimpleBackgroundRefresh,
#     create_async_background_task,
#     create_sync_background_refresh,
#     run_periodic_async,
# )

# Default implementations
# from .collectors import KafkaAdminLagCollector
# from .calculators import ThresholdHotPartitionCalculator

__all__ = [
    # Protocols
    "LagDataCollector",
    # "CacheBackend",
    # Exceptions
    "SmartProducerError",
    "LagDataUnavailableError",
    "HealthManagerError",
    "CacheError",
    "PartitionSelectionError",
    "ConfigurationError",
    # Caching system
    "LocalCache",
    "RemoteCache",
    "HybridCache",
    "DefaultLocalCache",
    "DefaultRemoteCache",
    "DefaultHybridCache",
    "CacheConfig",
    "CacheEntry",
    "CacheFactory",
    "CacheTimeoutError",
    "CacheUnavailableError",
    # # Threading utilities
    # "SimpleBackgroundRefresh",
    # "run_periodic_async",
    # "create_async_background_task",
    # "create_sync_background_refresh",
    # Configuration
    "HealthManagerConfig",
    "SmartProducerConfig",
    # Health management
    "PartitionHealthMonitor",
    "AsyncPartitionHealthMonitor",
    # Producer classes
    "SmartProducer",
    "AsyncSmartProducer",
    # Future components
    # "KafkaAdminLagCollector",
    # "ThresholdHotPartitionCalculator",
]
