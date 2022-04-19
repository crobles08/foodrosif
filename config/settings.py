from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_HOSTNAME = os.environ.get('MYSQL_HOSTNAME')
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_PORT = os.environ.get('MYSQL_PORT')