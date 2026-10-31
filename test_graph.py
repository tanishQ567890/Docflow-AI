def main():
    from graph import graph
    from langchain_core.messages import HumanMessage
    from utils import extract_text

    config = {"configurable": {"thread_id": "cli"}}

    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            break

        if question.lower() == "exit":
            break
        if not question:
            continue

        result = graph.invoke(
            {"messages": [HumanMessage(content=question)]},
            config=config,
        )

        ai_content = extract_text(result["messages"][-1])
        print(f"\nGemini: {ai_content}\n")


if __name__ == "__main__":
    main()