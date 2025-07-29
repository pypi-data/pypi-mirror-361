from abc import ABC, abstractmethod

from licitpy.core.models import Tender


class BaseTenderProvider(ABC):

    @abstractmethod
    async def get_by_code(self, code: str) -> Tender: ...
