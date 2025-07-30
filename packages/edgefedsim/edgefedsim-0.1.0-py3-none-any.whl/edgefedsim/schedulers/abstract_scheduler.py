from abc import ABC, abstractmethod

class AbstractScheduler(ABC):
    """Abstract base class for custom schedulers."""
    @abstractmethod
    def schedule(self, *args, **kwargs):
        pass
