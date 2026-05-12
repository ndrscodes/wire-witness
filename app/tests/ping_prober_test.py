from config import PingTask
from models.ping_models import PingResult
from probers import PingProber


def _create_prober(host: str = "example.com") -> PingProber:
    """Helper to create a PingProber without requiring an actual ping command."""
    config = PingTask(target_host=host, count=3, schedule="* * * * *")
    return PingProber(config, cmd=None)


def test_parse_output_success():
    """Test that __parse_output correctly deserializes valid ping output into a PingResult instance."""
    prober = _create_prober("example.com")

    # Simulate realistic ping -q (quiet) output
    ping_output = b"""
PING example.com (93.184.216.34): 56 data bytes

--- example.com ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 10.123/15.456/20.789/3.211 ms
""".strip()

    result = prober.parse_output(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "example.com"
    assert result.ip == "93.184.216.34"
    assert result.packet_loss == 0.0
    assert result.min_latency == 10.123
    assert result.avg_latency == 15.456
    assert result.max_latency == 20.789


def test_parse_output_with_packet_loss():
    """Test that __parse_output correctly parses ping output with packet loss."""
    prober = _create_prober("lossy-host.com")

    ping_output = b"""
PING lossy-host.com (10.0.0.1): 56 data bytes

--- lossy-host.com ping statistics ---
10 packets transmitted, 7 packets received, 30.0% packet loss
round-trip min/avg/max/stddev = 5.000/12.500/25.000/5.555 ms
""".strip()

    result = prober.parse_output(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is None
    assert result.host == "lossy-host.com"
    assert result.ip == "10.0.0.1"
    assert result.packet_loss == 30.0
    assert result.min_latency == 5.0
    assert result.avg_latency == 12.5
    assert result.max_latency == 25.0


def test_parse_output_invalid_output_too_few_lines():
    """Test that __parse_output returns PingResult with error when output has too few lines."""
    prober = _create_prober("example.com")

    ping_output = b"only two\nlines"

    result = prober.parse_output(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
    assert result.host == "example.com"


def test_parse_output_unmatched_regex():
    """Test that __parse_output returns PingResult with error when regex patterns don't match."""
    prober = _create_prober("example.com")

    ping_output = b"""
random garbage output
that does not match ping format
at all
""".strip()

    result = prober.parse_output(ping_output)

    assert isinstance(result, PingResult)
    assert result.error is not None
    assert "unexpected ping output" in result.error
    assert result.host == "example.com"
