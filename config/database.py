import mysql.connector
from config import settings

db = mysql.connector.connect(
    host=settings.MYSQL_HOSTNAME,
    user=settings.MYSQL_USERNAME,
    password=settings.MYSQL_PASSWORD,
    port=settings.MYSQL_PORT,
    database=settings.MYSQL_DATABASE,
    buffered=True
)
db.autocommit = True