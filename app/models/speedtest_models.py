from dataclasses import dataclass, field
from typing import Any, Self
from errors import ErrorMixin

@dataclass
class PingLatency:
    iqm: float = 0.0
    low: float = 0.0
    high: float = 0.0
    jitter: float = 0.0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iqm=data.get("iqm", 0.0),
            low=data.get("low", 0.0),
            high=data.get("high", 0.0),
            jitter=data.get("jitter", 0.0),
        )

@dataclass
class PingInfo:
    jitter: float = 0.0
    latency: float = 0.0
    low: float = 0.0
    high: float = 0.0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            jitter=data.get("jitter", 0.0),
            latency=data.get("latency", 0.0),
            low=data.get("low", 0.0),
            high=data.get("high", 0.0),
        )

@dataclass
class DownloadLatency:
    iqm: float = 0.0
    low: float = 0.0
    high: float = 0.0
    jitter: float = 0.0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iqm=data.get("iqm", 0.0),
            low=data.get("low", 0.0),
            high=data.get("high", 0.0),
            jitter=data.get("jitter", 0.0),
        )

@dataclass
class DownloadInfo:
    bandwidth: int = 0
    bytes: int = 0
    elapsed: int = 0
    latency: DownloadLatency = field(default_factory=DownloadLatency)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bandwidth=data.get("bandwidth", 0),
            bytes=data.get("bytes", 0),
            elapsed=data.get("elapsed", 0),
            latency=DownloadLatency.from_dict(data.get("latency", {})),
        )

@dataclass
class UploadLatency:
    iqm: float = 0.0
    low: float = 0.0
    high: float = 0.0
    jitter: float = 0.0

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iqm=data.get("iqm", 0.0),
            low=data.get("low", 0.0),
            high=data.get("high", 0.0),
            jitter=data.get("jitter", 0.0),
        )

@dataclass
class UploadInfo:
    bandwidth: int = 0
    bytes: int = 0
    elapsed: int = 0
    latency: UploadLatency = field(default_factory=UploadLatency)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bandwidth=data.get("bandwidth", 0),
            bytes=data.get("bytes", 0),
            elapsed=data.get("elapsed", 0),
            latency=UploadLatency.from_dict(data.get("latency", {})),
        )

@dataclass
class InterfaceInfo:
    internal_ip: str = ""
    name: str = ""
    mac_addr: str = ""
    is_vpn: bool = False
    external_ip: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            internal_ip=data.get("internalIp", ""),
            name=data.get("name", ""),
            mac_addr=data.get("macAddr", ""),
            is_vpn=data.get("isVpn", False),
            external_ip=data.get("externalIp", ""),
        )

@dataclass
class ServerInfo:
    id: int = 0
    host: str = ""
    port: int = 0
    name: str = ""
    location: str = ""
    country: str = ""
    ip: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", 0),
            host=data.get("host", ""),
            port=data.get("port", 0),
            name=data.get("name", ""),
            location=data.get("location", ""),
            country=data.get("country", ""),
            ip=data.get("ip", ""),
        )

@dataclass
class ResultInfo:
    id: str = ""
    url: str = ""
    persisted: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            persisted=data.get("persisted", False),
        )

@dataclass
class SpeedtestResult(ErrorMixin):
    type: str = ""
    timestamp: str = ""
    ping: PingInfo = field(default_factory=PingInfo)
    download: DownloadInfo = field(default_factory=DownloadInfo)
    upload: UploadInfo = field(default_factory=UploadInfo)
    packet_loss: float = 0.0
    isp: str = ""
    interface: InterfaceInfo = field(default_factory=InterfaceInfo)
    server: ServerInfo = field(default_factory=ServerInfo)
    result: ResultInfo = field(default_factory=ResultInfo)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            type=data.get("type", ""),
            timestamp=data.get("timestamp", ""),
            ping=PingInfo.from_dict(data.get("ping", {})),
            download=DownloadInfo.from_dict(data.get("download", {})),
            upload=UploadInfo.from_dict(data.get("upload", {})),
            packet_loss=float(data.get("packetLoss", 0.0)),
            isp=data.get("isp", ""),
            interface=InterfaceInfo.from_dict(data.get("interface", {})),
            server=ServerInfo.from_dict(data.get("server", {})),
            result=ResultInfo.from_dict(data.get("result", {})),
        )
