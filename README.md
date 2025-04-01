
# DomainSentinel

Domain Sentinel is a lightweight Python tool designed to monitor the status of a domain. It checks for changes in the WHOIS updated date and the HTTP status code, then sends an email notification if any changes are detected. This tool is ideal for users who want to keep track of their domain's status and receive timely alerts via email.

## Features

- **WHOIS Monitoring:** Retrieves and monitors the "Updated Date" field from the WHOIS record.
- **HTTP Status Check:** Performs an HTTP GET request to check the current status of the domain.
- **Email Notifications:** Sends a detailed email alert when a change is detected in either the WHOIS record or HTTP status.
- **Cronjob Integration:** Easily schedule the script to run at regular intervals using cron.

## Requirements

- Python 3.x
- [Requests](https://docs.python-requests.org/) library for HTTP requests
- Standard Python libraries: `subprocess`, `os`, `sys`, `logging`, `smtplib`, `re`, `email`

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/domain-sentinel.git
   cd domain-sentinel

2.  **Install Dependencies:** 
Although the script primarily uses standard libraries, make sure you have the requests library installed:
```bash
	pip install requests
```
## Configuration:
Open the monitor_domain.py file and update the following configuration parameters with your own settings:

DOMAIN: Set to the domain you wish to monitor.

SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD: Your SMTP server details and credentials.

EMAIL_FROM, EMAIL_TO: Sender and recipient email addresses.

Note: The current values are placeholders (e.g., "****"). Replace these with your actual data. For production environments, consider using environment variables or a secure secrets management approach.

## Usage
Run the script manually by executing:

```bash
./monitor_domain.py
```
or

```bash
python3 monitor_domain.py
```

## Scheduling with Cron

To automate domain monitoring, set up a cronjob. For example, to run the script every hour:

Open the cron editor:

```bash
crontab -e
```
Add the following line (adjust the paths as necessary):

```bash
0 * * * * /usr/bin/python3 /path/to/monitor_domain.py
```
**Logging**
The script uses Python's built-in logging module. Logs are printed to the console and include debug information that can help troubleshoot issues.
