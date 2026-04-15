import os
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

load_dotenv()

def load_config(config_path: str = "config.json") -> dict:
    """Load settings from a JSON config file."""
    with open(config_path, "r") as f:
        return json.load(f)

def load_credentials() -> tuple[str, str]:
    """Load credentials from environment variables."""
    username = os.getenv("VFS_USERNAME")
    password = os.getenv("VFS_PASSWORD")
    if not username or not password:
        raise ValueError(
            "Missing credentials. Set VFS_USERNAME and VFS_PASSWORD in your .env file."
        )
    return username, password

def setup_logger(logs_dir: str, session_id: str) -> logging.Logger:
    """Configure logging to both console and a timestamped log file."""
    Path(logs_dir).mkdir(exist_ok=True)
    log_file = Path(logs_dir) / f"session_{session_id}.log"

    logger = logging.getLogger("vfs_automation")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  [%(levelname)s]  %(message)s", "%H:%M:%S")

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info(f"Log file: {log_file}")
    return logger



def run_login(headless: bool, config: dict, logger: logging.Logger, session_id: str):
    """Core login automation function."""

    username, password = load_credentials()

    screenshots_dir = config.get("screenshots_dir", "screenshots")
    Path(screenshots_dir).mkdir(exist_ok=True)

    timeout = config.get("timeout", 30000)
    viewport = config.get("viewport", {"width": 1280, "height": 800})
    url = config["url"]
    homepage = config.get("homepage", url)

    mode = "HEADLESS" if headless else "HEADED"
    logger.info(f"Starting login automation in {mode} mode")
    logger.info(f"Target URL: {url}")

    with sync_playwright() as p:

        
        browser = p.chromium.launch(
            headless=headless,
            slow_mo=60,  
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport=viewport,
            locale="en-US",
            timezone_id="Europe/London",
        )

        page = context.new_page()

        try:
            
            logger.info("Visiting homepage first (warm-up)...")
            page.goto(homepage, timeout=timeout, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)

            
            logger.info("Navigating to login page...")
            page.goto(url, timeout=timeout, wait_until="networkidle")
            page.wait_for_timeout(1000)

            
            logger.info("Waiting for login form...")
            page.wait_for_selector("#username", timeout=timeout)

            
            page.mouse.move(400, 300)
            page.wait_for_timeout(500)

            
            logger.info("Entering username...")
            page.click("#username")
            page.type("#username", username, delay=80)   
            page.wait_for_timeout(500)

            logger.info("Entering password...")
            page.click("#password")
            page.type("#password", password, delay=80)
            page.wait_for_timeout(500)

            
            logger.info("Clicking Login button...")
            page.click("#submit")

            
            logger.info("Waiting for page to load after login...")
            try:
                page.wait_for_load_state("networkidle", timeout=timeout)
            except PlaywrightTimeoutError:
                pass  
            page.wait_for_timeout(1500)  

            
            current_url = page.url
            page_content = page.content()

            
            success_url_fragment = "logged-in-successfully"
            success_text = "Congratulations"

            if success_url_fragment in current_url or success_text in page_content:
                logger.info("LOGIN SUCCESSFUL")
                status = "success"
            else:
                
                try:
                    error_el = page.query_selector("#error")
                    error_msg = error_el.inner_text() if error_el else "Unknown error"
                except Exception:
                    error_msg = "Could not read error message"
                logger.error(f"LOGIN FAILED — {error_msg}")
                status = "failed"

        
            screenshot_path = (
                Path(screenshots_dir) / f"login_{status}_{session_id}.png"
            )
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Screenshot saved → {screenshot_path}")

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout error: {e}")
            page.screenshot(path=str(Path(screenshots_dir) / f"timeout_{session_id}.png"))
            logger.info("Timeout screenshot saved.")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            try:
                page.screenshot(
                    path=str(Path(screenshots_dir) / f"error_{session_id}.png")
                )
            except Exception:
                pass

        finally:
            if not headless:
                input("\nPress ENTER to close the browser...")
            browser.close()
            logger.info("Browser closed. Session complete.")



def main():
    parser = argparse.ArgumentParser(description="VFS Login Automation")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless (background) mode",
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config file (default: config.json)",
    )
    args = parser.parse_args()

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    config = load_config(args.config)
    logger = setup_logger(config.get("logs_dir", "logs"), session_id)

    run_login(
        headless=args.headless,
        config=config,
        logger=logger,
        session_id=session_id,
    )


if __name__ == "__main__":
    main()
