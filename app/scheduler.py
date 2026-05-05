import logging
import sys
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BlockingScheduler, BaseScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

import config
import handler
import probers
import influx

logger = logging.getLogger(__name__)

def create_scheduler() -> BaseScheduler | None:
    # we do not allow parallel executions as these might influence measurements on other executors.
    executors = {
        "default": ThreadPoolExecutor(max_workers=1)
    }

    influx_client = influx.InfluxClient(
        config.Config.INFLUXDB_HOST,
        config.Config.INFLUXDB_ORG,
        config.Config.INFLUXDB_DATABASE,
        config.Config.INFLUXDB_TOKEN
    )

    scheduler = BlockingScheduler(executors=executors)

    if config.Config.IPERF_CRON_SCHEDULE:
        iperf_task = handler.TaskHandler(prober=probers.IperfProber())
        iperf_task.subscribe(handler.LogHandler())
        iperf_task.subscribe(handler.InfluxHandler(influx_client))
        if iperf_task.ready():
            scheduler.add_job(
                iperf_task.execute,
                CronTrigger.from_crontab(config.Config.IPERF_CRON_SCHEDULE),
                max_instances=1,
                misfire_grace_time=config.Config.MISFIRE_GRACE_TIME,
                name="iperf measurement"
            )
        else:
            logger.warning("Not scheduling iperf handler - handler not ready")
            raise Exception("Iperf handler not ready")
    else:
        logger.warning("Not scheduling iperf handler - no schedule defined")

    if config.Config.SPEEDTEST_CRON_SCHEDULE:
        speedtest_handler = handler.TaskHandler(prober=probers.SpeedtestProber())
        speedtest_handler.subscribe(handler.LogHandler())
        speedtest_handler.subscribe(handler.InfluxHandler(influx_client))
        if speedtest_handler.ready():
            scheduler.add_job(
                speedtest_handler.execute,
                CronTrigger.from_crontab(config.Config.SPEEDTEST_CRON_SCHEDULE),
                max_instances=1,
                misfire_grace_time=config.Config.MISFIRE_GRACE_TIME,
                name="speedtest measurement"
            )
        else:
            logger.warning("Not scheduling speedtest handler - handler not ready")
            raise Exception("Speedtest handler not ready")
    else:
        logger.warning("Not scheduling speedtest handler - no schedule defined")
    
    if config.Config.PING_SCHEDULE:
        ping_handler = handler.TaskHandler(prober=probers.PingProber())
        ping_handler.subscribe(handler.LogHandler())
        ping_handler.subscribe(handler.InfluxHandler(influx_client))
        if ping_handler.ready():
            scheduler.add_job(
                ping_handler.execute,
                CronTrigger.from_crontab(config.Config.PING_SCHEDULE),
                max_instances=1,
                misfire_grace_time=config.Config.MISFIRE_GRACE_TIME,
                name="ping measurement"
            )
        else:
            logger.warning("Not scheduling ping handler - handler not ready")
            raise Exception("Ping handler not ready")
    else:
        logger.warning("Not scheduling ping handler - no schedule defined")

    return scheduler
