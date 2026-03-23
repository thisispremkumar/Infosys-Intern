"""
Email automation for sending business reports.
Uses SMTP with TLS for secure email delivery.
Supports Gmail, Outlook, and custom SMTP servers.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime


# Pre-configured SMTP providers
SMTP_PROVIDERS = {
    "Gmail": {"host": "smtp.gmail.com", "port": 587},
    "Outlook": {"host": "smtp.office365.com", "port": 587},
    "Yahoo": {"host": "smtp.mail.yahoo.com", "port": 587},
    "Custom": {"host": "", "port": 587},
}


def send_report_email(
    smtp_host: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str | None = None,
    body: str | None = None,
    pdf_bytes: bytes | None = None,
    pdf_filename: str | None = None,
) -> tuple[bool, str]:
    """
    Send an email with an optional PDF attachment.

    Returns (success: bool, message: str).
    """
    if not subject:
        subject = f"Business Report - {datetime.now().strftime('%B %d, %Y')}"
    if not body:
        body = (
            "Hello,\n\n"
            "Please find attached the latest business analysis report from the "
            "Small Business Sales & Profit Analyzer.\n\n"
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.\n\n"
            "Best regards,\n"
            "Small Business Analyzer"
        )
    if not pdf_filename:
        pdf_filename = f"business_report_{datetime.now().strftime('%Y%m%d')}.pdf"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if pdf_bytes:
        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
        msg.attach(attachment)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True, f"Report sent successfully to {recipient_email}"
    except smtplib.SMTPAuthenticationError:
        return False, (
            "Authentication failed. For Gmail, use an App Password "
            "(https://myaccount.google.com/apppasswords). "
            "For Outlook, ensure SMTP is enabled in account settings."
        )
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
