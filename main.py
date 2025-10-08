import os
import smtplib
import logging
from tqdm import tqdm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from concurrent.futures import ThreadPoolExecutor, as_completed

from email_utils import (
    load_template,
    read_csv_data,
    is_valid_email,
    get_attachments,
    markdown_to_html
)
from settings import SENDER_EMAIL, PASSWORD, DISPLAY_NAME

# Configure Logging
logging.basicConfig(
    filename='mailer.log',
    filemode='a',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)


def build_message(receiver, subject, body_text, attachments):
    """Construct MIME message with attachments."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{DISPLAY_NAME} <{SENDER_EMAIL}>"
    msg['To'] = receiver

    msg.attach(MIMEText(body_text, 'plain'))
    msg.attach(MIMEText(markdown_to_html(body_text), 'html'))

    # Attach files
    for name, content in zip(attachments['names'], attachments['contents']):
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={name}')
        msg.attach(part)

    return msg


def send_email(receiver, message, server):
    """Send single email with retry and error handling."""
    try:
        server.sendmail(SENDER_EMAIL, receiver, message.as_string())
        logging.info(f"Email sent to {receiver}")
        return True
    except Exception as e:
        logging.error(f"Failed to send to {receiver}: {e}")
        return False


def main():
    print("🚀 Starting Bulk Mailer...")

    # Load template and CSV data
    template = load_template("compose.md")
    data = read_csv_data("data.csv")
    attachments = get_attachments()

    # Prepare SMTP
    host, port = "smtp.gmail.com", 587
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(SENDER_EMAIL, PASSWORD)

    success_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for row in data:
            receiver = row.get('EMAIL')
            if not receiver or not is_valid_email(receiver):
                logging.warning(f"Invalid email skipped: {receiver}")
                continue

            # Personalize message
            message = template
            for key, val in row.items():
                message = message.replace(f"${key}", val)

            subject = message.splitlines()[0]
            msg = build_message(receiver, subject, message, attachments)

            futures.append(executor.submit(send_email, receiver, msg, server))

        # Track progress
        for f in tqdm(as_completed(futures), total=len(futures), desc="Sending emails"):
            if f.result():
                success_count += 1

    print(f"✅ Sent {success_count}/{len(data)} emails successfully.")
    logging.info(f"Completed sending {success_count}/{len(data)} emails.")

    server.quit()


if __name__ == "__main__":
    main()
