#!/usr/bin/env python3

from bs4 import BeautifulSoup

import webbrowser
import tempfile
import requests
import getpass
import pickle
import os

# Disable warnings in requests vendored urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class trashmail:
	def __init__(self):
		self.domain			= 'fake-box.com'
		self.url_inbox		= 'https://www.trash-mail.com/inbox/'
		self.url_message	= 'https://www.trash-mail.com/en/mail/message/id/'
		self.cafile			= './trash-mail.pem'
		self.cookiefile		= 'trash-mail.cookie'

	def save_cookies(self, requests_cookiejar):
		with open(self.cookiefile, 'wb') as f:
			pickle.dump(requests_cookiejar, f)

	def load_cookies(self):
		with open(self.cookiefile, 'rb') as f:
			return pickle.load(f)

	def save_message(self, n):
		response = requests.post(self.url_message + n, cookies=self.cookies, verify=self.cafile)
		soup = BeautifulSoup(response.text, "html.parser")
		info 	= soup.find('div', {'class':'message-info'})
		content = soup.find('div', {'class':'message-content'})
		with tempfile.NamedTemporaryFile(mode='w+t', suffix=".html", delete=True) as f:
			f.write(str(info))
			f.write(str(content))
			f.seek(0)
			webbrowser.open("file://" + f.name)
			print("Output: file://" + f.name)
			input("[Enter] Delte and Contiune...")

	def login(self):
		usr     = input("User: ")
		domain	= input("Domain: ")
		pwd     = getpass.getpass("Password: ")
		payload = ({'form-postbox': usr,
					'form-password': pwd,
					'form-domain': domain + '---1'})
		response = requests.post(self.url_inbox, data=payload, verify=self.cafile)
		self.html 		= response.text
		self.cookies 	= response.cookies
		self.save_cookies(response.cookies)

	def login_with_cookies(self):
		self.cookies = self.load_cookies()
		response = requests.post(self.url_inbox, cookies=self.cookies, verify=self.cafile)
		if (response.headers['Connection'] == 'close'):
			print("Session closed!")
			self.login()
		else:
			self.html		= response.text

	def list_messages(self):
		soup 		= BeautifulSoup(self.html, "html.parser")
		self.mail 	= soup.find('a', {'class':'nolink-default'}).string
		print("Logged in as " +  self.mail)

		messages=soup.findAll('p', {'class':'message-subject'})
		i=len(messages)+1
		for m in messages:
			i-=1
			print("[" + str(i) + "] " + m.string)

if(__name__ == '__main__'):

	mail = trashmail()

	if os.path.isfile('trash-mail.cookie'):
		mail.login_with_cookies()
	else:
		mail.login()

	mail.list_messages()
	n = input("Open Nr.: ")
	mail.save_message(n)
