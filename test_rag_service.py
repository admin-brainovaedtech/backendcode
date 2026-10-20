from app.services.rag_service import RAGService


def main():

    rag = RAGService()

    question = "What is uniform motion?"

    result = rag.ask(question)

    print("\nQUESTION")

    print(question)

    print("\nANSWER")

    print(result.answer)

    print("\nSOURCES")

    for source in result.sources:

        print(f"\nPage: {source.page}")

        print(source.content[:200])


if __name__ == "__main__":
    main()