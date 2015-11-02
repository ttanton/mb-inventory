import pandas as pd
import numpy as np
import math
from pprint import pprint
import csv
import urllib2
import icgadmin
import os

print "\n\nRunning MB Inventory Analysis..."
print "Requesting Authorization..."

auth = icgadmin.gain_authentication()
opener = auth[0]
domain = auth[1]

inv_proc_url = 'https://' + domain + '/admin/mbinventorylist.cfm'
inv_down_url = 'https://' + domain + '/admin/MB_Product_list.xls'


print "Downloading current MB Inventory..."
resp = opener.open(inv_proc_url).read()
resp = opener.open(inv_down_url)
inv_file = os.path.basename(inv_down_url)
with open(os.path.basename(inv_down_url), "wb") as local_file:
	local_file.write(resp.read())
#f = "MB_Product_list.xls"
xls_file = pd.ExcelFile(inv_file)
data = xls_file.parse('Sheet1')

print "Downloading current Inventory Limits from Google Drive..."
limits_url = "https://docs.google.com/spreadsheets/d/1r_6OMoaorVeAKdsSNMXLMHzhbFkXlz3VGHN9f167rFg/export?format=csv"
response = urllib2.urlopen(limits_url)
f2 = response.read()

#write limits file locally for reference
with open("inventory-limits.csv", "wb") as local_file:
	local_file.write(f2)

print "Cleaning Inventory Limits"
data2 = []
for i in f2.split('\r'):
    #data2.append(i.split(','))
    j= i.split(',')
    for k in range(0, len(j)):
        j[k] = j[k].strip('\n')
    data2.append(j)
    
#f2 = 'product_limits.csv'
limits = pd.DataFrame(data2, columns=data2[0])
limits = limits.drop(0)
#print limits

print "Matching Available Limits to Inventory Items..."
inv = data.values
alt = limits.values
for i in range(0,len(alt)):
    for j in range(4,9):
        alt[i][j] = (float(alt[i][j]) if alt[i][j] else 0)
        
#print inv[1]
#print alt[17]
#print type(alt[1][4])

print "Building Order List..."
alert_list = []
for i in inv:
    for j in alt:
        if str(i[0]) == str(j[0]) and j[5]>0 and j[8]!=1:
            alert_list.append([unicode(i[2]),i[3],i[1],float(i[4]),j[4],j[5],j[6],j[7],j[8]])
#print alert_list[1]
#for i in alert_list: print i

suppliers = []
orderlist = []
for i in alert_list:
    suppliers.append(i[1])
suppliers = set(suppliers)
#print suppliers


print "\nOut of Stock Listings..."
for j in alert_list:
	if j[3]==0:
		print j[2]

print "\nSupplier Needs At-A-Glance..."
glance = []
for i in suppliers:
    count = 0
    for j in alert_list:
		if i == j[1] and j[4]>=j[3]:
			count += 1
			qty = j[5] - j[3]
			if j[6]>0:
				qty = math.ceil(qty/j[6])*j[6]
			elif j[5]>=15:
				qty = math.ceil(qty/10.0)*10
			if j[7]>0:
				qty = qty/j[7]
			orderlist.append([j[1], j[0], qty, j[2]])
    glance.append([str(count), str(i)])
	#print str(count) + " low products from " + str(i)
	
def getKey(item):
	return item[0]

glance = sorted(glance, key=getKey, reverse=True)

for i in glance:
	print i[0] + " low products from " + i[1]

#pprint(orderlist)
print "\nSaving order sheet to order_list.csv"
with open('order_list.csv', 'wb') as w:
    wr = csv.writer(w, delimiter=',')
    for i in orderlist:
        wr.writerow(i)
		
trash = raw_input('Press Enter to Exit... ')