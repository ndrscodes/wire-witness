from probers import ProberInterface
from influx import InfluxClient
from models.iperf_models import IperfResult
from models.speedtest_models import SpeedtestResult
import logging

logger = logging.getLogger(__name__)

class SubscriberInterface:
    def update(self, data):
        pass

class LogHandler(SubscriberInterface):
    def update(self, data):
        logger.debug("new measurement collected: %s", data)

class TaskHandler:
    subscribers: list

    def __init__(self, prober: ProberInterface):
        self.subscribers = []
        self.prober = prober

    def subscribe(self, subscriber: SubscriberInterface):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber: SubscriberInterface):
        self.subscribers.remove(subscriber)
    
    def execute(self):
        data = self.prober.probe()
        for subscriber in self.subscribers:
            subscriber.update(data)
    
class InfluxHandler(SubscriberInterface):
    def __init__(self, influx_client: InfluxClient):
        self.client = influx_client
    def update(self, data: IperfResult | SpeedtestResult):
        self.client.push(data)