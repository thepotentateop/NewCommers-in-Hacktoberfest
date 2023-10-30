import os
from dotenv import load_dotenv

load_dotenv()

DISPLAY_NAME = os.getenv('display_name')          " Get actual Name from env 
SENDER_EMAIL = os.getenv('sender_email')          " Get actual Email from env
PASSWORD = os.getenv('password')                  " Get actual Password from env

try:
    assert DISPLAY_NAME
    assert SENDER_EMAIL
    assert PASSWORD
except AssertionError:
    print('Please set up credentials. Read https://github.com/aahnik/automailer#usage')
else:
    print('Credentials loaded successfully')
