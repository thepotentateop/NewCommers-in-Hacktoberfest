import os
from dotenv import load_dotenv

def load_credentials():
    """
    Load email credentials from environment variables.

    Returns:
        tuple: (display_name, sender_email, password)
    """
    load_dotenv()

    display_name = os.getenv('DISPLAY_NAME')
    sender_email = os.getenv('SENDER_EMAIL')
    password = os.getenv('PASSWORD')

    if not all([display_name, sender_email, password]):
        raise ValueError(
            "Missing credentials. Please refer to https://github.com/aahnik/automailer#usage"
        )

    return display_name, sender_email, password


if __name__ == "__main__":
    try:
        display_name, sender_email, password = load_credentials()
        print("Credentials loaded successfully")
    except ValueError as e:
        print(e)
