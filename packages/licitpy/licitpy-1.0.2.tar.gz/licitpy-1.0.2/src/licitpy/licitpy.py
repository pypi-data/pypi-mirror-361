from datetime import timedelta
from types import TracebackType
from typing import Optional, Type

from licitpy.core.http import AsyncHttpClient
from licitpy.countries.cl.provider import ChileProvider


class Licitpy:
    def __init__(
        self,
        use_cache: bool = True,
        cache_expire_after: timedelta = timedelta(hours=1),
    ):
        self._downloader = AsyncHttpClient(
            use_cache=use_cache, cache_expire_after=cache_expire_after
        )

        # Currently only CLProvider is implemented
        self._cl_provider: Optional[ChileProvider] = None

    async def __aenter__(self) -> "Licitpy":
        """Async context manager entry point."""
        await self._downloader.open()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Closes async resources when exiting an async context."""
        await self._downloader.close()

    @property
    def cl(self) -> ChileProvider:
        """Lazy property para el provider de Chile."""
        if self._cl_provider is None:
            self._cl_provider = ChileProvider(self._downloader)

        return self._cl_provider
