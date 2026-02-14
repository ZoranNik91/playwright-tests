from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pathlib import Path
from urllib.parse import urlparse
import logging
import requests


class ReversingLabsPage:
    HOME_URL = "https://www.reversinglabs.com/"

    def __init__(self, page):
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def go_to_website(self, url: str):
        self.page.goto(url)
        self.log_page_opened(url)

    def click_by_selector_and_text(self, selector: str, text: str):
        loc = self.page.locator(selector, has_text=text).first
        loc.click()
        self.log_clicked(text)

    def is_visible_by_selector_and_text(self, selector: str, text: str):
        loc = self.page.locator(selector, has_text=text).first
        loc.wait_for(state="visible")
        visible = loc.is_visible()
        self.log_visible(text)
        return visible

    def assert_text_contains(self, selector: str, text: str):
        actual = self.page.locator(selector).first.inner_text()
        assert text in actual
        self.log_assert(text, selector)

    def ensure_dir(self, path: str | Path) -> Path:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def locator_by_selector_and_text(self, selector: str, text: str):
        return self.page.locator(selector, has_text=text).first

    def href_from_locator(self, locator) -> str:
        return (locator.get_attribute("href") or "").strip()

    def resolve_filename(
        self,
        filename: str | None = None,
        *,
        suggested: str | None = None,
        href: str | None = None,
    ) -> str:
        if filename:
            return filename
        if suggested:
            return suggested
        if href:
            name = Path(urlparse(href).path).name
            if name:
                return name
        return "downloaded_file"

    def download_via_playwright(
        self,
        locator,
        timeout_ms: int,
        out_dir: Path,
        filename: str,
        before_pages: list,
    ) -> tuple[Path, str]:
        ctx = self.page.context
        with self.page.expect_download(timeout=timeout_ms) as dl_info:
            locator.click()

            # Check new tab before 'Download started' log
            after_pages = list(ctx.pages)
            self.log_new_tab_opened_title(before_pages, after_pages)

        download = dl_info.value
        out_name = self.resolve_filename(filename, suggested=download.suggested_filename)
        out_path = out_dir / out_name

        self.log_download_started(out_name)
        download.save_as(str(out_path))
        self.log_saved(out_name, out_path)

        return out_path, download.url

    def download_via_http(self, href: str, out_dir: Path, filename: str, timeout_ms: int) -> tuple[Path, str]:
        out_name = self.resolve_filename(filename, href=href)
        out_path = out_dir / out_name

        self.log_download_fallback(out_name)
        self.log_download_started_http(out_name)

        timeout_s = max(5, int(timeout_ms / 1000))
        r = requests.get(href, timeout=timeout_s)
        r.raise_for_status()
        out_path.write_bytes(r.content)

        self.log_saved(out_name, out_path)
        return out_path, href

    def download_file_by_selector_and_text(
        self,
        selector: str,
        text: str,
        download_dir: str | Path,
        *,
        timeout_ms: int = 5000,
        filename: str | None = None,
    ) -> tuple[Path, str]:

        out_dir = self.ensure_dir(download_dir)

        loc = self.locator_by_selector_and_text(selector, text)
        loc.wait_for(state="visible", timeout=timeout_ms)

        self.log_clicked(text)

        href = self.href_from_locator(loc)
        ctx = self.page.context
        before_pages = list(ctx.pages)

        try:
            return self.download_via_playwright(
                loc,
                timeout_ms=timeout_ms,
                out_dir=out_dir,
                filename=filename,
                before_pages=before_pages,
            )
        except PlaywrightTimeoutError:
            if not href:
                raise
            return self.download_via_http(href=href, out_dir=out_dir, filename=filename, timeout_ms=timeout_ms)

    def remove_file_if_exists(self, file_path: str | Path) -> bool:
        p = Path(file_path)
        if p.exists():
            self.log_file_removed(p.name)
            p.unlink()
            return True

        self.log_no_file_found(p.name)
        return False

    def get_link_href(self, selector: str, text: str | None = None) -> str:
        locator = (
            self.page.locator(selector, has_text=text).first
            if text
            else self.page.locator(selector).first
        )
        href = locator.get_attribute("href")
        return (href or "").strip()

    # Logging output methods
    def log_clicked(self, text: str):
        self.logger.debug('Clicked on: "%s"', text)

    def log_visible(self, text: str):
        self.logger.debug('"%s" is visible', text)

    def log_page_opened(self, url: str):
        self.logger.debug('Opened web page: "%s"', url)

    def log_new_tab(self, text: str):
        self.logger.debug('New tab opened: "%s"', text)

    def log_download_started(self, name: str):
        self.logger.debug('Download started: "%s"', name)

    def log_file_removed(self, text: str):
        self.logger.debug('Existing file removed: "%s"', text)

    def log_no_file_found(self, text: str):
        self.logger.debug('No existing file found: "%s"', text)

    def log_download_fallback(self, name: str):
        self.logger.debug('Download can\'t start, switching via HTTP: "%s"', name)

    def log_download_started_http(self, name: str):
        self.logger.debug('Download started via HTTP: "%s"', name)

    def log_saved(self, name: str, path: Path):
        self.logger.debug('"%s" successfully saved in: "%s"', name, path)

    def log_assert(self, name: str, selector: str):
        self.logger.debug('Asserted text contains "%s" on selector "%s"', name, selector)

    def log_new_tab_opened_title(self, before_pages: list, after_pages: list):
        if len(after_pages) <= len(before_pages):
            return
        new_pages = [p for p in after_pages if p not in before_pages]
        new_page = new_pages[-1] if new_pages else after_pages[-1]
        try:
            title = (new_page.title() or "").strip()
        except Exception:
            title = ""
        if title:
            self.log_new_tab(title)

