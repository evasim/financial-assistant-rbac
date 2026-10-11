import os 
import json
from dotenv import load_dotenv
from csv_lookup import import_csv
from groq import Groq
from embed_pipeline import collection, model
from csv_lookup import get_value_csv
income_csv = import_csv("../data/income_statement.csv")
balance_csv = import_csv("../data/balance_sheet.csv")
cash_csv = import_csv("../data/cash_flow_statement.csv")

load_dotenv()
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

def ask_llm(question, context):
    prompt = f"""Answer the question using only the context below. If the answer is not in context, say "I don't know".
    
    Context : {context}

    Question : {question}
    """
    response = client.chat.completions.create(
        model = "openai/gpt-oss-20b", 
        messages= [{"role":"user", "content": prompt}]
    )
    return response.choices[0].message.content

# for .txt LLM function
def answer_question(question, role_tier):
    visible_tier = {
        "exec" :["exec", "manager", "staff"],
        "manager" : ["manager", "staff"],
        "staff" :["staff"]
    }
    answer_result = collection.query(
        query_embeddings= model.encode([question]).tolist(),
        n_results = 1, 
        where={"role_tier":{"$in":visible_tier[role_tier]}}
    )
    answer_context = answer_result["documents"][0][0]
    answer = ask_llm(question, answer_context)
    return answer 

# for csv LLM function 
def answer_csv_question(answer_csv, csv_file_name, csv_quarter, csv_column, csv_role_tier):
    value = get_value_csv(answer_csv, csv_file_name, csv_quarter, csv_column, csv_role_tier)
    if isinstance(value, str):
        return value 
    value = value.values[0]
    context_sentence = f"{csv_column} for {csv_quarter} : {value}" # in sentence form so that LLM have something to read
    answers_csv = ask_llm(f"What is the {csv_column} for {csv_quarter}?", context_sentence)
    return answers_csv

def route_question(question):
    prompt = f"""Read the question. Reply with JSON only. No other words.
    
    If the question ask for a number from financial statement, reply like this:
    {{"source": "csv", "file":"income_statement", "quarter":"2025-Q3", "column":"net_income"}}
    
    If the question ask about report or an explanation, reply like this:
    {{"source":"txt"}}
    
    file must be balance_sheet, cash_flow_statement, income_statement.
    quarter must look like 2025-Q3
    column must underscores, like net_income.

    Valid columns for each file:
    {valid_columns}

    column must be one of the valid columns for that file.
    If the question does not state a quarter, leave quarter out. Never guess one.
    
    Question: {question}
    """
    response = client.chat.completions.create(
        model = "openai/gpt-oss-20b",
        messages= [{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)

valid_columns = {
    "income_statement":[
        "revenue", "cogs", "gross_profit", "marketing_expense", "logistics_expense", "it_expense", "ga_expense",
        "payroll_expense", "total_operating_expense", "operating_income", "interest_expense", "pretax_income", 
        "tax_expense", "net_income"
    ], 
    "balance_sheet":[
        "cash", "accounts_receivable", "inventory", "ppe_net", "total_assets", "accounts_payable", 
        "short_term_debt", "long_term_debt", "total_liabilities", "common_stock", "retained_earnings", 
        "total_equity", "total_liabilities_and_equity"
    ], 
    "cash_flow_statement":[
        "net_income", "depreciation", "change_in_ar", "change_in_inventory", "change_in_ap", "cash_from_operations", 
        "capital_expenditures", "cash_from_investing", "dividends_paid", "debt_repayment", "cash_from_financing", 
        "net_change_in_cash", "ending_cash_balance" 
    ]
}

valid_quarters = [f"{y}-Q{q}" for y in range(2021, 2026) for q in range(1, 5)]

def check_forms(form):
    if form["source"] == "txt":
        return True 
    elif form["file"] not in valid_columns:
        return False
    elif form["column"] not in valid_columns [form["file"]]:
        return False
    elif form.get("quarter") not in valid_quarters:
        return False
    else: 
        return True 

def handle_question(question, role_tier):
    form = route_question(question)

    if not check_forms(form):
        return "Sorry, I could not understand that. Please include a quarter, like 2025-Q3."
    if form["source"] == "txt":
        return answer_question(question, role_tier)
    csv_files = {
        "income_statement" : income_csv, 
        "balance_sheet" : balance_csv, 
        "cash_flow_statement" : cash_csv, 
    }
    return answer_csv_question(
        csv_files[form["file"]], form["file"], form["quarter"], form["column"], role_tier
    )