from abc import ABC, abstractmethod

from diffr.data_models.diff import FullDiff


class DiffrAlgorithm(ABC):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @abstractmethod
    def diff(self, old: str, new: str) -> FullDiff:
        raise NotImplementedError
