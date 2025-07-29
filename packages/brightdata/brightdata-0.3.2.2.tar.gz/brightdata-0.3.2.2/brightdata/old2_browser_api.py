# to run:  python -m brightdata.browser_api
"""
brightdata.browser_api  ·  Playwright edition
---------------------------------------------
Async, resource-friendly wrapper around Bright Data’s Browser-API (CDP).

All public helpers return **ScrapeResult** so that the higher-level
`brightdata.auto` helpers work unchanged.

Quick smoke-test:
    python -m brightdata.browser_api
"""
from __future__ import annotations

import asyncio, os, pathlib, time
import logging

logging.getLogger("asyncio").setLevel(logging.INFO)
# suppress filelock’s debug chatter
logging.getLogger("filelock").setLevel(logging.INFO)
# (if you ever see tldextract noise, you can do the same:)
logging.getLogger("tldextract").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


from datetime import datetime
from typing import Any
from dotenv import load_dotenv
from playwright.async_api import (
    async_playwright,
    Page,
    Error as PWError,
    TimeoutError as PWTimeoutError,
)

# ── brightdata imports ───────────────────────────────────────────
from brightdata.models import ScrapeResult
from brightdata.utils import _make_result_browserapi as _mk
from brightdata.playwright_session import PlaywrightSession

# ── module-level defaults ────────────────────────────────────────
DEFAULT_HOST          = "brd.superproxy.io"
DEFAULT_CDP_PORT      = 9222
DEFAULT_WINDOW_SIZE   = (1920, 1080)
DEFAULT_LOAD_STATE    = "domcontentloaded"       # Playwright wait_until

DEFAULT_NAV_TIMEOUT_MS   = 75_000          # ← was NAVIGATION_TIMEOUT_MS
DEFAULT_HYDRATE_WAIT_MS  = 30_000          # ← was MAIN_SELECTOR_WAIT_MS


