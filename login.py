import json
from time import sleep
from DrissionPage import ChromiumPage
from DrissionPage.errors import NoRectError

with open("credentials.json") as f:
    creds = json.load(f)
    USERNAME = creds["Email"]
    PASSWORD = creds["password"]

def safe_click(element):
    try:
        element.click()
    except NoRectError:
        print("Element has no rectangle, trying JavaScript click...")
        element.click(by_js=True)

def safe_input(element, text):
    try:
        element.input(text)
    except Exception as e:
        print(f"Input failed: {e}, trying JavaScript set value...")
        element.run_js(f'this.value="{text}"')
        element.run_js('this.dispatchEvent(new Event("input", { bubbles: true }))')
        element.run_js('this.dispatchEvent(new Event("change", { bubbles: true }))')

def wait_for_element(page, selectors, timeout_each=5, retries=6, label="element"):
    for attempt in range(retries):
        for sel in selectors:
            try:
                temp = page.ele(sel, timeout=timeout_each)
                if temp:
                    try:
                        if temp.wait.displayed(timeout=timeout_each):
                            print(f"Found {label} via: {sel}")
                            return temp
                    except Exception:
                        return temp
            except Exception:
                pass
        print(f"Attempt {attempt + 1}/{retries}: {label} not found yet, waiting 3s...")
        sleep(3)
    return None

def login_vfs():
    page = ChromiumPage()

    page.get('https://visa.vfsglobal.com/are/en/mlt/login')
    print("Waiting for page to load and Cloudflare challenge to pass...")
    sleep(15)

    print(f"Page title: {page.title}")
    print(f"Current URL: {page.url}")
    print(f"HTML length: {len(page.html)}")

    email_selectors = [
        'input[type="email"]',
        'input[formcontrolname="email"]',
        'input[placeholder*="jane.doe"]',
        'input[placeholder*="jane"]',
        'input[placeholder*="email"]',
        'input[name="email"]',
        'xpath://input[@type="email"]',
        'xpath://input[contains(@placeholder,"jane")]',
        'xpath://input[contains(@placeholder,"email") or contains(@placeholder,"Email")]',
        'xpath://mat-form-field//input',
    ]

    email_input = wait_for_element(page, email_selectors, timeout_each=5, retries=8, label="email field")

    if not email_input:
        print("Email field not found after all attempts. Saving debug info...")
        page.get_screenshot(path='error_no_email.png')
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page.html)
        print("Saved error_no_email.png and page_source.html for inspection.")
        return

    email_input.scroll.to_see()
    sleep(1)
    safe_click(email_input)
    sleep(0.5)
    safe_input(email_input, USERNAME)
    print(f"Entered email: {USERNAME}")
    sleep(1.5)

    password_selectors = [
        'input[type="password"]',
        'input[formcontrolname="Password"]',
        'input[formcontrolname="password"]',
        'input[name="password"]',
        'xpath://input[@type="password"]',
    ]

    password_input = wait_for_element(page, password_selectors, timeout_each=5, retries=4, label="password field")

    if not password_input:
        print("Password field not found.")
        page.get_screenshot(path='error_no_password.png')
        return

    password_input.scroll.to_see()
    sleep(1)
    safe_click(password_input)
    sleep(0.5)
    safe_input(password_input, PASSWORD)
    print("Entered password")
    sleep(1.5)

    login_btn_selectors = [
        'button[type="submit"]',
        'xpath://button[@type="submit"]',
        'xpath://button[contains(text(),"Sign In")]',
        'xpath://button[contains(text(),"Login")]',
        'xpath://button[contains(text(),"sign in")]',
        'xpath://button[contains(normalize-space(),"Sign In")]',
        'xpath://mat-raised-button',
        'xpath://button[contains(@class,"mat-raised-button")]',
    ]

    login_btn = wait_for_element(page, login_btn_selectors, timeout_each=5, retries=4, label="login button")

    if not login_btn:
        print("Login button not found.")
        page.get_screenshot(path='error_no_button.png')
        return

    login_btn.scroll.to_see()
    sleep(1)
    safe_click(login_btn)
    print("Login submitted. Waiting for redirect...")

    try:
        page.wait.doc_loaded(timeout=20)
    except Exception:
        pass
    sleep(5)

    try:
        page.get_screenshot(path='login_result.png')
        print("Done! Screenshot saved as 'login_result.png'.")
    except Exception as e:
        print(f"Screenshot failed (page may still be loading): {e}")
        print(f"Current URL after login: {page.url}")

    input("Press Enter to close browser...")
    page.quit()

if __name__ == "__main__":
    login_vfs()
