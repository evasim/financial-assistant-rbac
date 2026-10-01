import os 
from dotenv import load_dotenv
from groq import Groq
from embed_pipeline import collection, model
from csv_lookup import get_value_csv

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
    answer_result = collection.query(
        query_embeddings= model.encode([question]).tolist(),
        n_results = 1, 
        where={"role_tier":role_tier}
    )
    answer_context = answer_result["documents"][0][0]
    answer = ask_llm(question, answer_context)
    return answer 

# for csv LLM function 
def answer_csv_question(answer_csv, csv_file_name, csv_quarter, csv_column, csv_role_tier):
    value = get_value_csv(answer_csv, csv_file_name, csv_quarter, csv_column, csv_role_tier)
    value = value.values[0]
    context_sentence = f"{csv_column} for {csv_quarter} : {value}" # in sentence form so that LLM have something to read
    answers_csv = ask_llm(f"What is the {csv_column} for {csv_quarter}?", context_sentence)
    return answers_csv