from bs4 import BeautifulSoup
import requests
from collections import OrderedDict
import gspread
import getpass
import sys
import python_colors as pyCol
import re


def find_table_index(financial_category, table_list):
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

    d_table = {
        "BalanceSheet": "ASSETS",
        "CashFlow": "OPERATIONS",
        "IncomeStatement": "REVENUE AND GROSS PROFIT"}

    for index, table in enumerate(table_list):
        if table.find("tr", text=d_table[financial_category]) is not None:
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
    r_bsheet = requests.get(
        'http://markets.ft.com/research/Markets/Tearsheets/Financials?s=' +
        company_name +
        '&subview=' +
        financial_category)
    print pyCol.COL('Gathering data from URL below:', 'blue')
    print r_bsheet.url
    soup = BeautifulSoup(r_bsheet.text)

    # Exit if the search is invalid
    search_error = soup.findAll(
        text=re.compile("No results were returned for"))
    print search_error
    if search_error != []:
        print pyCol.COL(search_error[0], 'fail')
        print pyCol.COL("Exiting...", "fail")
        sys.exit()

    table_list = soup.findAll('table')

    table_index = find_table_index(financial_category, table_list)

    table = ''
    try:
        table = table_list[table_index]
    except TypeError:
        print pyCol.COL("Invalid name, exiting ...", "fail")
        sys.exit()
    list_rows = table.findAll('tr')

    # Use an ordered dictionnary to keep the structure of the table
    d_result_ordered = OrderedDict()

    for row in list_rows:
        list_col = row.findAll('td')
        d_result_ordered[str(list_col[0].getText())] = []

        if list_col[1:] != []:
            for col in list_col[1:]:
                d_result_ordered[str(list_col[0].getText())].append(
                    str(col.getText()))

    return d_result_ordered


def upload_financial_data(
    financial_category,
    spreadsheet_name,
    gc,
        d_result_ordered):
    """
    DESCRIPTION
    Upload the table contained in the d_result_ordered dictionary to google Drive
    The financial_category must match with the contents of d_result_ordered

	ARGUMENTS
	financial_category		(string)			can be "BalanceSheet",  "CashFlow" or    "IncomeStatement"
	spreadsheet_name		(string)			the name of the spreadsheet to be updated. It should be the company name (e.g. Oracle)
	gc						(gspread class)		allows the access to Drive
	d_result_ordered		(dictionary)		contains the content of the financial_category for the company of interest

    RETURN
    None
    """
    spreadsheet = None
    worksheet = None
    try:
        spreadsheet = gc.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        print pyCol.COL('There is no spreadsheet named:', 'fail'), spreadsheet_name, pyCol.COL(', please manually create it.', 'fail')
        print pyCol.COL('Exiting ...', 'fail')
        sys.exit()
    try:
        worksheet = spreadsheet.worksheet(financial_category)
    except gspread.WorksheetNotFound:
        print pyCol.COL('There is no worksheet named:', 'warning'), financial_category, pyCol.COL(', creating it...', 'warning')
        worksheet = spreadsheet.add_worksheet(
            title=financial_category,
            rows="1000",
            cols="26")

    # Update the worksheet
    for key_index, key in enumerate(d_result_ordered.keys()):

        # Progress bar
        sys.stdout.write('\rProcessing line ' + str(key_index)
                         + ' / ' + str(-1 + len(d_result_ordered.keys())))
        sys.stdout.flush()

        # Update the title of the row
        worksheet.update_cell(key_index + 1, 1, str(key))
        # Update the columns
        col_list = d_result_ordered[key]
        for col_index, col_value in enumerate(col_list):
            worksheet.update_cell(key_index + 1, col_index + 2, str(col_value))
    print


def get_financial_data_and_upload(spreadsheet_name):

    print pyCol.COL("Type your google ID (e.g. john.wayne@gmail.com) then press ", "header") + pyCol.COL('<Enter>: ', 'green')
    email = raw_input()
    print

    pwd = getpass.getpass(
        pyCol.COL('Type password then press ',
                  'header') + pyCol.COL('<Enter>: ',
                                        'green'))  # command line prompt without echo
    print
    gc = gspread.login(str(email), pwd)

    print pyCol.COL('Type Company Symbol (e.g: ORCL:NYQ) then press ', 'header') + pyCol.COL('<Enter>: ', 'green')
    company_name = raw_input()
    # company_name = 'ORCL:NYQ'

    print pyCol.COL('Data for company ' + company_name + ' will be downloaded', 'blue')
    print

    financial_category_list = ["BalanceSheet", "CashFlow", "IncomeStatement"]

    for financial_category in financial_category_list:
        print pyCol.COL('Updating the ' + financial_category + ' category', 'blue')
        d_result_ordered = get_financial_data(financial_category, company_name)
        upload_financial_data(
            financial_category,
            spreadsheet_name,
            gc,
            d_result_ordered)