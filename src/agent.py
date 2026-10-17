import json
from llm import answer_question, answer_csv_question, check_forms, income_csv, balance_csv, cash_csv
from llm import client

tools = [
    {
        "type": "function", 
        "function":{
            "name": "get_value_csv", 
            "description":"Get one number from a financial statement for one quarter.",
            "parameters":{
                "type":"object",
                "properties":{
                    "file":{
                        "type":"string",
                        "enum":["income_statement","balance_sheet","cash_flow_statement"],
                    },
                    "quarter":{"type":"string", "description":"like 2025-Q3"},
                    "column":{"type":"string", "description": "column name, like net_income"},
                },
                "required":["file","quarter","column"], 
            }
        }
    },

    {
        "type": "function",
        "function":{
            "name":"answer_question",
            "description":"Search the company text documents for explanations, reasons, plans or risks.",
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

def run_agent(question, role_tier, max_rounds=5):
    if role_tier not in ["exec", "manager", "staff"]:
        return "Access Denied"
    messages = [
        {
            "role":"system", 
            "content":(
                "You are a financial assistant. "
                "Use the tools to find facts. "
                "Answer only from the tool results. "
                "Report numbers exactly as the tool gives them. Do not add units and do not convert them. "
                "If a tool says Access Denied, reply: Access Denied. "
                "If a tool says Invalid request, ask the user to include a valid quarter between 2021-Q1 and 2025-Q4. "
                "If the tools do not have the answer, say \"I don't know\". "
                "Never guess numbers."
            ),
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
            result = run_tool(call.function.name, args, role_tier)
            #print("TOOL:", call.function.name, args, "->", result)
            messages.append({
                "role":"tool", 
                "tool_call_id":call.id, 
                "content":str(result),
            })

    return "Sorry, I could not finish this request"  