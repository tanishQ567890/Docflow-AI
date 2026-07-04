def extract_text(message):

    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text = ""

        for part in content:

            if isinstance(part, dict):

                if part.get("type") == "text":

                    text += part["text"]

        return text

    return str(content)

def format_sources(docs):

    if not docs:

        return ""

    output = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "Unknown"
        )
        if source != "Unknown":
            from pathlib import Path
            source = Path(source).name

        page = doc.metadata.get(
            "page",
            "-"
        )

        output.append(
            f"{source} (Page {page})"
        )

    return "\n".join(

        sorted(

            set(output)

        )

    )