from datetime import timedelta

from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession, SQLiteBackend


class AsyncHttpClient:
    """Handles asynchronous HTTP requests with optional caching."""

    def __init__(
        self, use_cache: bool = True, cache_expire_after: timedelta = timedelta(hours=1)
    ) -> None:
        """
        Initialize configuration but don't create the session yet.

        Unlike sync resources, async resources should be explicitly opened/closed
        using async methods, as they often require event loop integration.
        The actual session is created in the open() method.
        """
        self._session: ClientSession | CachedSession | None = None

        self._is_open: bool = False
        self._use_cache = use_cache
        self._cache_expire_after = cache_expire_after

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en,es-ES;q=0.9,es;q=0.8",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }

    async def open(self) -> None:
        """
        Initializes the async session if it is not already open.

        Unlike the sync version where session creation happens in __init__,
        async resources require explicit opening so they can be properly
        integrated with the event loop.
        """

        # Early return if already open
        if self._is_open:
            return

        # Create the appropriate session based on config
        if self._use_cache:
            self._session = CachedSession(
                cache=SQLiteBackend(
                    cache_name="licitpy_async", expire_after=self._cache_expire_after
                ),
                headers=self.headers,
                allowed_codes=[200],
            )
        else:
            self._session = ClientSession(headers=self.headers)

        # Mark as open
        self._is_open = True

    @property
    def session(self) -> ClientSession | CachedSession:
        """Returns the active async session, raising an error if not open."""
        if not self._is_open or self._session is None:
            raise RuntimeError(
                "HTTP session not initialized. Use one of these options:\n"
                "1. Context manager: 'async with Licitpy() as client:'\n"
                "2. Manual init: 'await client.ensure_open()'"
            )
        return self._session

    async def close(self) -> None:
        """Closes the async session if it exists and is open."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._is_open = False

    async def get_html_by_url(self, url: str) -> str:
        async with self.session.get(url) as response:
            return await response.text()
