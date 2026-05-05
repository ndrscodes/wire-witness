from models.iperf_models import IperfResult
from models.speedtest_models import SpeedtestResult
from influxdb_client_3 import InfluxDBClient3, Point, write_client_options, WriteOptions
import logging
from config import Config

logger = logging.getLogger(__name__)

class InfluxClient:
    def __init__(self, host, organization, database, token):
        opts = WriteOptions(retry_interval=Config.RETRY_INTERVAL, max_retry_delay=Config.MAX_RETRY_DELAY, max_retry_time=Config.MAX_RETRY_TIME)
        wco = write_client_options(write_options=opts)
        self.client = InfluxDBClient3(host, organization, database, token, write_client_options=wco)

    def push(self, data: IperfResult | SpeedtestResult):
        if isinstance(data, IperfResult):
            points = iperf_to_point(data)
        elif isinstance(data, SpeedtestResult):
            points = speedtest_to_point(data)
        else:
            logger.warning(f"received unknown data type: {type(data).__name__}")
            return

        self.client.write(points)

def speedtest_to_point(data: SpeedtestResult) -> list[Point]:
    records = []

    result_point = (
        Point("speedtest_result")
        .time(data.timestamp)
        .tag("type", data.type)
        .tag("isp", data.isp)
        .tag("country", data.server.country)
        .tag("server_name", data.server.name)
        .tag("server_location", data.server.location)
        .tag("interface_name", data.interface.name)
        .tag("interface_is_vpn", str(data.interface.is_vpn))
        .tag("result_id", data.result.id)
        .tag("result_url", data.result.url)
        .field("packet_loss", data.packet_loss)
        .field("ping_latency", data.ping.latency)
        .field("ping_low", data.ping.low)
        .field("ping_high", data.ping.high)
        .field("ping_jitter", data.ping.jitter)
        .field("download_bandwidth", data.download.bandwidth)
        .field("download_bytes", data.download.bytes)
        .field("download_elapsed", data.download.elapsed)
        .field("download_latency_iqm", data.download.latency.iqm)
        .field("download_latency_low", data.download.latency.low)
        .field("download_latency_high", data.download.latency.high)
        .field("download_latency_jitter", data.download.latency.jitter)
        .field("upload_bandwidth", data.upload.bandwidth)
        .field("upload_bytes", data.upload.bytes)
        .field("upload_elapsed", data.upload.elapsed)
        .field("upload_latency_iqm", data.upload.latency.iqm)
        .field("upload_latency_low", data.upload.latency.low)
        .field("upload_latency_high", data.upload.latency.high)
        .field("upload_latency_jitter", data.upload.latency.jitter)
    )
    records.append(result_point)

    return records

def iperf_to_point(data: IperfResult) -> list[Point]:
    records = []

    connecting_to = data.start.connecting_to
    server_host = connecting_to.get("host", "unknown")
    server_port = connecting_to.get("port", 0)
    
    local_host = "unknown"
    local_port = 0
    if data.start.connected:
        local_host = data.start.connected[0].local_host
        local_port = data.start.connected[0].local_port

    result_point = (
        Point("iperf_result")
        .tag("server_host", server_host)
        .tag("server_port", str(server_port))
        .tag("local_host", local_host)
        .tag("local_port", str(local_port))
        .tag("protocol", data.start.test_start.protocol)
        .tag("version", data.start.version)
        .field("num_streams", data.start.test_start.num_streams)
        .field("block_size", data.start.test_start.blksize)
        .field("omit_duration", data.start.test_start.omit)
        .field("test_duration", data.start.test_start.duration)
        .field("interval", data.start.test_start.interval)
        .field("reverse", data.start.test_start.reverse)
        .field("bidirectional", data.start.test_start.bidir)
        .field("socket_buffer_size", data.start.sock_bufsize)
        .field("send_buffer_actual", data.start.snd_buf_actual)
        .field("receive_buffer_actual", data.start.rcv_buf_actual)
        .field("tcp_mss_default", data.start.tcp_mss_default)
        .field("bytes_sent", data.end.sum_sent.bytes)
        .field("bandwidth_sent_bps", data.end.sum_sent.bits_per_second)
        .field("retransmits_sent", data.end.sum_sent.retransmits)
        .field("duration_sent", data.end.sum_sent.seconds)
        .field("bytes_received", data.end.sum_received.bytes)
        .field("bandwidth_received_bps", data.end.sum_received.bits_per_second)
        .field("duration_received", data.end.sum_received.seconds)
        .field("cpu_utilization_host", data.end.cpu_utilization_percent.get("host_total", 0.0))
        .field("cpu_utilization_remote", data.end.cpu_utilization_percent.get("remote_total", 0.0))
    )
    records.append(result_point)

    if len(data.end.streams) > 1:
        for idx, stream in enumerate(data.end.streams):
            stream_point = (
                Point("iperf_stream_result")
                .tag("server_host", server_host)
                .tag("server_port", str(server_port))
                .tag("stream_id", str(idx))
                .field("sender_bytes", stream.sender.bytes)
                .field("sender_bandwidth_bps", stream.sender.bits_per_second)
                .field("sender_retransmits", stream.sender.retransmits)
                .field("sender_reorder", stream.sender.reorder)
                .field("sender_max_snd_cwnd", stream.sender.max_snd_cwnd)
                .field("sender_max_snd_wnd", stream.sender.max_snd_wnd)
                .field("sender_max_rtt", stream.sender.max_rtt)
                .field("sender_min_rtt", stream.sender.min_rtt)
                .field("sender_mean_rtt", stream.sender.mean_rtt)
                .field("sender_duration", stream.sender.seconds)
                .field("receiver_bytes", stream.receiver.bytes)
                .field("receiver_bandwidth_bps", stream.receiver.bits_per_second)
                .field("receiver_duration", stream.receiver.seconds)
            )
            records.append(stream_point)

    return records