# Methods for obtaining data from ICG Admin
#
#
#
#

import cookielib
import urllib2
import urllib
import getpass
from datetime import date
from bs4 import BeautifulSoup

def gain_authentication():
	url = raw_input('Domain URL (domain.com): ')
	user = raw_input('Username: ')
	passw = getpass.getpass('Password: ')
	
	admin_authentication_url = 'https://' + url + '/admin/login.cfm'

	#Store the login cookie and create an opener to hold them
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	#Admin Login Parameters
	payload = {
		'adminID': user,
		'strPassword': passw
		}
	#Encode the payload & request
	login_data = urllib.urlencode(payload)

	#Send/receive login request and data
	opener.open(admin_authentication_url, login_data)
	return (opener, url)

def makeNum(old):
	if isinstance(old, list):
		new = []
		for i in old:
			j = i.replace("$","")
			k = j.replace(",","")
			new.append(float(k))
		return new					#Returns list in float type

	elif isinstance(old, str):
		j = old.replace("$","")
		k = j.replace(",","")
		new = float(k)
		return new					#Returns float

def get_month_sales(url, sm, em, opener, day, year, kind):
# sm:start month, em:end month, opener, day, year, kind:mtd or ytd	
	vendors = ['','NoVendor','Amazon','Amazon-FBA']
	sales_url = 'https://' + url + '/admin/monsterbrew-reports-sales-daily.cfm'
	
	for i in vendors:
		print 'Getting', sm, '/', year, 'sales report data for', i
		payload = {
			'intFromMonth': int(sm),
			'intFromDay': 1,
			'intFromYear': year,
			'intToMonth': int(em),
			'intToDay': day,
			'intToYear': year,
			'vendorID': i,
			'submitForm': 'submit'
			}
		
		# Encode the payload & request
		date_data = urllib.urlencode(payload)
	
		# Send request
		resp = opener.open(sales_url, date_data).read()
		with open ('archive/' + str(year) + kind + '_sales_' + i + '.html', 'w') as fid:
			fid.write(resp)

def get_month_profit(url, sm, em, opener, day, year, kind):
# sm:start month, em:end month, opener, day, year, kind:mtd or ytd
	vendors = ['','NoVendor','Amazon','Amazon-FBA']
	sales_url = 'https://' + url + '/admin/monsterbrew-profit-report.cfm'
	
	for i in vendors:
		print 'Getting', sm, '/', year, 'profit report data for', i
		payload = {
			'intFromMonth': int(sm),
			'intFromDay': 1,
			'intFromYear': year,
			'intToMonth': int(em),
			'intToDay': day,
			'intToYear': year,
			'vendorID': i,
			'submitForm': 'submit'
			}
		
		# Encode the payload & request
		date_data = urllib.urlencode(payload)
	
		# Send request
		resp = opener.open(sales_url, date_data).read()
		#page_content = resp.read()
		with open ('archive/' + str(year) + kind + '_profit_' + i + '.html', 'w') as fid:
			fid.write(resp)

def get_month_product(url, sm, em, opener, day, year, kind):
# sm:start month, em:end month, opener, day, year, kind:mtd or ytd
	vendors = ['NoVendor']
	sales_url = 'https://' + url + '/admin/monsterbrew-reports.cfm'
	
	for i in vendors:
		print 'Getting', sm, '/', year, 'product report data for', i
		payload = {
			'intFromMonth': int(sm),
			'intFromDay': 1,
			'intFromYear': year,
			'intToMonth': int(em),
			'intToDay': day,
			'intToYear': year,
			'vendorID': i,
			'submitForm': 'submit'
			}
		
		# Encode the payload & request
		date_data = urllib.urlencode(payload)
	
		# Send request
		resp = opener.open(sales_url, date_data).read()
		with open ('archive/' + str(year) + kind + '_product_' + i + '.html', 'w') as fid:
			fid.write(resp)

