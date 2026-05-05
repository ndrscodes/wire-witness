from dataclasses import dataclass

@dataclass
class PingResult:
    packet_loss: float
    min_latency: float
    avg_latency: float
    max_latency: float
    host: str | None
    ip: str | None