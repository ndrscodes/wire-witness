from dataclasses import dataclass
from typing import Optional, Self

from errors import ErrorMixin


@dataclass
class PingResult(ErrorMixin):
    packet_loss: float = 0.0
    min_latency: float = 0.0
    avg_latency: float = 0.0
    max_latency: float = 0.0
    host: Optional[str] = None
    ip: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            packet_loss=data.get("packet_loss", 0.0),
            min_latency=data.get("min_latency", 0.0),
            avg_latency=data.get("avg_latency", 0.0),
            max_latency=data.get("max_latency", 0.0),
            host=data.get("host"),
            ip=data.get("ip"),
        )
