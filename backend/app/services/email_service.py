"""
Email Service: Handles sending/receiving via IMAP/SMTP, Gmail API, or Outlook API.
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


async def send_email_smtp(
    host: str,
    port: int,
    username: str,
    password: str,
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    use_tls: bool = True,
) -> bool:
    """Send email via SMTP"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Use asyncio-compatible approach (sync in background)
        import asyncio
        loop = asyncio.get_event_loop()

        def _send():
            if use_tls:
                server = smtplib.SMTP(host, port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(host, port)

            server.login(username, password)
            server.send_message(msg)
            server.quit()
            return True

        result = await loop.run_in_executor(None, _send)
        return result
    except Exception as e:
        print(f"SMTP send error: {e}")
        return False


async def check_inbox_imap(
    host: str,
    port: int,
    username: str,
    password: str,
    use_ssl: bool = True,
) -> list[dict]:
    """Check inbox via IMAP for new messages"""
    try:
        import asyncio

        def _check():
            if use_ssl:
                mail = imaplib.IMAP4_SSL(host, port)
            else:
                mail = imaplib.IMAP4(host, port)

            mail.login(username, password)
            mail.select("INBOX")

            status, messages = mail.search(None, "UNSEEN")
            email_ids = messages[0].split() if messages[0] else []

            results = []
            for eid in email_ids[-10:]:  # Last 10 unseen
                status, msg_data = mail.fetch(eid, "(RFC822)")
                if status == "OK":
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    results.append({
                        "from": msg["From"],
                        "subject": msg["Subject"],
                        "message_id": msg["Message-ID"],
                    })

            mail.logout()
            return results

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _check)
    except Exception as e:
        print(f"IMAP check error: {e}")
        return []


async def verify_smtp_connection(
    host: str,
    port: int,
    username: str,
    password: str,
    use_tls: bool = True,
) -> dict:
    """Test SMTP connection and return status"""
    try:
        import asyncio

        def _test():
            if use_tls:
                server = smtplib.SMTP(host, port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            server.login(username, password)
            server.quit()
            return True

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _test)
        return {"ok": True, "message": "Conexión SMTP exitosa"}
    except smtplib.SMTPAuthenticationError:
        return {"ok": False, "message": "Error de autenticación SMTP"}
    except smtplib.SMTPException as e:
        return {"ok": False, "message": f"Error SMTP: {str(e)}"}
    except Exception as e:
        return {"ok": False, "message": f"Error de conexión: {str(e)}"}
