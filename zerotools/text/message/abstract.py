from abc import ABC, abstractmethod


class Serializable(ABC):
    @abstractmethod
    def encode(self, offset=0):
        ...
