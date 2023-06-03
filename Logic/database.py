from peewee import *
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.getenv("PGDATABASE")
DATBASE_USER = os.getenv("PGUSER")
DATABASE_PASSWORD = os.getenv("PGPASSWORD")

PORT = os.getenv("PGPORT")

db = MySQLDatabase(
    DATABASE_NAME, user=DATBASE_USER, password=DATABASE_PASSWORD, port=PORT
)


class Product(Model):
    image = CharField()
    description = TextField()
    price = FloatField()

    class Meta:
        database = db


class Complaint(Model):
    image = CharField()
    phone_number = CharField()
    description = TextField()

    class Meta:
        database = db


def create_connection():
    db.connect()


def close_connection():
    db.close()


def create_product_tables():
    with db:
        db.create_tables([Product])


def create_complaint_tables():
    with db:
        db.create_tables([Complaint])


def get_all_products():
    products = Product.select()
    return products


def save_order():
    pass
