from models.ping_models import PingResult
from probers import UnixPingParser, WindowsPingParser


# --- UnixPingParser Tests ---


def test_unix_parser_success():
    """Test that UnixPingParser correctly deserializes valid Unix ping output into a PingResult instance."""
    parser = UnixPingParser("example.com")

    ping_output = """PING example.com (93.184.216.34): 56 data bytes

--- example.com ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 10.123/15.456/20.789/3.211 ms"""

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "example.com"
    assert result.ip == "93.184.216.34"
    assert result.packet_loss == 0.0
    assert result.min_latency == 10.123
    assert result.avg_latency == 15.456
    assert result.max_latency == 20.789


def test_unix_parser_with_packet_loss():
    """Test that UnixPingParser correctly parses ping output with packet loss."""
    parser = UnixPingParser("lossy-host.com")

    ping_output = """PING lossy-host.com (10.0.0.1): 56 data bytes

--- lossy-host.com ping statistics ---
10 packets transmitted, 7 packets received, 30.0% packet loss
round-trip min/avg/max/stddev = 5.000/12.500/25.000/5.555 ms"""

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "lossy-host.com"
    assert result.ip == "10.0.0.1"
    assert result.packet_loss == 30.0
    assert result.min_latency == 5.0
    assert result.avg_latency == 12.5
    assert result.max_latency == 25.0


def test_unix_parser_without_stddev():
    """Test that UnixPingParser correctly parses ping output without stddev in latency line."""
    parser = UnixPingParser("example.com")

    ping_output = """PING example.com (93.184.216.34): 56 data bytes

--- example.com ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max = 10.123/15.456/20.789 ms
"""

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "example.com"
    assert result.ip == "93.184.216.34"
    assert result.packet_loss == 0.0
    assert result.min_latency == 10.123
    assert result.avg_latency == 15.456
    assert result.max_latency == 20.789


def test_unix_parser_invalid_output_too_few_lines():
    """Test that UnixPingParser returns PingResult with error when output has too few lines."""
    parser = UnixPingParser("example.com")

    ping_output = "only two\nlines"

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
    assert result.host == "example.com"


def test_unix_parser_unmatched_regex():
    """Test that UnixPingParser returns PingResult with error when regex patterns don't match."""
    parser = UnixPingParser("example.com")

    ping_output = """random garbage output
that does not match ping format
at all"""

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
    assert result.host == "example.com"


# --- WindowsPingParser Tests ---


def test_windows_parser_success():
    """Test that WindowsPingParser correctly deserializes valid Windows ping output into a PingResult instance."""
    parser = WindowsPingParser("example.com")

    ping_output = """
Pinging example.com [93.184.216.34] with 32 bytes of data:
Reply from 93.184.216.34: bytes=32 time=14ms TTL=55
Reply from 93.184.216.34: bytes=32 time=12ms TTL=55
Reply from 93.184.216.34: bytes=32 time=13ms TTL=55

Ping statistics for 93.184.216.34
    Packets: Sent = 3, Received = 3, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 12ms, Maximum = 14ms, Average = 13ms
""".strip()

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "example.com"
    assert result.ip == "93.184.216.34"
    assert result.packet_loss == 0.0
    assert result.min_latency == 12
    assert result.avg_latency == 13
    assert result.max_latency == 14


def test_windows_parser_with_packet_loss():
    """Test that WindowsPingParser correctly parses ping output with packet loss."""
    parser = WindowsPingParser("lossy-host.com")

    ping_output = """
Pinging lossy-host.com [10.0.0.1] with 32 bytes of data:
Reply from 10.0.0.1: bytes=32 time=5ms TTL=64
Reply from 10.0.0.1: bytes=32 time=10ms TTL=64
Request timed out.

Ping statistics for 10.0.0.1
    Packets: Sent = 3, Received = 2, Lost = 1 (33% loss),
Approximate round trip times in milli-seconds:
    Minimum = 5ms, Maximum = 10ms, Average = 7ms
""".strip()

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "lossy-host.com"
    assert result.ip == "10.0.0.1"
    assert result.packet_loss == 33.0
    assert result.min_latency == 5
    assert result.avg_latency == 7
    assert result.max_latency == 10


def test_windows_parser_without_ip_in_host_line():
    """Test that WindowsPingParser handles host line without IP in brackets (IP address as host)."""
    parser = WindowsPingParser("10.0.0.1")

    ping_output = """
Pinging 10.0.0.1 with 32 bytes of data:
Reply from 10.0.0.1: bytes=32 time=5ms TTL=64
Reply from 10.0.0.1: bytes=32 time=10ms TTL=64

Ping statistics for 10.0.0.1
    Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 5ms, Maximum = 10ms, Average = 7ms
""".strip()

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "10.0.0.1"
    assert result.ip == "10.0.0.1"
    assert result.packet_loss == 0.0
    assert result.min_latency == 5
    assert result.avg_latency == 7
    assert result.max_latency == 10


def test_windows_parser_invalid_output_too_few_lines():
    """Test that WindowsPingParser returns PingResult with error when output has too few lines."""
    parser = WindowsPingParser("example.com")

    ping_output = "only two\nlines"

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
    assert result.host == "example.com"


def test_windows_parser_unmatched_regex():
    """Test that WindowsPingParser returns PingResult with error when regex patterns don't match."""
    parser = WindowsPingParser("example.com")

    ping_output = """random garbage output
that does not match ping format
at all"""

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
    assert result.host == "example.com"


def test_windows_parser_missing_latency_info():
    """Test that WindowsPingParser returns error when latency line doesn't match."""
    parser = WindowsPingParser("example.com")

    ping_output = """
Pinging example.com [93.184.216.34] with 32 bytes of data:
Reply from 93.184.216.34: bytes=32 time=14ms TTL=55

Ping statistics for 93.184.216.34
    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
Some random line without latency data
""".strip()

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error


def test_windows_parser_missing_host_info():
    """Test that WindowsPingParser returns error when host line doesn't match."""
    parser = WindowsPingParser("example.com")

    ping_output = """
random output without host info
with 32 bytes of data:
Reply from somewhere: bytes=32 time=14ms TTL=55

Ping statistics for somewhere
    Packets: Sent = 1, Received = 1, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 5ms, Maximum = 10ms, Average = 7ms
""".strip()

    result = parser.parse(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
