# Login Automation Script using Playwright

This project demonstrates a login automation script built using **Playwright (Python)** for the VFS Global website:
https://visa.vfsglobal.com/are/en/mlt/login
This website is a **high-security, government-related platform protected by Cloudflare**, which actively detects and blocks automation tools. Because of this, the project focuses on building a **robust, ethical, and production-aware automation approach**, rather than attempting to bypass security mechanisms.

---

## What This Script Does

* Opens the website and establishes a valid session
* Navigates to the login page
* Enters credentials securely (no hardcoding)
* Detects CAPTCHA and pauses for manual solving
* Determines whether login is successful, failed, or unclear
* Captures screenshots for all outcomes
* Logs all actions and errors
* Supports both **headed (visible)** and **headless (background)** modes

---

##Handling Bot Detection (Cloudflare)

One of the biggest challenges in this task is that the VFS Global website uses **Cloudflare bot protection**, which can:

* Detect automation frameworks like Playwright
* Block access with “Access Denied” or “Verify you are human” pages
* Freeze or restrict interaction

To handle this, I implemented several **practical mitigation techniques**:

* Used **Playwright Stealth** to mask automation fingerprints
* Configured **realistic browser context** (user-agent, headers, viewport)
* Added **human-like behavior** (mouse movements, delays)
* Opened the **homepage first** to establish session
* Suggested use of **VPN (EU region)** to avoid IP-based blocking

> Even with these measures, the site may still get blocked. This is expected due to the strength of the security system.

---

##CAPTCHA Handling (Important Design Choice)

The website uses **Cloudflare Turnstile CAPTCHA**, which is specifically designed to prevent automation.

Instead of trying to bypass it (which is unethical and often illegal), the script handles it in a **professional way**:

* The script pauses execution when CAPTCHA is detected
* The user manually solves the CAPTCHA
* The user clicks login manually
* The script resumes execution afterward

> This approach ensures the automation remains reliable and compliant with security standards.

---

##Login Result Detection

After attempting login, the script evaluates the result using:

* Current URL
* Page title and content

It categorizes outcomes into:

* **Login Successful**
* **Login Failed**
* **Result Unclear**

This makes the script flexible even when the website behavior changes.

---

## Screenshot Capture

A screenshot is captured **in every scenario**, including:

* Successful login
* Failed login
* Blocked access
* Errors or unexpected states

This ensures:

* Easy debugging
* Clear proof of execution
* Transparency in results
<img width="1280" height="800" alt="blocked_20260415_140810" src="https://github.com/user-attachments/assets/091c1f1e-c27d-4892-a0fd-25cd9b9aa877" />

---

## 🛡️ Error Handling & Stability

The script is designed to be **robust and fault-tolerant**:

* Handles timeouts using Playwright’s timeout system
* Uses try-except blocks for unexpected errors
* Logs all issues clearly
* Ensures the pipeline does not crash abruptly

Even if something fails, the script:

* Logs the error
* Takes a screenshot
* Exits gracefully

---

## Secure Credential Management

Credentials are **not hardcoded** in the script.

Instead, they are stored in a `.env` file:

```bash
VFS_USERNAME=your_username
VFS_PASSWORD=your_password
```

These are loaded securely using `python-dotenv`.

> The `.env` file is intentionally not included in this repository to prevent exposing sensitive data.

---

## Why the Website Gets Blocked

It’s important to understand that:

* VFS Global is a **high-security platform**
* It is protected by **Cloudflare (enterprise-grade protection)**
* It actively detects bots and automation tools

So when the script gets blocked, it is **not a failure of the script**, but a **designed behavior of the website**.

---

## Professional Approach (Real-World Perspective)

In real production systems, we would **not automate login through UI** for such platforms.

Instead, better approaches include:

* Using **official APIs (if available)**
* Requesting **whitelisted or internal access**
* Working with **staging/test environments**
* Backend-level integrations

This project demonstrates awareness of these best practices.

---

## Reusability of the Script

The script is written in a **modular and reusable way**, meaning:

* It can be adapted to any login-based website
* Only selectors and URLs need to be changed
* Core logic remains the same

---

## Demo Automation (Proof of Working Logic)

To demonstrate that the automation logic works correctly:

* The same script was tested on a **demo website with lower security**
* Login was successfully automated
* Screenshots of successful execution are included

📁 You can check the results in:

```
/screenshots/
```

This shows that:

* The automation logic is correct
* The only limitation is external website security
<img width="1263" height="869" alt="login_success_20260415_143908" src="https://github.com/user-attachments/assets/5a10c0e8-08fc-4811-ba28-8846993723cb" />

---

## 🧠 Final Thoughts

This project focuses on building a **realistic automation solution**, not just a working script.

It demonstrates:

* Understanding of modern web security systems
* Ethical handling of CAPTCHA and bot detection
* Strong automation design and structure

> The goal is not to break security, but to build systems that work **within real-world constraints**.

---
