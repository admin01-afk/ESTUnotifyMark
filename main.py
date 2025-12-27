#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup

import urllib3 # suppress InsecureRequestWarning (using proxy with verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv
load_dotenv()

STEP_DEBUG = True
PROXY = False # BurpSuite
VERBOSE = False

BASE_OBS = "https://obs.eskisehir.edu.tr"
SSO_BASE = "https://giris.eskisehir.edu.tr"

USERNAME = os.getenv("TC_ID")
PASSWORD = os.getenv("PASSWORD")

# Session + headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

# route through Burp for debugging/interception
if PROXY:
    session.proxies.update({"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"})
    session.verify = False

def extract_meta_csrf(html):
    soup = BeautifulSoup(html, "html.parser")
    m = soup.find("meta", attrs={"name": "_csrf"})
    if m and m.get("content"):
        return m["content"]
    alt = soup.find("meta", attrs={"name": "csrf-token"}) or soup.find("meta", attrs={"name": "csrf"})
    return alt["content"] if alt and alt.get("content") else None

def extract_input_value(html, name):
    soup = BeautifulSoup(html, "html.parser")
    el = soup.find("input", attrs={"name": name})
    if el and el.get("value"):
        return el["value"]
    # fallback: check URL query for name
    # (useful when the response was a redirect URL)
    return None

def InputOrLog(prompt):
    if STEP_DEBUG:
        input(prompt)
    else:
        print(prompt)

try:
    # 1) GET OBS root (no redirects) to capture SSO redirect
    InputOrLog(f"GET {BASE_OBS} Press Enter to continue...")

    r0 = session.get(BASE_OBS, allow_redirects=False, timeout=20)
    print("OBS status:", r0.status_code, "✅" if r0.ok else "❌")
    r0.cookies.__len__() and VERBOSE and print("\nGot Cookies 🍪\n", session.cookies.get_dict())

    # login URL is always https://giris.eskisehir.edu.tr/login?redirect_uri=https://obs.eskisehir.edu.tr/
    # but first GET to BASE_OBS is required
    login_url = "https://giris.eskisehir.edu.tr/login?redirect_uri=https://obs.eskisehir.edu.tr"
    print("    login URL ->", login_url)

    # 2) GET SSO login page (contains hidden code)
    InputOrLog("GET login URL. Press Enter to GET it...")

    r_login = session.get(login_url, allow_redirects=True, timeout=20)
    r_login.raise_for_status()
    r_login.cookies.__len__() and VERBOSE and print("\nGot Cookies 🍪\n", session.cookies.get_dict())
    r_login.text and print("Got html(length:", len(r_login.text), ")", sep="")

    InputOrLog("parse tokens from login page html. Press Enter to continue...")

    # 3) extract hidden 'code' (and SSO CSRF if any)
    code = extract_input_value(r_login.text, "code") or extract_input_value(r_login.text, "sso")
    print("Extracted code:", code)

    print("\nLOGIN")
    InputOrLog("Ready to POST (/login/ad). Press Enter to continue...")

    # 4) POST credentials to /login/ad
    payload = {"username": USERNAME or "", "password": PASSWORD or ""}
    if code:
        payload["code"] = code
    headers = {
        "Origin": SSO_BASE,
        "Referer": r_login.url,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    print("POSTing to /login/ad with fields:", list(payload.items()))
    login_resp = session.post(f"{SSO_BASE}/login/ad", data=payload, headers=headers, allow_redirects=False, timeout=20)
    print("POST status:", login_resp.status_code , "✅" if login_resp.ok else "❌")

    InputOrLog("\nGET the OBS root (authenticated target) to extract OBS _csrf meta. Press Enter to GET it...")

    # 5) GET OBS root to obtain OBS CSRF
    obs_home = session.get(BASE_OBS, allow_redirects=True, timeout=20)
    print("\nOBS home URL:", obs_home.url)
    VERBOSE and print("\nCookies:", session.cookies.get_dict())
    obs_csrf = extract_meta_csrf(obs_home.text)
    print("OBS _csrf (meta):", obs_csrf, "\n")

    """
    # TODO: implement grade fetching (not simply in the response text)
    # 6) GET grades (use CSRF header if available)
    InputOrLog("\nAttempt to GET grades. Press Enter to continue...")
    grades_url = BASE_OBS + "/#/not-gor" # https://obs.eskisehir.edu.tr/#/not-gor
    ...
    """

except Exception as exc:
    print("Exception:", type(exc).__name__, exc)