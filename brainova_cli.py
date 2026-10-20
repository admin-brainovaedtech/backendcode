from app.services.rag_service import RAGService


def main():

    print(
    "Hello! I am Brainova, your Class 9 AI tutor."
    )
    print(
        "Ask me questions based on your NCERT study material."
    )

    print("=" * 50)
    print("      BRAINOVA CLASS 9")
    print("=" * 50)

    print("Ask a Science question.")
    print("Type 'exit or quit or close' to stop.\n")

    rag = RAGService()

    while True:

        question = input("You: ")

        if question.lower() in {"new", "clear", "reset"}:
            rag.clear_history()
            print("\nConversation history cleared.")
            
            print(
                "\nBrainova:\n"
                "Conversation cleared. Let's start a new topic."
            )

            print("\n" + "-" * 50 + "\n")

            continue

        if question.lower() in {"exit", "quit", "close"}:
            print("\nThank you for using Brainova.")
            break

        result = rag.ask(question)

        print("\nBrainova:")

        print(result.answer)

        if result.sources:

            print("\nSources:")

            grouped_sources = {}

            # Show only the top 3 retrieved sources
            top_sources = result.sources[:3]

            for source in top_sources:

                key = (
                    source.chapter_number,
                    source.chapter,
                    source.document
                )

                if key not in grouped_sources:
                    grouped_sources[key] = set()

                grouped_sources[key].add(source.page)

            for (
                chapter_number,
                chapter,
                document
            ), pages in grouped_sources.items():

                print(
                    f"Chapter {chapter_number}: {chapter}"
                )

                print(
                    f"Document: {document}"
                )

                sorted_pages = sorted(pages)

                print(
                    "Pages: "
                    + ", ".join(
                        map(str, sorted_pages)
                    )
                )

                print()

        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()