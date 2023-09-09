import selenium.common.exceptions
from flask import Flask
from flask import request
from flask import render_template
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import time
import os
from thefuzz import fuzz
from thefuzz import process

service = Service('C:/Windows/chromedriver')
driver = webdriver.Chrome(service=service)
url = 'https://account.labx.com/customer/account/login'
driver.get(url)

EMAIL = '*******************'
PASSWORD = '************'

email_input = driver.find_element(By.ID, 'email')
password_input = driver.find_element(By.ID, 'password')

email_input.send_keys(EMAIL)
password_input.send_keys(PASSWORD)

sign_in = driver.find_element(By.CLASS_NAME, 'signInBtn')
sign_in.click()

driver.find_element(By.PARTIAL_LINK_TEXT, 'Inquiries').click()
time.sleep(1)

keep_going = True
name_list = []
product_list = []
sku_list = []
company_list = []
phone_list = []
email_list = []
street_list = []
city_list = []
state_list = []
country_list = []
zip_list = []

while keep_going:
    inquiries = driver.find_elements(By.TAG_NAME, 'tr')[1:]
    for i in inquiries:
        columns = i.find_elements(By.TAG_NAME, 'td')
        if '2023' in columns[0].text:
            view_link = columns[-1].find_element(By.CLASS_NAME, 'editbtn').get_attribute('href')
            # print(view_link)
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(view_link)
            # time.sleep(0.5)
            try:
                contact_container = driver.find_element(By.CLASS_NAME, 'yourContactInfoContainer')
                contact_info = contact_container.find_elements(By.TAG_NAME, 'div')[0].find_elements(By.TAG_NAME, 'p')
                address_element = contact_container.find_elements(By.TAG_NAME, 'div')[1].find_elements(By.TAG_NAME, 'p')
                product_container = driver.find_element(By.CLASS_NAME, 'yourProductInfoContainer')
                product_name = product_container.find_element(By.TAG_NAME, 'a').text
                product_sku = product_container.find_elements(By.TAG_NAME, 'strong')[1].text
                name_list.append(contact_info[0].text.split(': ')[1])
                product_list.append(product_name)
                sku_list.append(product_sku)
                try:
                    company_list.append(contact_info[1].text.split(': ')[1])
                except IndexError:
                    company_list.append('null')
                phone_list.append(contact_info[2].text.split(': ')[1])
                email_list.append(contact_info[3].text.split(': ')[1])
                street_list.append(address_element[0].text.split(': ')[1])
                city_list.append(address_element[1].text.split(': ')[1])
                state_list.append(address_element[2].text.split(': ')[1])
                country_list.append(address_element[3].text.split(': ')[1])
                zip_list.append(address_element[4].text.split(': ')[1])
            except selenium.common.exceptions.NoSuchElementException:
                print('Error Loading Page')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            keep_going = False
    page_buttons = driver.find_element(By.CLASS_NAME, 'pages').find_elements(By.TAG_NAME, 'div')
    page_buttons[-2].click()
    print('next page')

engine = create_engine('sqlite://',
                        connect_args={'check_same_thread': False},
                        poolclass=StaticPool)

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'labx-inquiries.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'labx_python'
db = SQLAlchemy(app)


class Inquiries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    product = db.Column(db.String(250), nullable=False)
    sku = db.Column(db.String(250), nullable=False)
    company = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    street = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    country = db.Column(db.String(250))
    zip_code = db.Column(db.String(250))


with app.app_context():
    db.create_all()
    for i in range(0, len(name_list)):
        new_item = Inquiries(name=name_list[i], product=product_list[i], sku=sku_list[i], company=company_list[i],
                         phone=phone_list[i], email=email_list[i], street=street_list[i], city=city_list[i],
                         state=state_list[i], country=country_list[i], zip_code=zip_list[i])
        db.session.add(new_item)

    db.session.commit()
