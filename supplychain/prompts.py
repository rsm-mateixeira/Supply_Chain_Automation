from langchain.prompts import PromptTemplate

# Define database schema description
schema_description = """Table: supply_chain
Columns:
- Location (TEXT)
- Date (TEXT)
- Predicted_Demand (INTEGER)
- Existing_Capacity (INTEGER)
- Increase_Capacity (TEXT)
- Units_Increase (INTEGER)
- Supplier_Chosen (TEXT)
- Order_Cost (INTEGER)"""

query_summarization_prompt = PromptTemplate(
    input_variables=["chat_history", "new_question"],
    template=(
        "You are assisting a user with supply chain data retrieval. "
        "Below is the history of their questions and your answers:\n\n"
        "{chat_history}\n\n"
        "The user has now asked: {new_question}\n\n"
        "Rules:\n"
        "- Be cautious about the questions before, and the city you should create the query about.\n"
        "- If the user specifies a location, ONLY generate an intent relevant to that location.\n"
        "- Summarize their request into a structured intent that captures the meaning of all past interactions while avoiding redundant or irrelevant details.\n\n"
        "Output a structured, human-readable intent statement that can be used to generate an accurate SQL query.\n\n"
        "Summarized Intent:"
    )
)


sql_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=(
        "Convert the following natural language question into a valid SQL query "
        "based on this database schema:\n\n{schema}\n\n"
        "Rules:\n"
        "- If the user asks about 'when to increase capacity,' return ONLY rows where `Increase_Capacity = 'Yes'`, "
        "including only the columns `Date` and `Units_Increase`.\n"
        "- If the user asks 'By how much?', return ONLY the 'Units_Increase' column.\n"
        "- If the user asks about suppliers, return ONLY the 'Supplier_Chosen' column.\n"
        "- If the user specifies a city, filter the data only for that city.\n"
        "- Only return the raw SQL query without any formatting like triple quotes (```sql ... ```).\n\n"
        "User Question: {question}\n\n"
        "SQL Query:"
    )
)



answer_prompt = PromptTemplate(
    input_variables=["question", "query_result"],
    template=(
        "The user asked: {question}\n\n"
        "Here is the data retrieved from the database:\n{query_result}\n\n"
        "Rules for generating a response:\n"
        "- Rephrase the response in a natural and professional way.\n"
        "- Do NOT simply list the raw data; incorporate it into a full sentence.\n"
        "- Avoid over-explaining or adding unnecessary details.\n\n"
        "Final Answer:"
    )
)

