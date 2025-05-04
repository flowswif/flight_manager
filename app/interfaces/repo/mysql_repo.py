import pymysql
from pymysql.cursors import DictCursor
from app.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST

def create_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        cursorclass=DictCursor
    )
