# VFS Global Auto Login

A Python automation script that automatically logs into the [VFS Global visa appointment portal](https://visa.vfsglobal.com/are/en/mlt/login). It uses **DrissionPage**, a Chromium-based browser automation library that controls a real Chrome browser — making it more reliable against bot-detection systems like Cloudflare compared to tools like Selenium or Playwright.

---

## How It Works — Code Overview

The script is built around four key ideas:

### 1. Real Browser Automation (DrissionPage)
Instead of sending raw HTTP requests, the script opens an actual Chrome browser window and interacts with the page just like a human would — clicking, typing, and scrolling. This is important because VFS Global uses Cloudflare, which blocks headless or fake browsers.

### 2. Cloudflare Wait
When the page first loads, Cloudflare runs a silent browser check. The script waits 15 seconds to give this check time to pass before trying to interact with anything on the page.

### 3. Robust Element Finding (`wait_for_element`)
The VFS Global login page is built with Angular, which means page elements load dynamically after the initial HTML is received. A simple `find element` call would fail immediately. Instead, the script uses a `wait_for_element` function that:
- Tries multiple CSS and XPath selectors for each field (email, password, button)
- Retries up to 8 times with 3-second gaps between attempts
- Returns the first element it successfully finds and confirms is visible

### 4. Safe Click and Input (`safe_click`, `safe_input`)
Angular's reactive forms need more than just setting a value — they listen for DOM events. The `safe_input` function:
- First tries the native DrissionPage `.input()` method
- If that fails, falls back to JavaScript to set the value and manually fires `input` and `change` events so Angular registers the change correctly

The `safe_click` function similarly falls back to a JavaScript click if the element has no visible bounding rectangle.

---

## Requirements

- Python 3.10 or higher
- Google Chrome installed on your machine
- DrissionPage library

Install DrissionPage with:

```bash
pip install DrissionPage
```

---

## Project Structure

```
your-folder/
├── login.py            # The main automation script
├── credentials.json    # Your login details (you create this)
├── login_result.png    # Screenshot saved after login (auto-generated)
└── README.md
```

---

## Setup

**Step 1:** Clone or download this project into a folder on your computer.

**Step 2:** Create a file named `credentials.json` in the same folder as `login.py` with the following content:

```json
{
  "Email": "your@email.com",
  "password": "yourpassword"
}
```

Replace the values with your actual VFS Global account email and password.

**Step 3:** Install the required Python package:

```bash
pip install DrissionPage
```

---

## Running the Script

Open a terminal (Command Prompt or PowerShell on Windows, Terminal on Mac/Linux), navigate to the folder containing `login.py`, and run:

```bash
python login.py
```

**What you will see:**

```
Waiting for page to load and Cloudflare challenge to pass...
Page title: Login | VFS Global
Current URL: https://visa.vfsglobal.com/are/en/mlt/login
HTML length: 234313
Found email field via: xpath://input[contains(@placeholder,"jane")]
Entered email: your@email.com
Found password field via: xpath://input[@type="password"]
Entered password
Found login button via: xpath://button[contains(normalize-space(),"Sign In")]
Login submitted. Waiting for redirect...
Done! Screenshot saved as 'login_result.png'.
Press Enter to close browser...
```

A Chrome window will open visibly so you can see exactly what the script is doing. After login completes, the browser stays open until you press Enter in the terminal.

---

## Output Files

| File | When it is created | Description |
|---|---|---|
| `login_result.png` | After successful login | Screenshot of the post-login page |
| `error_no_email.png` | If email field is not found | Screenshot for debugging |
| `error_no_password.png` | If password field is not found | Screenshot for debugging |
| `error_no_button.png` | If Sign In button is not found | Screenshot for debugging |
| `page_source.html` | If email field is not found | Full HTML of the page for inspection |

---

## Troubleshooting

**Login submitted but redirect fails**
The page may be showing an error (wrong password, account locked, etc.). Check `login_result.png` to see the state of the page after submission.

---

## Security Note

The `credentials.json` file contains your login password in plain text. Do not share it or commit it to any version control system (GitHub, etc.). If using Git, add it to `.gitignore`:

```
credentials.json
```

---


