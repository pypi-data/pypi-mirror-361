"""
HyperFabric Interconnect - A breakthrough protocol architecture for ultra-low-latency,
high-bandwidth interconnects powering AI superclusters and quantum simulation networks.

Author: Krishna Bajpai
Email: bajpaikrishna715@gmail.com
License: MIT
"""

from .protocol import HyperFabricProtocol
from .nodes import NodeSignature, HardwareType
from .routing import RoutingEngine, RoutingStrategy
from .buffers import ZeroCopyBuffer, BufferManager
from .topology import TopologyManager, FabricZone
from .exceptions import (
    HyperFabricError,
    NodeNotFoundError,
    RoutingError,
    BufferError,
    TopologyError,
)

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    "HyperFabricProtocol",
    "NodeSignature",
    "HardwareType",
    "RoutingEngine",
    "RoutingStrategy",
    "ZeroCopyBuffer",
    "BufferManager",
    "TopologyManager",
    "FabricZone",
    "HyperFabricError",
    "NodeNotFoundError",
    "RoutingError",
    "BufferError",
    "TopologyError",
    "__version__",
]
