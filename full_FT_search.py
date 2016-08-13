# import re
from bs4 import BeautifulSoup
import requests
from collections import OrderedDict


def find_table_index(financial_category,table_list):
	"""
	DESCRIPTION
	The internet page may contain several tables.
	For FT market searches, we are interested in three financial categories: BalanceSheet, CashFlow and IncomeStatement
	In each internet page, the data is contained in ONE table which we identify with a keyword. 
	For instance, the table of interest in the BalanceSheet page contains a line ASSET=(our keyword). 

	d_table is a dictionnary that indicates the keyword for each of the financial categories

	Then the program looks for all the tables of the webpage and identifies the one which contains the keyword. 
    
    ARGUMENTS
    financial_category		(string)					can be "BalanceSheet",  "CashFlow" or    "IncomeStatement"
    table_list				(list of HTML tables)		a list of HTML tables

	RETURN 
	the index of the table of interest 
	"""

	d_table ={"BalanceSheet": "ASSETS", "CashFlow":"OPERATIONS", "IncomeStatement":"REVENUE AND GROSS PROFIT" }

	for index, table in enumerate(table_list):
		if table.find("tr", text =d_table[financial_category])!=None:
			return index


def get_financial_data(financial_category, company_name):
	"""
	DESCRIPTION
	Look for a specific financial category of the given company name on the FT website

	The program first identifies the table of interest. 
	Then it loops over the fields of the table and returns it

    ARGUMENTS
    financial_category		(string)		can be "BalanceSheet",  "CashFlow" or    "IncomeStatement"
    company_name			(string)		Company full Symbol, e.g: ORCL:NYQ

	RETURN 
	a dictionnary cointaining all the fields of interest of the table
	"""
	r_bsheet = requests.get('http://markets.ft.com/research/Markets/Tearsheets/Financials?s=' + company_name + '&subview=' + financial_category)
	print r_bsheet.url
	soup = BeautifulSoup(r_bsheet.text)

	table_list  = soup.findAll('table')
	
	table_index =find_table_index(financial_category, table_list)

	table =table_list[table_index]
	list_rows=table.findAll('tr')

	#Use an ordered dictionnary to keep the structure of the table
	d_result_ordered=OrderedDict()

	for row in list_rows:
		list_col=row.findAll('td')
		d_result_ordered[str(list_col[0].getText())]=[]

		if list_col[1:]!=[]:
			for col in list_col[1:]:
				d_result_ordered[str(list_col[0].getText())].append(str(col.getText()))

	# print d_result_ordered
	for key in d_result_ordered.keys():
		print key
	return d_result_ordered


