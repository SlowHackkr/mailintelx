# mailintelx.py
# Email Recon Tool (Offline + Free API Only)
# Author: OpenAI-assisted | Designed for Penetration Testers

import re
import os
import json
import socket
import datetime
import smtplib
import requests
import dns.resolver
import whois
import webbrowser
from urllib.parse import quote
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Directory to store results
os.makedirs("results", exist_ok=True)

# === UTILITY FUNCTIONS ===
def get_name_guess(email):
    return email.split('@')[0].replace('.', ' ').title()

def extract_domain(email):
    return email.split('@')[1]

def get_mx_records(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return sorted([str(r.exchange).rstrip('.') for r in records])
    except:
        return []

def resolve_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except:
        return None

def get_geolocation(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        return response.json()
    except:
        return {}

def get_whois_info(domain):
    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "whois_server": w.whois_server,
            "updated_date": str(w.updated_date),
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "status": w.status,
            "emails": w.emails,
            "org": w.org,
            "country": w.country
        }
    except:
        return {"domain": domain, "error": "WHOIS lookup failed"}

def get_social_profiles(email):
    username = email.split('@')[0]
    return {
        "github": f"https://github.com/{username}",
        "twitter": f"https://twitter.com/{username}",
        "gravatar": f"https://www.gravatar.com/avatar/{gravatar_hash(email)}"
    }

def gravatar_hash(email):
    import hashlib
    email_clean = email.strip().lower().encode('utf-8')
    return hashlib.md5(email_clean).hexdigest()

# === MAIN SCAN FUNCTION ===
def scan_email(email):
    print(f"{Fore.CYAN}[+] Scanning email: {email}{Style.RESET_ALL}")

    name_guess = get_name_guess(email)
    domain = extract_domain(email)

    print(f"{Fore.YELLOW}[*] Extracted domain: {domain}{Style.RESET_ALL}")
    mx_records = get_mx_records(domain)
    print(f"{Fore.YELLOW}[*] MX records: {mx_records}{Style.RESET_ALL}")

    resolved_ip = resolve_ip(domain)
    if not resolved_ip:
        root_domain = '.'.join(domain.split('.')[-2:])
        resolved_ip = resolve_ip(root_domain)
    print(f"{Fore.YELLOW}[*] Resolved IP: {resolved_ip or 'Not found'}{Style.RESET_ALL}")

    geolocation = get_geolocation(resolved_ip) if resolved_ip else {}
    whois_info = get_whois_info(domain)
    social_profiles = get_social_profiles(email)

    result = {
        "email": email,
        "name_guess": name_guess,
        "domain": domain,
        "mx_records": mx_records,
        "resolved_ip": resolved_ip,
        "geolocation": geolocation,
        "whois": whois_info,
        "social_profiles": social_profiles,
        "scan_date": str(datetime.datetime.now())
    }

    return result

# === REPORTING ===
def save_json_report(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def save_html_report(data, filename):
    html = f"""
    <html><head><title>Email Recon Report</title></head><body>
    <h2>Email Recon Report</h2>
    <p><b>Email:</b> {data['email']}</p>
    <p><b>Name Guess:</b> {data['name_guess']}</p>
    <p><b>Domain:</b> {data['domain']}</p>
    <h3>MX Records</h3>
    <ul>{''.join(f'<li>{mx}</li>' for mx in data['mx_records'])}</ul>
    <h3>IP and Geolocation</h3>
    <p><b>Resolved IP:</b> {data['resolved_ip'] or 'Not found'}</p>
    <pre>{json.dumps(data['geolocation'], indent=2)}</pre>
    <h3>WHOIS Info</h3>
    <pre>{json.dumps(data['whois'], indent=2)}</pre>
    <h3>Social Profiles (Guessed)</h3>
    <ul>
      <li><a href="{data['social_profiles']['github']}" target="_blank">GitHub</a></li>
      <li><a href="{data['social_profiles']['twitter']}" target="_blank">Twitter</a></li>
      <li><a href="{data['social_profiles']['gravatar']}" target="_blank">Gravatar</a></li>
    </ul>
    <p><b>Scan Date:</b> {data['scan_date']}</p>
    </body></html>
    """
    with open(filename, 'w') as f:
        f.write(html)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"{Fore.RED}Usage: python3 mailintelx.py <email>{Style.RESET_ALL}")
        sys.exit(1)

    email = sys.argv[1]
    result = scan_email(email)

    date_tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = email.replace('@','_') + f"_{date_tag}"
    json_path = f"results/{base_filename}.json"
    html_path = f"results/{base_filename}.html"

    save_json_report(result, json_path)
    save_html_report(result, html_path)

    print(f"{Fore.GREEN}\n[+] Scan complete!")
    print(f"- JSON Report: {json_path}")
    print(f"- HTML Report: {html_path}{Style.RESET_ALL}")

    try:
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
    except:
        print(f"{Fore.RED}[!] Could not open browser to display HTML report.{Style.RESET_ALL}")