# ══════════════════════════════════════════════════════════════════
# BrowserAPI
# ══════════════════════════════════════════════════════════════════
class BrowserAPI:
    """
    Thin async wrapper around Bright Data’s Browser-API proxy.

    Parameters
    ----------
    username / password : str | None
        If omitted the constructor falls back to the env vars
        `BRIGHTDATA_BROWSERAPI_USERNAME` / `_PASSWORD`.
    load_state : {"load","domcontentloaded","networkidle","commit"}
        Default Playwright milestone used in `goto`.
    block_resources : bool | list[str]
        • True           → block common heavy assets (png, jpg, woff…)
        • list of globs  → custom patterns, e.g. ["**/*.png","**/*.css"]
        • False / []     → no interception.
    enable_multihydration_selector_fallback : bool
        Try several CSS selectors when waiting for “page is hydrated”.
    enable_networkidle_hydration_sign : bool
        Skip CSS selectors entirely – rely on `wait_until="networkidle"`.
    """

    # ───────── constructor ─────────────────────────────────────────
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_CDP_PORT,
        window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
        load_state: str = DEFAULT_LOAD_STATE,
        navigation_timeout_ms: int  = DEFAULT_NAV_TIMEOUT_MS,
        hydration_wait_ms:   int    = DEFAULT_HYDRATE_WAIT_MS,
        block_resources: bool | list[str] = True,
        enable_multihydration_selector_fallback: bool = True,
        enable_networkidle_hydration_sign: bool = False,
        
    ):
        load_dotenv()

        self.username = username or os.getenv("BRIGHTDATA_BROWSERAPI_USERNAME")
        self.password = password or os.getenv("BRIGHTDATA_BROWSERAPI_PASSWORD")
        if not (self.username and self.password):
            raise ValueError(
                "Provide Browser-API credentials via env vars or constructor."
            )
        

                   

        self.host, self.port          = host, port
        self.window_size              = window_size
        self._nav_timeout           = navigation_timeout_ms
        self._hydration_wait        = hydration_wait_ms
        self._default_load_state      = load_state
        self._use_multi_hydration     = enable_multihydration_selector_fallback
        self._use_networkidle_sign    = enable_networkidle_hydration_sign

        # Selector registry is *mutable* – callers may insert site-specific hooks
        self.hydration_selectors: list[str] = [
            "#main",                   # placed first for compatibility
            "div#__next",              # Next.js
            "div[data-reactroot]",     # React generic
            "body > *:not(script)",    # “anything inside <body>”
        ]

        self._block_patterns: list[str] = (
            ["**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf,otf}"]
            if block_resources is True
            else (block_resources or [])
        )

        self._session: PlaywrightSession | None = None   # created lazily

    # ───────── internal helpers ────────────────────────────────────
    async def _open_page(self) -> Page:

        logger.debug("▶ _open_page start — session exists? %s", self._session is not None)
        """Fresh incognito context + tab behind Bright Data."""
        if self._session is None:
            logger.debug("   no session, calling PlaywrightSession.get()")
            self._session = await PlaywrightSession.get(
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                # window_size=self.window_size
            )
            logger.debug("   PlaywrightSession.get() returned %r", self._session)


        # return await self._session.new_page(
        logger.debug("   calling new_page() on session")
        page = await self._session.new_page(
            headless=True,
            window_size=self.window_size,
        )
        
        logger.debug("✔ _open_page end — got page %r", page)
        return page
    
    async def _perform_navigation(self, url: str, *, load_state: str | None):
        logger.debug("▶ _perform_navigation start: url=%r load_state=%r", url, load_state)
        page = await self._open_page()
        warmed_at = datetime.utcnow()               # ← browser is now hot
    
        # ── resource blocking (optional) ────────────────────────────
        if self._block_patterns:
            async def _block(route): await route.abort()
            for pat in self._block_patterns:
                await page.route(pat, _block)

        # ── actual navigation ───────────────────────────────────────
        sent_at   = datetime.utcnow()
        wait_until = (
            "networkidle"
            if self._use_networkidle_sign
            else (load_state or self._default_load_state)
        )
        
        t0 = time.time()
        logger.debug("→ goto %r (wait_until=%r)", url, wait_until)
        
        await page.goto(url, timeout=self._nav_timeout, wait_until=wait_until)
        
        elapsed = time.time() - t0
        logger.debug("← goto %r (wait_until=%r) took %.2fs", url, wait_until, elapsed)
        
        return page, warmed_at, sent_at

    async def _navigate_and_collect(
        self,
        url: str,
        wait_for_main: bool | int,
        *,
        load_state: str | None,
    ):
        """
        Returns  (html, sent_at, recv_at, warning_msg)
        warning_msg is None on perfect success or a note on soft failures.
        """
        page, warmed_at, sent_at = await self._perform_navigation(url, load_state=load_state)

        try:
            # ── optional hydration wait ─────────────────────────────
            if wait_for_main and not self._use_networkidle_sign:
                timeout_ms = (
                    wait_for_main * 1_000
                    if isinstance(wait_for_main, int)
                    else self._hydration_wait
                )

                logger.debug(
                    "hydration wait enabled: waiting up to %sms for selectors %r",
                    timeout_ms,
                    self.hydration_selectors)
                
                if self._use_multi_hydration:
                    # CSS :is() will match the first selector to appear
                    # grouped = ":is(" + ",".join(self.hydration_selectors) + ")"
                    # await page.wait_for_selector(grouped, timeout=timeout_ms)


                    for sel in self.hydration_selectors:
                        logger.debug("→ waiting for selector %r", sel)
                        start = time.time()
                        try:
                            await page.wait_for_selector(sel, timeout=timeout_ms)
                            took = (time.time() - start) * 1_000
                            logger.debug("✔ selector %r appeared after %.0fms", sel, took)
                            break
                        except PWTimeoutError:
                            logger.debug("✗ selector %r timed out after %sms", sel, timeout_ms)
                    else:
                        logger.debug("⚠ none of the hydration selectors appeared; continuing")

                else:
                    sel = self.hydration_selectors[0]
                    logger.debug("→ waiting for single selector %r", sel)
                    await page.wait_for_selector(sel, timeout=timeout_ms)

                
                # else:
                #     await page.wait_for_selector(self.hydration_selectors[0], timeout=timeout_ms)
            
            html    = await page.content()
            recv_at = datetime.utcnow()
            # return html, sent_at, recv_at, None
            return html, warmed_at, sent_at, recv_at, None

        except PWTimeoutError as e:
            html    = await page.content()
            recv_at = datetime.utcnow()
            note    = f"wait_for_selector timeout ({e}). Returned partial HTML."
            return html, warmed_at, sent_at, recv_at, note

        finally:
            await page.context.close()

    async def _goto(
        self,
        url: str,
        wait_for_main: bool | int,
        *,
        load_state: str | None = None,
    ) -> ScrapeResult:
        
        logger.debug("▶ _goto start: url=%r wait_for_main=%s load_state=%r", url, wait_for_main, load_state)
        try:
            html, warmed_at,sent_at, recv_at, warn = await self._navigate_and_collect(
                url, wait_for_main, load_state=load_state
            )
            logger.debug("✔ _goto end: url=%r", url)
            return _mk(
                url,
                success=html is not None,
                status="ready",
                data=html,
                error=warn,
                request_sent_at=sent_at,
                browser_warmed_at=warmed_at,
                data_received_at=recv_at,
            )
        except PWError as e:
            return _mk(url, success=False, status="error", error=str(e))
        except Exception as e:
            return _mk(url, success=False, status="error", error=str(e))
    
    # ───────── public async API ─────────────────────────────────────
    async def get_page_source_async(self, url: str, *, load_state: str | None = None):
        return await self._goto(url, wait_for_main=False, load_state=load_state)
     
    async def get_page_source_with_a_delay_async(
        self,
        url: str,
        wait_time_in_seconds: int = 25,
        *,
        load_state: str | None = None,
    ):
        logger.debug("▶ get_page_source_with_a_delay_async start: url=%r ", url,)
        return await self._goto(
            url, wait_for_main=wait_time_in_seconds, load_state=load_state
        )

    async def capture_screenshot_async(
        self,
        url: str,
        path: str | pathlib.Path,
        wait_for_main: bool | int = False,
        *,
        load_state: str | None = None,
    ):
        res = await self._goto(url, wait_for_main, load_state=load_state)
        if not res.success:
            return res
        
        page, _ = await self._perform_navigation(url, load_state=load_state)
        if wait_for_main and not self._use_networkidle_sign:
            try:
                timeout = (
                    wait_for_main * 1_000 if isinstance(wait_for_main, int) else self._hydration_wait
                )
                await page.wait_for_selector(self.hydration_selectors[0], timeout=timeout)
            except PWTimeoutError:
                pass

        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(path), full_page=True)
        await page.context.close()

        return _mk(url, success=True, status="ready", data=str(path))

    # ───────── sync wrappers for convenience ───────────────────────
    def get_page_source(self, url: str, *, load_state: str | None = None):
        # return asyncio.run(self.get_page_source_async(url, load_state=load_state))
        # res = asyncio.run(self.get_page_source_async(url, load_state=load_state))
        # try:
        #     asyncio.run(self.close())
        # except:
        #     pass
        # return res
        try:
            return asyncio.run(self.get_page_source_async(url, load_state=load_state))
        finally:
            # always close the session
            asyncio.run(self.close())


    def get_page_source_with_a_delay( self, url: str, wait_time_in_seconds: int = 25, *, load_state: str | None = None
    ):
        logger.debug( "inside  get_page_source_with_a_delay" )

        try:
            return asyncio.run(
                self.get_page_source_with_a_delay_async(
                    url, wait_time_in_seconds, load_state=load_state
                )
            )
        finally:
            asyncio.run(self.close())

        # res = asyncio.run(
           
        #     self.get_page_source_with_a_delay_async(
        #         url, wait_time_in_seconds, load_state=load_state
        #     )
        # )

        # try:
        #     asyncio.run(self.close())
        # except:
        #     pass
        # return res

    def capture_screenshot(
        self,
        url: str,
        path: str | pathlib.Path,
        wait_for_main: bool | int = False,
        *,
        load_state: str | None = None,
    ):
        return asyncio.run(
            self.capture_screenshot_async(
                url, path, wait_for_main=wait_for_main, load_state=load_state
            )
        )

    # ───────── tidy-up ──────────────────────────────────────────────
    async def close(self):
        # if self._session:
        #     await self._session.close()
        #     self._session = None

        if self._session:
            await self._session.context.close()
            self._session = None
        # now tear down the underlying browser/CDP session
        from brightdata.playwright_session import PlaywrightSession
        await PlaywrightSession.close_all()


# ══════════════════════════════════════════════════════════════════
# Smoke-test  ( python -m brightdata.browser_api )
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":  # pragma: no cover


    logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s  %(message)s",
)
    


    import pprint, sys
     
    async def _demo() -> None:
        url = "https://openai.com"
        api  = BrowserAPI(
            enable_multihydration_selector_fallback=True,
            enable_networkidle_hydration_sign=False,
        )
        
        t0 = time.time()
        res = await api.get_page_source_with_a_delay_async(url, 25)
        t1 = time.time()

        pprint.pprint(
            {
                "success": res.success,
                "status":  res.status,
                "root":    res.root_domain,
                "err":     res.error,
                "snippet": (res.data or "")[:400],
                "elapsed": round(t1 - t0, 3),
            }
        )
        await api.close()
    
    asyncio.run(_demo())




