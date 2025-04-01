#!/usr/bin/env python3
import subprocess
import os
import sys
import logging
import smtplib
import requests
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ====== Logging Configuration ======
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ====== Configuration Section ======
DOMAIN = "*****"  # <-- Replace with domain you want to track

# Files to store the last recorded values (in the same directory as the script)
WHOIS_FILE = "whois_record.txt"
STATUS_FILE = "curl_status.txt"

# SMTP configuration (update with your SMTP server details)
SMTP_SERVER   = "****"		# <-- Your SMTP server
SMTP_PORT     = 465  # Using port 465 for implicit SSL
SMTP_USERNAME = "****"  # <-- Your SMTP username/email
SMTP_PASSWORD = "****"            # <-- Your SMTP password or app-specific password
EMAIL_FROM    = "****"   # <-- Your email address (sender)
EMAIL_TO      = "****"         # <-- Recipient's email address
# ====== End of Configuration ======

def normalize_http_status(status_str):
    """
    Normalize an HTTP status string by removing variable memory addresses.
    For example, it converts:

      "Error: HTTPConnectionPool(... at 0x7acd50b51ac0>: ...)"

    to a version without the 'at 0x...' parts.
    """
    return re.sub(r' at 0x[0-9a-fA-F]+', '', status_str).strip()

def get_whois_updated_date(domain):
    """
    Runs the 'whois' command for the given domain and returns the value of the
    "Updated Date:" field as a string.
    """
    logging.debug("Retrieving whois record for domain: %s", domain)
    try:
        result = subprocess.run(
            ["whois", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            logging.error("Error running whois: %s", result.stderr.strip())
            return None

        # Search for the line containing "Updated Date:" (case-insensitive)
        for line in result.stdout.splitlines():
            if "Updated Date:" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    updated_date = parts[1].strip()
                    logging.debug("Found updated date: %s", updated_date)
                    return updated_date
        logging.warning("Updated Date not found in whois output.")
        return None
    except Exception as e:
        logging.exception("Exception occurred while running whois")
        return None

def get_http_status(domain):
    """
    Performs an HTTP GET request to the domain and returns a string representing
    the HTTP status code. If the request fails, returns a normalized error message.
    """
    url = f"http://{domain}"
    logging.debug("Performing HTTP GET for URL: %s", url)
    try:
        response = requests.get(url, timeout=10)
        logging.debug("HTTP GET succeeded with status code: %s", response.status_code)
        return str(response.status_code)
    except Exception as e:
        error_message = f"Error: {str(e)}"
        normalized = normalize_http_status(error_message)
        logging.error("HTTP request failed for %s: %s", url, normalized)
        return normalized

def send_email(subject, body):
    """
    Sends an email via SMTP_SSL with the given subject and body.
    """
    logging.debug("Preparing email with subject: %s", subject)
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        logging.debug("Connecting to SMTP server: %s:%s", SMTP_SERVER, SMTP_PORT)
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Enable SMTP debug output
        logging.debug("Logging in as %s", SMTP_USERNAME)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        logging.debug("Sending email to %s", EMAIL_TO)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        logging.info("Notification email sent successfully.")
    except Exception as e:
        logging.exception("Error sending email")

def main():
    logging.info("Starting check for domain: %s", DOMAIN)

    # Retrieve the current WHOIS updated date.
    current_updated = get_whois_updated_date(DOMAIN)
    if current_updated is None:
        logging.error("Could not retrieve whois updated date for %s", DOMAIN)
        send_email(f"Error: Whois Check for {DOMAIN}",
                   f"Could not retrieve the Updated Date from whois for {DOMAIN}.")
        sys.exit(1)

    # Retrieve the current HTTP status (or normalized error message).
    current_http_status = get_http_status(DOMAIN)
    normalized_current_http = normalize_http_status(current_http_status)

    # Read the previous WHOIS updated date.
    if not os.path.exists(WHOIS_FILE):
        logging.info("Whois file not found. Creating new file with current value.")
        with open(WHOIS_FILE, "w") as f:
            f.write(current_updated)
        previous_updated = current_updated
    else:
        with open(WHOIS_FILE, "r") as f:
            previous_updated = f.read().strip()

    # Read the previous HTTP status.
    if not os.path.exists(STATUS_FILE):
        logging.info("Status file not found. Creating new file with current value.")
        with open(STATUS_FILE, "w") as f:
            f.write(normalized_current_http)
        previous_http_status = normalized_current_http
    else:
        with open(STATUS_FILE, "r") as f:
            previous_http_status = f.read().strip()

    normalized_previous_http = normalize_http_status(previous_http_status)

    # Determine if there is any change.
    whois_changed = (current_updated != previous_updated)
    http_changed = (normalized_current_http != normalized_previous_http)

    # Compose the email subject.
    subject = f"{DOMAIN} changed" if (whois_changed or http_changed) else f"{DOMAIN} same"

    # Compose the email body.
    body_lines = []
    if whois_changed:
        body_lines.append(
            f"Whois Updated Date changed:\n  Previous: {previous_updated}\n  Current:  {current_updated}"
        )
    else:
        body_lines.append(f"Whois Updated Date unchanged: {current_updated}")

    if http_changed:
        body_lines.append(
            f"HTTP status changed:\n  Previous: {normalized_previous_http}\n  Current:  {normalized_current_http}"
        )
    else:
        body_lines.append(f"HTTP status unchanged: {normalized_current_http}")

    body = "\n\n".join(body_lines)

    # Send a single email with the combined results.
    send_email(subject, body)

    # Update the stored values.
    with open(WHOIS_FILE, "w") as f:
        f.write(current_updated)
    with open(STATUS_FILE, "w") as f:
        f.write(normalized_current_http)

    logging.info("Check complete. Email subject: '%s'", subject)

if __name__ == "__main__":
    main()