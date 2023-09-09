import pandas as pd
from flask import Flask
from sqlalchemy import create_engine
import os

basedir = os.path.abspath(os.path.dirname(__file__))
my_path = basedir + '\labx-inquiries.db'
engine = create_engine('sqlite:///' + my_path)
print(my_path)

app = Flask(__name__)

with app.app_context():
    query = "SELECT * FROM inquiries"
    df = pd.read_sql(query, con=engine)
    print(df.head())
    df.to_excel('labx_inquiries_2023.xlsx')
