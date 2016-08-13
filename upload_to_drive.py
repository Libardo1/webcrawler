import gspread
import getpass
import sys

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
        gc.open(spreadsheet_name)
    except gspread.SpreasheetNotFound:
        print 'There is no spreadsheet named:', spreadsheet_name, ', please manually create it.'
        print 'Exiting ...'
        sys.exit()
    try:
        worksheet = spreadsheet.worksheet(financial_category)
    except gspread.worksheetNotFound:
        print 'There is no worksheet named:', financial_category, ', creating it...'
        worksheet = spreadsheet.add_worksheet(
            title=financial_category,
            rows="1000",
            cols="26")

    # Update the worksheet
    for key_index, key in enumerate(d_result_ordered.keys()):
        # Update the title of the row
        worksheet.update_cell(key_index, 1, str(key))
        # Update the columns
        col_list = d_result_ordered[key]
        for col_index, col_value in enumerate(col_list):
            worksheet.update_cell(key_index, col_index + 1, str(col_value))
