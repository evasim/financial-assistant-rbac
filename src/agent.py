import json
from llm import answer_question, answer_csv_question, check_forms, income_csv, balance_csv, cash_csv, valid_columns
from llm import client

tools = [
    {
        "type": "function", 
        "function":{
            "name": "get_value_csv", 
            "description":"Get one exact number from a financial statement (income statement, balance sheet, cash flow) for one quarter. Use this for any specific figure like revenue, net income, ending cash or total assets.",
            "parameters":{
                "type":"object",
                "properties":{
                    "file":{
                        "type":"string",
                        "enum":["income_statement","balance_sheet","cash_flow_statement"],
                    },
                    "quarter":{"type":"string", "description":"format YYYY-Qn, like 2025-Q3. Convert wording like 'third quarter of 2025' to 2025-Q3."},
                    "column":{"type":"string", "description": f"Exact column name. Valid columns by file: {valid_columns}"},
                },
                "required":["file","quarter","column"], 
            }
        }
    },

    {
        "type": "function",
        "function":{
            "name":"answer_question",
            "description":"Search the narrative text documents for explanations, reasons, plans, risks and budgets. Do not use this for exact financial statement figures for a specific quarter.",
            "parameters":{
                "type":"object",
                "properties":{                    
                    "question":{"type":"string", "description":"the user's question in plain words"},
                },
                "required":["question"]
            }
         }
    }
]

def run_tool(name, args, role_tier):
    if name == "get_value_csv":
        form ={
            "source":"csv",
            "file":args["file"],
            "quarter":args["quarter"],
            "column":args["column"],
        }
        if not check_forms(form):
            return "Invalid request. Check the file, column and quarter."
        csv_files ={
            "income_statement": income_csv,
            "balance_sheet":balance_csv,
            "cash_flow_statement": cash_csv,
        }
        return answer_csv_question(
            csv_files[args["file"]], args["file"], args["quarter"], args["column"], role_tier
        )
    elif name == "answer_question":
        return answer_question(args["question"], role_tier)
    else:
        return "Unknown tool"

SINGLE_PROMPT = (
    "You are a financial assistant. "
    "Use the tools to find facts. "
    "Answer only from the tool results. "
    "For any exact figure for a specific quarter, such as ending cash, revenue or net income, use get_value_csv. "
    "Use answer_question for explanations, reasons, plans and risks. These do not need quarter or year, so just search. "
    "Report numbers exactly as the tool gives them. Do not add units and do not convert them. "
    "If a tool says Access Denied, reply: Access Denied. "
    "If a tool says Invalid request, fix the inputs and try once more. If it still fails, ask the user to include a valid quarter between 2021-Q1 and 2025-Q4. "
    "Only if the user asks for an exact number, such as revenue, net income or ending cash, and gives no quarter, do not use a tool. Ask which quarter they mean. "
    "If the tools do not have the answer, say \"I don't know\". "
    "Never guess numbers."
)

def run_agent(question, role_tier, system_prompt, tools, tool_runner, max_rounds=5):
    if role_tier not in ["exec", "manager", "staff"]:
        return "Access Denied"
    messages = [
        {
            "role":"system", 
            "content": system_prompt,
        },
        {"role":"user","content":question},
    ]

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model = "openai/gpt-oss-20b", 
            messages=messages, 
            tools=tools, 
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or "Sorry, I could not produce an answer."

        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = tool_runner(call.function.name, args, role_tier)
            #print("TOOL:", call.function.name, args, "->", result)
            messages.append({
                "role":"tool", 
                "tool_call_id":call.id, 
                "content":str(result),
            })

    return "Sorry, I could not finish this request" 

def run_single(question, role_tier):
    return run_agent(question, role_tier, SINGLE_PROMPT, tools, run_tool) 