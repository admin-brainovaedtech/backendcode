import os
from pathlib import Path
from unittest import result

from dotenv import load_dotenv
from google import genai

from app.services.semantic_search import SemanticSearch
from app.models.schemas import BrainovaResponse, SourceChunk


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

RAG_TOP_K = int(
    os.getenv("RAG_TOP_K", "5")
)

RAG_MIN_SCORE = float(
    os.getenv("RAG_MIN_SCORE", "0.65")
)


class RAGService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.semantic_search = SemanticSearch()

        # --------------------------------------------------
        # Conversation memory
        # --------------------------------------------------

        self.conversation_history = []

        # --------------------------------------------------
        # Structured conversation state
        # --------------------------------------------------

        self.conversation_state = {
            "topic": None,
            "last_concept": None,
            "last_example": None,
            "last_exercise": None,
            "last_interaction_type": None,
            "last_solution": None
        }


    # --------------------------------------------------
    # Determine interaction type
    # --------------------------------------------------

    def _get_interaction_type(self, question):

        question_lower = question.lower().strip()

        # --------------------------------------------
        # Solution request
        # --------------------------------------------

        solution_keywords = [
            "solve it",
            "solve this",
            "solve the",
            "give me the solution",
            "solution for",
            "solution of",
            "answer to the problem"
        ]

        if any(
            keyword in question_lower
            for keyword in solution_keywords
        ):
            return "solution_request"

        # --------------------------------------------
        # Difficulty request
        # --------------------------------------------

        difficulty_keywords = [
            "make it harder",
            "make it easier",
            "make it difficult",
            "make it more difficult",
            "make this harder",
            "make this easier",
            "harder",
            "easier"
        ]

        if any(
            keyword in question_lower
            for keyword in difficulty_keywords
        ):
            return "difficulty_request"

        # --------------------------------------------
        # Explanation request
        # --------------------------------------------

        explanation_keywords = [
            "explain it",
            "explain this",
            "explain again",
            "explain the solution",
            "explain the answer",
            "why is this",
            "why does",
            "why do"
        ]

        if any(
            keyword in question_lower
            for keyword in explanation_keywords
        ):
            return "explanation_request"

        # --------------------------------------------
        # Another request
        # --------------------------------------------

        another_keywords = [
            "another one",
            "give me another",
            "one more",
            "another question",
            "another exercise",
            "another problem"
        ]

        if any(
            keyword in question_lower
            for keyword in another_keywords
        ):
            return "another_request"

        # --------------------------------------------
        # Example request
        # --------------------------------------------

        example_keywords = [
            "give me an example",
            "give an example",
            "show me an example",
            "give me example",
            "example"
        ]

        if any(
            keyword in question_lower
            for keyword in example_keywords
        ):
            return "example_request"

        # --------------------------------------------
        # Exercise generation request
        # --------------------------------------------

        exercise_keywords = [
            "give me an exercise",
            "give an exercise",
            "give me a question",
            "give me a problem",
            "practice question",
            "practice problem",
            "numerical problem",
            "numerical question",
            "numerical"
        ]

        if any(
            keyword in question_lower
            for keyword in exercise_keywords
        ):
            return "generated_exercise"

        # --------------------------------------------
        # Normal question
        # --------------------------------------------

        return "normal"


    # --------------------------------------------------
    # Build conversation history
    # --------------------------------------------------

    def _build_conversation_context(self):

        if not self.conversation_history:
            return "No previous conversation."

        history = []

        for item in self.conversation_history:

            interaction_type = item.get(
                "type",
                "normal"
            )

            topic = item.get(
                "topic",
                "Not specified"
            )

            history.append(
                f"Interaction Type: {interaction_type}\n"
                f"Topic: {topic}\n"
                f"Student: {item['question']}\n"
                f"Brainova: {item['answer']}"
            )

        return "\n\n".join(history)


    # --------------------------------------------------
    # Get relevant previous interaction
    #
    # Structured state is checked first.
    # Conversation history is used as fallback.
    # --------------------------------------------------

    def _get_relevant_previous_interaction(
        self,
        interaction_type
    ):

        # --------------------------------------------
        # Solve the latest exercise
        # --------------------------------------------

        if interaction_type == "solution_request":

            last_exercise = (
                self.conversation_state.get(
                    "last_exercise"
                )
            )

            if last_exercise:
                return last_exercise

            for item in reversed(
                self.conversation_history
            ):

                if item.get("type") in [
                    "generated_exercise",
                    "difficulty_request"
                ]:
                    return item

            return None

        # --------------------------------------------
        # Make exercise harder/easier
        # --------------------------------------------

        if interaction_type == "difficulty_request":

            last_exercise = (
                self.conversation_state.get(
                    "last_exercise"
                )
            )

            if last_exercise:
                return last_exercise

            if self.conversation_history:
                return self.conversation_history[-1]

            return None

        # --------------------------------------------
        # Generate exercise from current concept
        # --------------------------------------------

        if interaction_type == "generated_exercise":

            last_concept = (
                self.conversation_state.get(
                    "last_concept"
                )
            )

            if last_concept:
                return last_concept

            if self.conversation_history:
                return self.conversation_history[-1]

            return None

        # --------------------------------------------
        # Generate example from current concept
        # --------------------------------------------

        if interaction_type == "example_request":

            last_concept = (
                self.conversation_state.get(
                    "last_concept"
                )
            )

            if last_concept:
                return last_concept

            if self.conversation_history:
                return self.conversation_history[-1]

            return None

        # --------------------------------------------
        # Explain previous concept
        # --------------------------------------------

        if interaction_type == "explanation_request":

            last_interaction_type = (
                self.conversation_state.get(
                    "last_interaction_type"
                )
            )

            if last_interaction_type == "solution_request":

                last_solution = (
                    self.conversation_state.get(
                        "last_solution"
                    )
                )

                if last_solution:
                    return last_solution

            if last_interaction_type == "example_request":

                last_example = (
                    self.conversation_state.get(
                        "last_example"
                    )
                )

                if last_example:
                    return last_example

            if last_interaction_type in [
                "generated_exercise",
                "difficulty_request"
            ]:

                last_exercise = (
                    self.conversation_state.get(
                        "last_exercise"
                    )
                )

                if last_exercise:
                    return last_exercise

            last_concept = (
                self.conversation_state.get(
                    "last_concept"
                )
            )

            if last_concept:
                return last_concept

            return None

        # --------------------------------------------
        # Another one
        # --------------------------------------------

        if interaction_type == "another_request":

            last_interaction_type = (
                self.conversation_state.get(
                    "last_interaction_type"
                )
            )

            # --------------------------------------------
            # Previous response was an exercise
            # --------------------------------------------

            if last_interaction_type in [
                "generated_exercise",
                "difficulty_request"
            ]:

                last_exercise = (
                    self.conversation_state.get(
                        "last_exercise"
                    )
                )

                if last_exercise:
                    return last_exercise

            # --------------------------------------------
            # Previous response was an example
            # --------------------------------------------

            if last_interaction_type == "example_request":

                last_example = (
                    self.conversation_state.get(
                        "last_example"
                    )
                )

                if last_example:
                    return last_example

            # --------------------------------------------
            # Fallback to current concept
            # --------------------------------------------

            last_concept = (
                self.conversation_state.get(
                    "last_concept"
                )
            )

            if last_concept:
                return last_concept

            if self.conversation_history:
                return self.conversation_history[-1]

            return None

        return None


    # --------------------------------------------------
    # Build relevant interaction context
    # --------------------------------------------------

    def _build_relevant_interaction_context(
        self,
        previous_interaction
    ):

        if not previous_interaction:

            return (
                "No specific previous interaction "
                "is available."
            )

        interaction_type = previous_interaction.get(
            "type",
            "normal"
        )

        topic = previous_interaction.get(
            "topic",
            self.conversation_state.get("topic")
        )

        return (
            f"Topic: {topic}\n"
            f"Student: "
            f"{previous_interaction.get('question', '')}\n"
            f"Brainova: "
            f"{previous_interaction.get('answer', '')}\n"
            f"Previous Interaction Type: "
            f"{interaction_type}"
        )


    def _normalize_query(self, question):

        prompt = f"""
Normalize the student's science question for semantic search.

Correct only obvious spelling mistakes or speech-to-text errors.

Rules:
1. Preserve the student's intended meaning.
2. Do not answer the question.
3. Do not add explanations.
4. Do not introduce new scientific concepts.
5. Do not replace a scientific term merely because another
   term is more common.
6. If the wording is already correct, return it unchanged.
7. If you are not confident that a word is misspelled,
   leave it unchanged.
8. Preserve important scientific terminology.
9. Return ONLY the corrected search query.
10. Do not put the query in quotes.
11. Do not add labels such as "Corrected:" or "Query:".

Examples:

Student:
where is epical tissue present

Return:
where is apical tissue present

Student:
what is velocity

Return:
what is velocity

Student:
what is a cell

Return:
what is a cell

Student:
what is epithelial tissue

Return:
what is epithelial tissue

STUDENT QUESTION
================
{question}
================
"""

        try:

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            normalized = (
                response.text.strip()
                if response.text
                else ""
            )

            if not normalized:
                return question.strip()

            # Guard against the model returning a prompt-style label.
            prefixes = [
                "corrected:",
                "corrected query:",
                "query:"
            ]

            normalized_lower = normalized.lower()

            for prefix in prefixes:

                if normalized_lower.startswith(prefix):

                    normalized = normalized[
                        len(prefix):
                    ].strip()

                    break

            return normalized or question.strip()

        except Exception:

            # Query normalization is an enhancement only.
            # Retrieval should continue with the original question
            # if normalization fails.
            return question.strip()


    # --------------------------------------------------
    # Rewrite question for context-aware retrieval
    # --------------------------------------------------

    def _rewrite_question(self, question):

        if not self.conversation_history:
            return question

        conversation_context = (
            self._build_conversation_context()
        )

        prompt = f"""
Rewrite the student's latest question as a complete,
standalone search query.

Use the conversation history only when the latest
question depends on previous context.

If it depends on previous context, resolve that context
in the rewritten question.

Examples:

Previous topic: velocity
Student: Give me an example.
Rewritten: Give me an example of velocity.

Previous topic: velocity and acceleration
Student: Give me an exercise.
Rewritten: Give me an exercise on velocity and
acceleration.

If the student's latest question is complete and
independent, return it unchanged.

Do not answer the question.
Do not explain the question.
Do not add information.
Do not greet the student.

Return ONLY the rewritten standalone search query.

CONVERSATION HISTORY
====================
{conversation_context}
====================

LATEST STUDENT QUESTION
====================
{question}
====================
"""

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        return response.text.strip()


    # --------------------------------------------------
    # Clear conversation history and state
    # --------------------------------------------------

    def clear_history(self):

        self.conversation_history = []

        self.conversation_state = {
            "topic": None,
            "last_concept": None,
            "last_example": None,
            "last_exercise": None,
            "last_interaction_type": None,
            "last_solution": None
        }


    # --------------------------------------------------
    # Update structured conversation state
    # --------------------------------------------------

    def _update_conversation_state(
        self,
        question,
        answer,
        interaction_type,
        topic
    ):

        # --------------------------------------------
        # Normal concept/question
        # --------------------------------------------

        if interaction_type == "normal":

            self.conversation_state["topic"] = topic

            self.conversation_state["last_concept"] = {
                "question": question,
                "answer": answer,
                "type": "normal",
                "topic": topic
            }

        # --------------------------------------------
        # Example
        # --------------------------------------------

        elif interaction_type == "example_request":

            self.conversation_state["last_example"] = {
                "question": question,
                "answer": answer,
                "type": "example_request",
                "topic": (
                    self.conversation_state["topic"]
                    or topic
                )
            }

        # --------------------------------------------
        # Generated exercise
        # --------------------------------------------

        elif interaction_type == "generated_exercise":

            self.conversation_state["last_exercise"] = {
                "question": question,
                "answer": answer,
                "type": "generated_exercise",
                "topic": (
                    self.conversation_state["topic"]
                    or topic
                )
            }

        # --------------------------------------------
        # Harder/easier exercise
        # --------------------------------------------

        elif interaction_type == "difficulty_request":

            self.conversation_state["last_exercise"] = {
                "question": question,
                "answer": answer,
                "type": "difficulty_request",
                "topic": (
                    self.conversation_state["topic"]
                    or topic
                )
            }

        # --------------------------------------------
        # Solution
        # --------------------------------------------

        elif interaction_type == "solution_request":

            self.conversation_state["last_solution"] = {
                "question": question,
                "answer": answer,
                "type": "solution_request",
                "topic": (
                    self.conversation_state["topic"]
                    or topic
                )
            }

        self.conversation_state["last_interaction_type"] = (
            interaction_type
        )
    # --------------------------------------------------
    # Safe retrieval with concept validation
    #
    # Strong semantic matches are trusted. Validation is
    # used only for ambiguous/weak retrieval so that a
    # valid semantic match is not incorrectly rejected.
    # --------------------------------------------------

    def _validate_retrieval_concept(
        self,
        question,
        normalized_question,
        retrieved_results
    ):

        if not retrieved_results:
            return False

        candidates = []

        for result in retrieved_results[:5]:
            if result.score > 0:
                score_info = f"Vector score: {result.score:.4f}"
            else:
                score_info = "Match type: keyword fallback"

            candidates.append(
                f"Chapter: {result.chapter}\n"
                f"Page: {result.page}\n"
                f"{score_info}\n"
                f"Content: {result.text}"
            )

        candidate_context = "\n\n".join(candidates)

        prompt = f"""
Determine whether the retrieved Class 9 Science content is
relevant to the student's question.

This is a retrieval relevance check, not an answer-generation task.

Rules:
1. Return MATCH when the retrieved material directly answers
   the question or clearly contains the scientific concept
   needed to answer it.
2. Semantic meaning is more important than exact wording.
3. Do not require the same words to appear in the question
   and retrieved material.
4. Related NCERT terminology is acceptable.
5. Do not reject a result merely because the retrieved text
   uses a different but scientifically equivalent description.
6. Return MISMATCH only when the retrieved material is clearly
   about a different scientific concept.
7. Pay special attention to confusing concepts such as:
   apical meristem vs epithelial tissue.
8. Return ONLY:
   MATCH
   or
   MISMATCH

Student question:
{question}

Normalized question:
{normalized_question}

Retrieved NCERT material:
{candidate_context}
"""

        try:

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            result = response.text.strip().upper()

            if result.startswith("MISMATCH"):
                return False

            if result.startswith("MATCH"):
                return True

            # Ambiguous validator output should not block
            # otherwise useful retrieved material.
            return True

        except Exception:

            # Validation is a secondary safeguard. Retrieval
            # should continue if validation itself fails.
            return True


    def _retrieve_with_concept_validation(
        self,
        question,
        normalized_question,
        search_query
    ):

        results = self.semantic_search.search(
            search_query,
            limit=RAG_TOP_K
        )

       

        filtered_results = [
            result
            for result in results
            if result.score >= RAG_MIN_SCORE
        ]

        if not filtered_results:
            return []

        # --------------------------------------------------
        # Strong retrieval should not be blocked by the
        # concept validator.
        #
        # A score substantially above the configured minimum
        # indicates a strong semantic match.
        # --------------------------------------------------

        strong_score_threshold = max(
            RAG_MIN_SCORE + 0.08,
            0.72
        )

        strongest_score = max(
            result.score
            for result in filtered_results
        )

        if strongest_score >= strong_score_threshold:
            return filtered_results

        # --------------------------------------------------
        # Ambiguous retrieval: validate the concept.
        # --------------------------------------------------

        is_match = self._validate_retrieval_concept(
            question=question,
            normalized_question=normalized_question,
            retrieved_results=filtered_results
        )

        if is_match:
            return filtered_results

        # --------------------------------------------------
        # Retry using the original student question.
        #
        # This prevents an imperfect normalization/rewrite
        # from permanently steering retrieval to the wrong
        # concept.
        # --------------------------------------------------

        if normalized_question != question:

            retry_results = self.semantic_search.search(
                question,
                limit=RAG_TOP_K
            )

            retry_filtered_results = [
                result
                for result in retry_results
                if result.score >= RAG_MIN_SCORE
            ]

            if retry_filtered_results:

                retry_strongest_score = max(
                    result.score
                    for result in retry_filtered_results
                )

                if retry_strongest_score >= strong_score_threshold:
                    return retry_filtered_results

                retry_is_match = (
                    self._validate_retrieval_concept(
                        question=question,
                        normalized_question=normalized_question,
                        retrieved_results=retry_filtered_results
                    )
                )

                if retry_is_match:
                    return retry_filtered_results

        # --------------------------------------------------
        # Final retry using the normalized question directly.
        # This handles cases where _rewrite_question() changed
        # the intent too aggressively.
        # --------------------------------------------------

        if normalized_question != search_query:

            retry_results = self.semantic_search.search(
                normalized_question,
                limit=RAG_TOP_K
            )

            retry_filtered_results = [
                result
                for result in retry_results
                if result.score >= RAG_MIN_SCORE
            ]

            if retry_filtered_results:

                retry_strongest_score = max(
                    result.score
                    for result in retry_filtered_results
                )

                if retry_strongest_score >= strong_score_threshold:
                    return retry_filtered_results

                retry_is_match = (
                    self._validate_retrieval_concept(
                        question=question,
                        normalized_question=normalized_question,
                        retrieved_results=retry_filtered_results
                    )
                )

                if retry_is_match:
                    return retry_filtered_results

          # --------------------------------------------------
        # Final keyword fallback for weak vector retrieval.
        # Candidate chunks must still pass concept validation.
        # --------------------------------------------------

        keyword_results = (
            self.semantic_search.search_keyword_fallback(
                question,
                limit=RAG_TOP_K
            )
        )

        if keyword_results:
            keyword_is_match = self._validate_retrieval_concept(
                question=question,
                normalized_question=normalized_question,
                retrieved_results=keyword_results
            )

            if keyword_is_match:
                return keyword_results

        return []



    # --------------------------------------------------
    # Main RAG process
    # --------------------------------------------------

    def ask(self, question):

        # --------------------------------------------
        # 1. Determine interaction type
        # --------------------------------------------

        interaction_type = (
            self._get_interaction_type(question)
        )

        normalized_question = (
            self._normalize_query(question)
        )
        # --------------------------------------------
        # 2. Get relevant previous interaction
        # --------------------------------------------

        previous_interaction = (
            self._get_relevant_previous_interaction(
                interaction_type
            )
        )

        # --------------------------------------------
        # 3. Build effective search query
        # --------------------------------------------

        context_dependent_types = [
            "solution_request",
            "difficulty_request",
            "another_request",
            "example_request",
            "explanation_request",
            "generated_exercise"
        ]

        if (
            interaction_type
            in context_dependent_types
            and previous_interaction
        ):

            search_query = (
                previous_interaction.get(
                    "topic"
                )
                or previous_interaction.get(
                    "question"
                )
            )

        else:

            search_query = self._rewrite_question(
                normalized_question
            )

        # --------------------------------------------
        # 4. Retrieve relevant NCERT content.
        #
        # Strong semantic matches are accepted directly.
        # Ambiguous matches go through concept validation
        # and retry logic.
        # --------------------------------------------

        retrieved = self._retrieve_with_concept_validation(
            question=question,
            normalized_question=normalized_question,
            search_query=search_query
        )

        if not retrieved:

            return BrainovaResponse(
                answer=(
                    "I could not confidently match this "
                    "question to the provided Class 9 Science "
                    "study material."
                ),
                sources=[]
            )

        # --------------------------------------------
        # 5. Build NCERT context
        # --------------------------------------------

        context_parts = []

        for result in retrieved:

            context_parts.append(
                f"Source: {result.document}\n"
                f"Chapter: {result.chapter}\n"
                f"Page: {result.page}\n"
                f"Content:\n{result.text}"
            )

        context = "\n\n".join(
            context_parts
        )

        # --------------------------------------------
        # 7. Build conversation context
        # --------------------------------------------

        conversation_context = (
            self._build_conversation_context()
        )

        # --------------------------------------------
        # 8. Build previous interaction context
        # --------------------------------------------

        relevant_interaction_context = (
            self._build_relevant_interaction_context(
                previous_interaction
            )
        )

        # --------------------------------------------
        # 9. Generate grounded answer
        # --------------------------------------------

        prompt = f"""
You are the answer engine for Brainova,
a CBSE Class 9 AI tutor.

The student's current interaction type is:

{interaction_type}

Use the relevant previous interaction only to
understand follow-up requests.

Use the NCERT study material as the source of
factual information.

IMPORTANT INTERACTION RULES:

1. If the interaction type is "example_request",
   give an example related to the previous concept.

2. If the interaction type is "generated_exercise",
   create a practice exercise based on the previous
   concept and supported NCERT material.

3. If the interaction type is "solution_request",
   solve the exact previous exercise provided in the
   relevant previous interaction.

4. If the interaction type is "difficulty_request",
   create a more difficult exercise based on the
   previous exercise or topic.

5. If the interaction type is "another_request",
   create another relevant example or exercise based
   on the previous interaction.

6. If the interaction type is "explanation_request",
   explain the relevant previous concept more clearly.

STRICT RULES:

1. Start directly with the answer.

2. Do NOT greet the student.

3. Do NOT introduce yourself.

4. Do NOT repeat the student's question.

5. Explain in simple language suitable for Class 9.

6. For simple definition questions, give the direct
   definition first.

7. Keep the answer concise unless more explanation,
   examples or calculations are requested.

8. Use information explicitly stated or clearly
   supported by the NCERT study material.

9. You may combine information from multiple
   retrieved passages.

10. Do NOT introduce new factual claims that are not
    supported by the NCERT study material.

11. For definition questions, construct a concise
    definition from relevant descriptions,
    classifications, properties and examples.

12. Use simple plain text for mathematical formulas
    and calculations.

13. Do NOT use LaTeX formatting.

14. Write fractions using /.

15. Write units in plain text.
    Examples:
    m/s
    m/s²
    km/h
    m²

16. For numerical problems, show calculations
    step by step.

17. Preserve exact scientific notation when it is explicitly
    provided or clearly supported by the NCERT study material.

18. For scientific facts, do not change or simplify:
    - isotope notation
    - chemical symbols
    - atomic numbers
    - mass numbers
    - chemical formulae
    - numerical values
    - units
    - equations

19. For isotope notation, use standard nuclear notation with:
    - mass number as superscript
    - atomic number as subscript
    - element symbol on the right

20. Use Unicode superscript and subscript characters.

21. Examples of correct isotope notation:
    ¹₁H
    ²₁H or D
    ³₁H
    ¹²₆C
    ¹³₆C
    ¹⁴₆C

22. Do NOT use slash notation such as:
    1/1 H
    2/1 H
    3/1 H
    12/6 C
    13/6 C
    14/6 C

23. Do NOT replace exact NCERT scientific notation with
    approximate, simplified, or alternative notation.

24. When explaining isotopes, preserve the relationship between
    protons, neutrons, and electrons exactly as supported by the
    NCERT material.

25. Preserve stated scientific applications exactly.
    Do not assign an application to a scientific concept or isotope
    unless that application is supported by the NCERT study material.

26. Return ONLY the answer.

CURRENT STRUCTURED TOPIC
====================
{self.conversation_state["topic"]}
====================

RELEVANT PREVIOUS INTERACTION
====================
{relevant_interaction_context}
====================

CONVERSATION HISTORY
====================
{conversation_context}
====================

NCERT STUDY MATERIAL
====================
{context}
====================

STUDENT QUESTION
====================
{question}
====================
"""

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        answer = response.text.strip()

        # --------------------------------------------
        # 10. Update structured state
        # --------------------------------------------

        self._update_conversation_state(
            question=question,
            answer=answer,
            interaction_type=interaction_type,
            topic=search_query
        )

        # --------------------------------------------
        # 11. Save conversation memory
        # --------------------------------------------

        self.conversation_history.append(
            {
                "question": question,
                "answer": answer,
                "type": interaction_type,
                "topic": (
                    self.conversation_state["topic"]
                    or search_query
                )
            }
        )

        # Keep only last 5 exchanges

        self.conversation_history = (
            self.conversation_history[-5:]
        )

        # --------------------------------------------
        # 12. Build source information
        # --------------------------------------------

        sources = []

        for result in retrieved:

            sources.append(
                SourceChunk(
                    chapter_number=result.chapter_number,
                    chapter=result.chapter,
                    document=result.document,
                    page=result.page,
                    content=result.text
                )
            )

        # --------------------------------------------
        # 13. Return final response
        # --------------------------------------------

        return BrainovaResponse(
            answer=answer,
            sources=sources
        )