import csv
import os
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from settings import SENDER_EMAIL, PASSWORD, DISPLAY_NAME


def get_message_template(csv_file_path, template):
    """
    Generate personalized email messages from a CSV file and a template.

    Args:
        csv_file_path (str): Path to the CSV file containing recipient data.
        template (str): Email template with placeholders for recipient data.

    Yields:
        tuple: (recipient_email, personalized_message)
    """
    with open(csv_file_path, 'r') as file:
        headers = file.readline().strip().split(',')
        headers[-1] = headers[-1].rstrip()

    with open(csv_file_path, 'r') as file:
        data = csv.DictReader(file)
        for row in data:
            message = template
            for header in headers:
                value = row[header]
                message = message.replace(f'${header}', value)
            yield row['EMAIL'], message


def confirm_attachments():
    """
    Confirm attachments to be sent with the email.

    Returns:
        dict: {'names': [attachment_names], 'contents': [attachment_contents]}
    """
    attachments = {'names': [], 'contents': []}
    try:
        for filename in os.listdir('ATTACH'):
            confirmed = input(f"Confirm attachment '{filename}'? (Y/n): ")
            if confirmed.lower() == 'y':
                attachments['names'].append(filename)
                with open(f'{os.getcwd()}/ATTACH/{filename}', 'rb') as f:
                    attachments['contents'].append(f.read())
    except FileNotFoundError:
        print("No ATTACH directory found.")
    return attachments


def send_emails(server, template):
    """
    Send personalized emails to recipients.

    Args:
        server (smtplib.SMTP): SMTP server object.
        template (str): Email template.
    """
    attachments = confirm_attachments()
    sent_count = 0

    for receiver, message in get_message_template('data.csv', template):
        multipart_msg = MIMEMultipart('alternative')
        multipart_msg['Subject'] = message.splitlines()[0]
        multipart_msg['From'] = f"{DISPLAY_NAME} <{SENDER_EMAIL}>"
        multipart_msg['To'] = receiver

        text = message
        html = markdown.markdown(text)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        multipart_msg.attach(part1)
        multipart_msg.attach(part2)

        if attachments['names']:
            for name, content in zip(attachments['names'], attachments['contents']):
                attach_part = MIMEBase('application', 'octet-stream')
                attach_part.set_payload(content)
                encoders.encode_base64(attach_part)
                attach_part.add_header('Content-Disposition', f"attachment; filename={name}")
                multipart_msg.attach(attach_part)

        try:
            server.sendmail(SENDER_EMAIL, receiver, multipart_msg.as_string())
        except Exception as err:
            print(f"Error sending email to {receiver}: {err}")
        else:
            sent_count += 1

    print(f"Sent {sent_count} emails")


if __name__ == "__main__":
    host = "smtp.gmail.com"
    port = 587

    with open('compose.md', 'r') as f:
        template = f.read()

    server = smtplib.SMTP(host, port)
    server.connect(host, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user=SENDER_EMAIL, password=PASSWORD)

    send_emails(server, template)

    server.quit()
