import logging

logger = logging.getLogger("chat")

SYSTEM_PROMPT = """You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply."""


def ask(client, store_name: str, question: str, model_name: str) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=question,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "tools": [
                {"file_search": {"file_search_store_names": [store_name]}}
            ],
        },
    )
    return response.text
