from probers import ProberInterface
from influx import InfluxClient
from models.iperf_models import IperfResult
from models.speedtest_models import SpeedtestResult
from models.ping_models import PingResult
import logging

logger = logging.getLogger(__name__)

class SubscriberInterface:
    def update(self, data, id: str | None = None):
        pass

class LogHandler(SubscriberInterface):
    def update(self, data, id: str | None = None):
        if id:
            logger.debug("new measurement collected for test %s: %s", data)
        else:
            logger.debug("new measurement collected: %s", data)

class TaskHandler:
    subscribers: list
    id: str | None = None

    def __init__(self, prober: ProberInterface, id: str | None = None):
        self.subscribers = []
        self.prober = prober
        self.id = id

    def subscribe(self, subscriber: SubscriberInterface):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber: SubscriberInterface):
        self.subscribers.remove(subscriber)
    
    def execute(self):
        data = self.prober.probe()
        for subscriber in self.subscribers:
            subscriber.update(data, self.id)
    
class InfluxHandler(SubscriberInterface):
    def __init__(self, influx_client: InfluxClient):
        self.client = influx_client
    def update(self, data: IperfResult | SpeedtestResult | PingResult, id: str | None = None):
        self.client.push(data, id)