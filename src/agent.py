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