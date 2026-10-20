import json
import os

from google import genai


MODEL_NAME = "gemini-3.7-flash"


def load_chunks():

    file_path = "data/motion_chunks.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def find_relevant_chunks(chunks, keyword):

    keyword = keyword.lower()

    relevant = []

    for chunk in chunks:

        content = chunk["content"].lower()

        if keyword in content:
            relevant.append(chunk)

    return relevant


def ask_gemini(question, chunks):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(api_key=api_key)

    context = "\n\n".join(
        [
            f"Page {chunk['page']}:\n{chunk['content']}"
            for chunk in chunks
        ]
    )

    prompt = f"""
You are Brainova, an AI tutor for Class 9 CBSE students.

Answer the student's question using ONLY the provided
NCERT context.

If the answer cannot be found in the context, say:
"I could not find this information in the provided study material."

Explain the answer in simple language suitable for a Class 9 student.

Study material:
----------------
{context}
----------------

Student question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


def main():

    chunks = load_chunks()

    print(f"Total chunks loaded: {len(chunks)}")

    question = "What is uniform motion?"

    relevant_chunks = find_relevant_chunks(
        chunks,
        "uniform motion"
    )

    print(
        f"Relevant chunks found: {len(relevant_chunks)}"
    )

    if not relevant_chunks:

        print("No relevant chunks found.")

        return

    answer = ask_gemini(
        question,
        relevant_chunks[:5]
    )

    print("\n==============================")
    print("BRAINOVA ANSWER")
    print("==============================")

    print(answer)


if __name__ == "__main__":
    main()