#!/usr/bin/env python3

import requests, pickle
import getpass
import os
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_message(info, content, filename):
    with open(filename, 'w') as f:
        f.write(str(info))
        f.write(str(content))

def login():
    usr = input("Postbox: ")
    pwd	= getpass.getpass("Password: ")
    payload = {'form-postbox': usr, 'form-password': pwd, 'form-domain': 'fake-box.com---1'}
    return payload

url	= 'https://www.trash-mail.com/inbox/'
cafile	= './trash-mail.pem'
session = requests.session()


try:
	response = requests.post(url, cookies=load_cookies("trash-mail.cookie"), verify=cafile)
	if (response.headers['Connection'] == 'close'):
		print("Session closed!")
		payload = login()
		response = requests.post(url, data=payload, verify=cafile)
		save_cookies(response.cookies, 'trash-mail.cookie')

except IOError:
	payload = login()
	response = requests.post(url, data=payload, verify=cafile)
	save_cookies(response.cookies, 'trash-mail.cookie')

html = response.text
soup = BeautifulSoup(html, "html.parser")

mail = soup.find('a', {'class':'nolink-default'})
print("Logged in as: " + mail.string)

messages=soup.findAll('p', {'class':'message-subject'})
i=len(messages)+1
for m in messages:
	i-=1
	print("[" + str(i) + "] " + m.string)

q = input("Output message: ")

response = requests.post("https://www.trash-mail.com/en/mail/message/id/" + q, cookies=load_cookies("trash-mail.cookie"), verify=cafile)

html = response.text
soup = BeautifulSoup(html, "html.parser")

message_info 	= soup.find('div', {'class':'message-info'})
message_content = soup.find('div', {'class':'message-content'})

save_message(message_info, message_content, "out.html")
print("Output: file://" + str(os.getcwd()) + "/out.html")
