# Financial Assistant with RBAC and Multi-Agent AI

An AI assistant for a finance team. It answers questions about a company's financial statements and internal reports. Each users only sees what their role allowed. 

All data is **synthetic**. The company, **Nexora Retail Holdings Inc**, is fictional. 

Built with free tools only.

**What it does**
- Answers exact figures from financial statements.
- Answers explanations from internal text reports.
- Enforces **role-based access control (RBAC)** for 3 roles: exec, manager, staff.
- Uses a small team of **AI agents**: A Manager routes each question to a Data agent or a Document agent.

**Architecture**
```
User question + role (role comes from code, never from the user or the model)
        │
        ▼
   Manager agent ── decides who should answer
     │                     │
     ▼                     ▼
 Data agent           Document agent
 (get_value_csv)      (answer_question)
     │                     │
     ▼                     ▼
 CSV files            Text reports in ChromaDB
 (pandas lookup,      (filtered by role tier
  allowed columns      before search)
  per role)
```
All agents share **one reusable agent loop (run_agent)**. Each agent only brings its own rules (system prompt) and its own tools.

**How RBAC works**
Security is enforced in code, **before the model sees any data.**
- Unknown role -> Access Denied
- CSV files     : each role has a list of allowed columns. A column outside the list returns **Access Denied**.
- Text reports  : each chunk is stored with a role tier. The search only looks at chunks the role may see.
- The model only receives the context the role is allowed to see. It cannot leak what it never received.
- The role is passed by code through every agent. The model cannot change it.

**How it works**
1. **Ingestion**  : text reports are split into chunks, embedded with **all-MiniLM-L6-v2**, and stored in ChromaDB with role_tier metadata.
2. **CSV lookup** : exact figures are read directly with pandas. No embeddings.
3. **Validation** : tools inputs written by the model are checked in code before use.
4. **Agent loop** : the model picks a tool, code runs it with the real role, the result goes back to the model, repeat until it answers (max 5 rounds).
5. **Multi-agent**: the Manager's tools are the 2 helper agents.

**Tech stack**
- Python, Pandas
- sentence-transformer(all-MiniLM-L6-v2)
- ChromaDB
- Groq API, model openai/gpt-oss-20b
- OpenAI-compatible tool calling
- Jupyter notebooks for testing

**Setup**
1. Clone the repo.
2. Install the packages: pip install -r requirements.txt
3. Create a .env file with your Groq API key. (.env is git-ignored and never committed.)
4. Run the ingestion once to build chroma_db/ (git-ignored).
5. Open the test notebook and run the cells in order.

**Disclaimer**
All data is synthetic and created for learning. Nexora Retail Holdings Inc. is a fictional company.
