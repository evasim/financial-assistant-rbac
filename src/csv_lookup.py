import pandas as pd

def import_csv(csv_file_path):
    csv = pd.read_csv(csv_file_path)
    return csv 

def lookup_csv(csv, quarter_csv, column_csv):
    csv_row = csv.loc[csv["quarter"] == quarter_csv, column_csv]
    return csv_row

def get_value_csv(csv, file_name, quarter_csv, column_csv, role_tier_csv):
    csv_values = csv.loc[csv["quarter"] == quarter_csv, column_csv]
    if file_name == "balance_sheet":
        csv_allowed_column = {
        "exec": ["cash", "accounts_receivable", "inventory", "ppe_net", "total_assets",
             "accounts_payable", "short_term_debt", "long_term_debt", "total_liabilities",
             "common_stock", "retained_earnings", "total_equity", "total_liabilities_and_equity"],
        "manager" : ["cash", "total_assets", "total_liabilities", "total_equity", "total_liabilities_and_equity"], 
        "staff" :[]
    }
    elif file_name == "cash_flow_statement":
        csv_allowed_column = {
        "exec" : ["net_income", "depreciation", "change_in_ar", "change_in_inventory",
                 "change_in_ap", "cash_from_operations", "capital_expenditures",
                 "cash_from_investing", "dividends_paid", "debt_repayment",
                 "cash_from_financing", "net_change_in_cash", "ending_cash_balance"],
        "manager" : ["net_change_in_cash", "ending_cash_balance"], 
        "staff" : []
    }
    elif file_name == "income_statement":
        csv_allowed_column = {
    "exec": ["revenue", "cogs", "gross_profit", "marketing_expense", "logistics_expense", "it_expense", "ga_expense", "payroll_expense", "net_income"],
    "manager": ["revenue", "net_income"],
    "staff": []
    }
    else:
        return "Unknown file"

    if column_csv in csv_allowed_column[role_tier_csv]:
        return csv_values
    else: 
        return "Access Denied"


   