def mine_getHeaders(infile):
	html_doc = open(infile).read()
	soup = BeautifulSoup(html_doc.replace('iso-8859-1', 'utf-8'))
	table = soup.findAll("table", {"cellpadding":"3","border":"1"} )
	header = []
	data = []

	for t in table:
		rows = t.findAll('tr')				#Holds Each Row of data
		entries = (len(rows)-3)/3			#Number of Days of data
	
		head = rows[0].findAll('td')			#Capture Header Data 
		for j in range(0, len(head)):
				a = str(head[j]).split("<strong>")
				b = str(a[1]).split("</strong>")
				header.append(b[0])
	return header						#Returns string list of header data for infile

def mine_getSalesData(infile):
	html_doc = open(infile).read()
	soup = BeautifulSoup(html_doc.replace('iso-8859-1', 'utf-8'))
	table = soup.findAll("table", {"cellpadding":"3","border":"1"} )
	data = []
	sales = []

	for t in table:
		rows = t.findAll('tr')				#Holds Each Row of data
		entries = (len(rows)-3)/3			#Number of Days of data
		head = rows[0].findAll('td')			#Capture Header Data 
		for j in range(0, len(head)):
				data.append([])

		for i in range (2, len(rows)-2, 3):		#Determine lines with Purchase Data
			columns = rows[i].findAll('td') 	#Holds Each Column of Data of Row i
			count = 0
			for j in range(0, len(columns)):
				a = str(columns[j]).split(">")
				b = str(a[1]).split("<")
				d = b[0]			#Capture Data stripped of HTML code
				data[count].append(d)
				count = count + 1
	sales = data[:2]
	for i in data[2:]:
		sales.append(makeNum(i))	
	return sales					#Returns String Matrix of per day sales data for infile
	
def mine_getSalesRefund(infile):
	html_doc = open(infile).read()
	soup = BeautifulSoup(html_doc.replace('iso-8859-1', 'utf-8'))
	table = soup.findAll("table", {"cellpadding":"3","border":"1"} )
	data = []

	for t in table:
		rows = t.findAll('tr')				#Holds Each Row of data
		entries = (len(rows)-3)/3			#Number of Days of data
		head = rows[0].findAll('td')			#Capture Header Data 
		for j in range(0, len(head)):
				data.append([])

		for i in range (3, len(rows)-2, 3):		#Determine lines with Purchase Data
			columns = rows[i].findAll('td') 	#Holds Each Column of Data of Row i
			count = 0
			for j in range(0, len(columns)):
				a = str(columns[j]).split(">")
				b = str(a[1]).split("<")
				d = b[0]			#Capture Data stripped of HTML code
				data[count].append(d)
				count = count + 1
		
	return data						#Returns String Matrix of per day refund data for infile

def mine_getProfitData(infile):
	html_doc = open(infile).read()
	soup = BeautifulSoup(html_doc.replace('iso-8859-1', 'utf-8'))
	table = soup.findAll("table", {"cellpadding":"3","border":"1"} )
	profit = ''

	for t in table:
		rows = t.findAll('tr')				#Holds Each Row of data
		head = rows[0].findAll('td')			#Capture Header Data 
		columns = rows[3].findAll('td')
		a = str(columns[7]).split(">")
		b = str(a[1]).split("<")
		d = b[0]					#Capture Data stripped of HTML code
		profit = d
	return profit						#Returns string of profit value from infile

def mine_getProductData(infile):
	html_doc = open(infile).read()
	soup = BeautifulSoup(html_doc.replace('iso-8859-1', 'utf-8'))
	table = soup.findAll("table", {"cellpadding":"2","border":"1"} )
	data = []
	
	for t in table:
		rows = t.findAll('tr')				#Holds Each Row of data
		entries = (len(rows)-3)/3			#Number of Days of data
		head = rows[1].findAll('td')			#Capture Header Data 
		for j in range(0, len(head)):
				data.append([])

		for i in range (2, len(rows)-1):		#Determine lines with Product Data
			columns = rows[i].findAll('td') 	#Holds Each Column of Data of Row i
			count = 0
			for j in range(0, len(columns)):
				a = str(columns[j]).split(">")
				b = str(a[1]).split("<")
				d = b[0]			#Capture Data stripped of HTML code
				data[count].append(d)
				count = count + 1
	return data						#Returns String Matrix of product data for infile
