from abc import ABC, abstractmethod
from typing import List
from models import Alert, User
from crud import create_delivery_log
from datetime import datetime
from database import SessionLocal

class DeliveryStrategy(ABC):
    @abstractmethod
    def deliver(self, alert: Alert, users: List[User]):
        pass

class InAppDelivery(DeliveryStrategy):
    def deliver(self, alert: Alert, users):
        db = SessionLocal()
        results = []
        for u in users:
            nd = create_delivery_log(db, alert.id, u.id)
            results.append(nd)
        db.close()
        return results

class DeliveryContext:
    def __init__(self, strategy: DeliveryStrategy):
        self.strategy = strategy

    def send(self, alert: Alert, users):
        return self.strategy.deliver(alert, users)
