from app.services.semantic_search import SemanticSearch


def main():

    search = SemanticSearch()

    questions = [
        "What is a mixture?"
    ]
        

    for question in questions:

        print()
        print("=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)

        results = search.search(
            question,
            limit=5
        )

        for index, result in enumerate(
            results,
            start=1
        ):

            print()
            print("=" * 70)
            print(f"RESULT {index}")
            print("=" * 70)

            print(
                f"Score: {result.score:.4f}"
            )

            print(
                f"Chapter: {result.chapter}"
            )

            print(
                f"Document: {result.document}"
            )

            print(
                f"Page: {result.page}"
            )

            print("\nContent:")

            print(result.text)


if __name__ == "__main__":

    main()