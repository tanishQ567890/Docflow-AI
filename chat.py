from graph import graph
from langchain_core.messages import HumanMessage
from utils import extract_text
from logger import logger
from node import stream_response
from langchain_core.messages import SystemMessage
from rag import save_uploaded_pdf
from rag import index_new_pdf
DEFAULT_THREAD = "default_user"

def chat(question, thread_id=DEFAULT_THREAD):

    config = {

        "configurable": {

            "thread_id": thread_id

        }

    }

    try:

        result = graph.invoke(

            {

                "messages": [

                    HumanMessage(

                        content=question

                    )

                ]

            },

            config=config

        )

        response = extract_text(

            result["messages"][-1]

        )

        sources = result.get(

            "retrieved_docs",

            []

        )

        return {
    "answer": response,
    "sources": sources,
    "context": result.get("context", "")
     }

    except Exception as e:

        logger.exception(e)

        return {

            "answer": str(e),

            "sources": []

        }

def stream_chat(question, thread_id=DEFAULT_THREAD):

    config = {

        "configurable": {

            "thread_id": thread_id

        }

    }

    try:

        for event in graph.stream(

            {

                "messages": [

                    HumanMessage(

                        content=question

                    )

                ]

            },

            config=config

        ):

            yield event

    except Exception as e:

        logger.exception(e)

        yield {

            "error": str(e)

        }

def ask(question):

    result = chat(question)

    return result["answer"]

def upload_pdf(uploaded_file):

    try:

        path = save_uploaded_pdf(

            uploaded_file

        )

        chunks = index_new_pdf(path)

        return True, chunks

    except Exception as e:

        logger.exception(e)

        return False, str(e)

def stream_answer(question, context="", thread_id=DEFAULT_THREAD):

    system_prompt = f"""
You are a helpful AI assistant.

Use the provided context whenever possible.

Context:

{context}
"""

    messages = [

        SystemMessage(content=system_prompt),

        HumanMessage(content=question)

    ]

    for chunk in stream_response(messages):

        if chunk.content:

            yield chunk.content