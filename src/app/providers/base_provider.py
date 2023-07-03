from abc import ABC, abstractmethod

from fastapi import FastAPI


class BaseProvider(ABC):
    def __init__(self, app: FastAPI):
        self.app = app

    @abstractmethod
    async def startup(self):
        """FastAPI startup event"""
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self):
        """FastAPI shutdown event"""
        raise NotImplementedError

    def register_events(self):
        self.app.add_event_handler("startup", self.startup)
        self.app.add_event_handler("shutdown", self.shutdown)
