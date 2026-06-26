from graph import graph
from utils import extract_text

from langchain_core.messages import HumanMessage

config = {

    "configurable":{

        "thread_id":"1"

    }

}

while True:

    question = input("You : ")

    if question=="exit":

        break

    result = graph.invoke(

        {

            "messages":[

                HumanMessage(

                    content=question

                )

            ]

        },

        config=config

    )

    print()

    ai_content = extract_text(result["messages"][-1])

    print("Gemini:", ai_content)

    print()