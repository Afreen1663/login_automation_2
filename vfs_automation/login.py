import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_sync  

# Load .env
load_dotenv()

#logging - the console and file
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log_filename = LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


#config loader
def load_config(config_path: str = "config.json") -> dict:
    defaults = {
        "url": "https://visa.vfsglobal.com/are/en/mlt/login",
        "homepage": "https://visa.vfsglobal.com",
        "timeout": 60000,
        "screenshot_dir": "screenshots",
        "slow_mo": 100,
        "viewport": {"width": 1280, "height": 800},
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }
    if Path(config_path).exists():
        with open(config_path, "r") as f:
            defaults.update(json.load(f))
        logger.info(f"Config loaded: {config_path}")
    else:
        logger.warning(f"Config '{config_path}' not found — using defaults.")
    return defaults


#credentials - not hardcoded
def load_credentials() -> tuple[str, str]:
    username = os.getenv("VFS_USERNAME")
    password = os.getenv("VFS_PASSWORD")
    if not username or not password:
        logger.error("Set VFS_USERNAME and VFS_PASSWORD in your .env file.")
        sys.exit(1)
    logger.info("Credentials loaded from environment variables.")
    return username, password


#take screenshot
def save_screenshot(page, config: dict, label: str = "result") -> str:
    screenshot_dir = Path(config["screenshot_dir"])
    screenshot_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = screenshot_dir / f"{label}_{timestamp}.png"
    page.screenshot(path=str(path), full_page=False)
    logger.info(f"Screenshot saved: {path}")
    return str(path)


#main login
def run_login(headless: bool = False, config_path: str = "config.json"):
    config = load_config(config_path)
    username, password = load_credentials()

    mode_label = "HEADLESS" if headless else "HEADED"
    logger.info(f"Starting in {mode_label} mode")

    with sync_playwright() as p:

        #browser launch
        browser = p.chromium.launch(
            headless=headless,
            slow_mo=config["slow_mo"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--flag-switches-begin",
                "--disable-site-isolation-trials",
                "--flag-switches-end",
            ],
        )

        
        context = browser.new_context(
            user_agent=config["user_agent"],
            viewport=config["viewport"],
            locale="en-US",
            timezone_id="Europe/London",     # using vpn in case my ip is flagged
            java_script_enabled=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,image/avif,image/webp,*/*;q=0.8"
                ),
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
        )

        page = context.new_page()

        #Apply playwright-stealth - 30+ browser fingerprint vectors that Cloudflare checks
        stealth_sync(page)
        logger.info("Stealth mode applied")

        try:
            # going step by step - first home page 
            logger.info(f"Visiting homepage: {config['homepage']}")
            page.goto(config["homepage"], timeout=config["timeout"])
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            # navigate to Login page
            logger.info(f"Going to login page: {config['url']}")
            page.goto(config["url"], timeout=config["timeout"])

            # Give Cloudflare time to evaluate
            page.wait_for_timeout(5000)

            # Check if we got blocked 
            page_text = page.content().lower()
            if "403" in page_text or "access denied" in page_text or "blocked" in page_text:
                logger.error(
                    "CLOUDFLARE BLOCK DETECTED.\n"
                    "   ➜ Enable a VPN and re-run the script.\n"
                    "   ➜ Recommended: Use a European VPN location (UK, Germany, Italy).\n"
                    "   ➜ Free options: ProtonVPN, Windscribe"
                )
                save_screenshot(page, config, label="cloudflare_blocked")
                return

            #login form
            logger.info("Waiting for login form")
            try:
                page.wait_for_selector(
                    "input[type='email'], input[name='email'], input[id*='email']",
                    timeout=20000,
                )
            except PlaywrightTimeout:
                logger.error("Login form not found. Page may still be loading or blocked.")
                save_screenshot(page, config, label="form_not_found")
                raise

            # Mouse movements
            page.mouse.move(200, 300)
            page.wait_for_timeout(400)
            page.mouse.move(640, 400)
            page.wait_for_timeout(400)

            # Fill credentials
            logger.info("Entering credentials")

            email_sel = "input[type='email'], input[name='email'], input[id*='email']"
            page.click(email_sel)
            page.wait_for_timeout(300)
            page.fill(email_sel, username)
            page.wait_for_timeout(700)

            pass_sel = "input[type='password'], input[name='password'], input[id*='password']"
            page.click(pass_sel)
            page.wait_for_timeout(300)
            page.fill(pass_sel, password)
            page.wait_for_timeout(700)

            logger.info("Credentials entered.")

            # Captcha handling - not bypass
            logger.warning(
                "\n" + "="*55 +
                "\nCAPTCHA STEP — ACTION REQUIRED\n" +
                "="*55 +
                "\n 1. Look at the browser window\n"
                " 2. Solve the CAPTCHA\n"
                " 3. Click the LOGIN button\n"
                " 4. Come back here and press ENTER\n" +
                "="*55
            )
            input("\n Press ENTER after you have logged in\n")

            # Wait for post login page
            page.wait_for_timeout(4000)

            #detect result
            current_url = page.url.lower()
            page_title  = page.title().lower()

            success_signals = ["dashboard", "profile", "application", "home", "welcome", "appointment"]
            failure_signals = ["login", "signin", "sign-in", "error", "invalid", "unauthorized"]

            if any(s in current_url or s in page_title for s in success_signals):
                logger.info("LOGIN SUCCESSFUL!")
                logger.info(f"   URL  : {page.url}")
                logger.info(f"   Title: {page.title()}")
                save_screenshot(page, config, label="login_success")

            elif any(s in current_url for s in failure_signals):
                logger.error("LOGIN FAILED — still on login/error page.")
                logger.error(f"   URL: {page.url}")
                save_screenshot(page, config, label="login_failed")

            else:
                logger.warning("Result unclear — check screenshot.")
                logger.warning(f"   URL: {page.url} | Title: {page.title()}")
                save_screenshot(page, config, label="login_unknown")

        except PlaywrightTimeout as e:
            logger.error(f"Timeout: {e}")
            save_screenshot(page, config, label="timeout_error")

        except Exception as e:
            logger.error(f"Error: {e}")
            save_screenshot(page, config, label="unexpected_error")
            raise

        finally:
            logger.info(f"Log saved: {log_filename}")
            if not headless:
                input("\nPress ENTER to close browser\n")
            browser.close()
            logger.info("Browser closed.")




def main():
    parser = argparse.ArgumentParser(description="VFS Global Login Automation")
    parser.add_argument("--headless", action="store_true", default=False,
                        help="Run in headless (background) mode.")
    parser.add_argument("--config", default="config.json",
                        help="Path to config file.")
    args = parser.parse_args()
    run_login(headless=args.headless, config_path=args.config)


if __name__ == "__main__":
    main()
