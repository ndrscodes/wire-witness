# WireWitness

WireWitness is an automated network performance monitoring tool. It periodically runs network tests and pushes the results to a time-series database so you can visualize exactly what's happening, and when.

## Why WireWitness?

WireWitness solves the problem of "blind spots" in your network monitoring by doing the heavy lifting for you.

By running scheduled speed tests and bandwidth measurements, it helps you hold your ISP accountable by keeping a historical log of your internet speeds over time using the official Ookla Speedtest CLI. 
Beyond the wider internet, you can also use it to monitor your internal network using `iperf3`. 
Finally, WireWitness is designed to be highly flexible and lightweight. 
You can run it locally on a home server, or install it at a remote site and just have it report to your central database. 

Note that `speedtest` mentioned here is the official Ookla Speedtest CLI, not the community `speedtest-cli` tool. Both tools behave differently and create different output, so be sure to use the official Ookla tool if setting up locally. The docker image already uses the correct tool.

## Getting Started: How to Run WireWitness

### Option 1: Docker
Docker compose is the absolute fastest way to get everything running, as it spins up WireWitness, an InfluxDB v3 instance, and Grafana all at once.
The docker image in this repository comes with the `speedtest` CLI and `iperf3` already installed, so you don't have to worry about that.

```bash
docker-compose up -d
```

You can, of course, als run only the WireWitness container and let it send measurements to a remote InfluxDB instance.

``` bash
docker build -t wirewitness:latest .
docker run -d wirewitness:latest
```

See below for more details on how to configure WireWitness.

### Option 2: The Bare-Metal / Local Way
The tool can also be run locally on a Raspberry Pi or any other machine.

1. Ensure you have Python 3 installed on your system.
2. Install the necessary Python packages (`pip install -r requirements.txt`).
3. Make sure `iperf3` and the `speedtest` CLI are installed and accessible on your machine. You can also omit running either tool by not configuring a schedule. Unconfigured tools will be skipped silently.
4. Run the application:

```bash
python main.py
```

Hint: You can always run `python main.py --dry-run` to validate your configuration and ensure everything looks good without actually starting the scheduler.

## Configuration & Options

WireWitness is highly customizable to fit your needs. 
You can configure it using Environment Variables or CLI Arguments (except for some specialized cases). 
If you provide both, the command-line arguments will take priority.

### Database (InfluxDB) Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Host URL** | `INFLUXDB_HOST` | `--influx-host` | The URL where your InfluxDB instance lives. | *Required* |
| **Organization** | `INFLUXDB_ORG` | `--influx-org` | Your InfluxDB organization name. | *Required* |
| **Database** | `INFLUXDB_DATABASE` | `--influx-database` | The target bucket or database for your network metrics. | `wirewitness` |
| **Auth Token** | `INFLUXDB_TOKEN` | `--influx-token` | Your secret authentication token. | *None* |
| **Token File** | `INFLUXDB_TOKEN_FILE` | `--influx-token-file` | Path to a file containing your auth token. | `/run/secrets/influx-admin-token` |
| **Max Retry** | `MAX_RETRY_TIME` | `--max-retry-time` | How long (in milliseconds) to keep trying if the database is temporarily unreachable. | `86400000` (24 hours) |
| **Max Delay** | `MAX_RETRY_DELAY` | `--max-retry-delay` | How long (in milliseconds) to wait before retrying if the database is temporarily unreachable. | `120000` (2 minutes) |
| **Retry Interval** | `RETRY_INTERVAL` | `--retry-interval` | How often (in milliseconds) to retry if the database is temporarily unreachable. | `60` (1 minute) |

### iperf3 Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Target Host** | `IPERF_TARGET_HOST` | `--iperf-host` | The IP address or hostname of your destination iperf3 server. | *None* |
| **Schedule** | `IPERF_CRON_SCHEDULE` | `--iperf-schedule` | When to run the test (uses standard cron syntax, e.g., `*/5 * * * *`). | *None* |
| **Duration** | `IPERF_DURATION` | `--iperf-duration` | How many seconds the speed test should blast traffic across your network. | `10` |
| **Command Path**| `IPERF_CMD` | `--iperf-cmd` | The path to your local iperf3 binary. | Uses the installed `iperf3` binary |
| **Extra Flags** | `IPERF_ADDITIONAL_FLAGS` | *N/A* | Pass extra flags to iperf3. | *None* |

### ping Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Target Host** | `PING_TARGET_HOST` | `--ping-host` | The IP address or hostname you want to ping. | *None* |
| **Schedule** | `PING_CRON_SCHEDULE` | `--ping-schedule` | When to run the test (cron syntax). | *None* |
| **Count** | `PING_COUNT` | `--ping-count` | How many ping packets to send each time. | `5` |
| **Command Path**| `PING_CMD` | `--ping-cmd` | The path to your local ping binary. | Uses the installed `ping` binary |

### Speedtest Settings

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Schedule** | `SPEEDTEST_CRON_SCHEDULE` | `--speedtest-schedule` | When to run the internet speed test (standard cron syntax). | *None* |
| **Accept GDPR** | `SPEEDTEST_GDPR_ACCEPT` | `--accept-speedtest-gdpr` *no value required* | You must accept Ookla's GDPR terms to run the prober. | `False` |
| **Accept License**| `SPEEDTEST_LICENSE_ACCEPT`| `--accept-speedtest-license` *no value required* | You must accept Ookla's License terms to run the prober. | `False` |
| **Command Path**| `SPEEDTEST_CMD` | `--speedtest-cmd` | The path to your Ookla speedtest binary. | Uses the installed `speedtest` binary. |
| **Extra Flags** | `SPEEDTEST_ADDITIONAL_FLAGS`| *N/A* | Target specific servers or interfaces by passing extra flags here (see `speedtest --help`). | *None* |

### Utility Options
A few extra knobs and dials to help you manage the application.

| Configuration | Environment Variable | Command-Line Argument | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| **Grace Time** | `MISFIRE_GRACE_TIME` | `--misfire-grace-time` | Grace period (in seconds) for cron jobs that missed their exact start time. | *None* (allows indefinite delay of tasks, meaning they will be started even if their scheduled time has passed) |
| **Log Level** | *N/A* | `--log-level` | How chatty the application should be (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |
| **Dry Run** | *N/A* | `--dry-run` | Validates your config and exits peacefully without starting the scheduler. | `False` |

## Contributing

I appreciate your interest in helping improve this tool. 
WireWitness is built on the spirit of open source and community collaboration.

If you encounter any bugs or have ideas for new features, please feel free to open an issue or submit a pull request. 
The goal is simply to provide a helpful resource for anyone trying to better understand their network.

## Planned Features

* Local SQL storage for metrics
* Local API to query metrics
* Optional Prometheus integration
* Custom local dashboard for displaying the most relevant metrics
