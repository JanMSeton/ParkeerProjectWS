import logging
import random
from datetime import datetime

import dataUtil

logger = logging.getLogger(__name__)

def create_receipt_WSF(data):
    """
    Receipt generator for the new Festival flow.
    """

    answers = data.get("answers", {})
    my_name = data.get("myName", "..........")
    project_country = data.get("projectCountry", "..........")

    config = dataUtil.parse_answer_YAML("answer_text_WSF")
    template = config["receipt_template"]

    # ---------------------------------------------------------
    # Calculate statement score
    # ---------------------------------------------------------

    statement_questions = config.get("statement_questions", [])

    score = 0

    for question_id in statement_questions:
        answer = answers.get(question_id)

        if answer is None:
            logger.warning(
                "Missing statement answer: %s",
                question_id,
            )
            continue

        try:
            score += int(answer)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid statement answer for %s: %r",
                question_id,
                answer,
            )

    # ---------------------------------------------------------
    # Score feedback
    # ---------------------------------------------------------

    score_feedback = get_festival_score_feedback(
        score,
        config.get("score_feedback", {}),
    )

    # ---------------------------------------------------------
    # Random quote
    # ---------------------------------------------------------

    quotes = config.get("quotes", [])

    quote = random.choice(quotes) if quotes else ""

    # ---------------------------------------------------------
    # Open questions
    # ---------------------------------------------------------

    memory_questions = config.get("memory_questions", {})

    answer_q1 = answers.get(
        memory_questions.get("culture"),
        ""
    )

    answer_q2 = answers.get(
        memory_questions.get("interaction"),
        ""
    )

    answer_q3 = answers.get(
        memory_questions.get("self"),
        ""
    )

    # ---------------------------------------------------------
    # Date/time
    # ---------------------------------------------------------

    date_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )

    # ---------------------------------------------------------
    # Build receipt
    # ---------------------------------------------------------

    values = {
        "myName": my_name,
        "projectCountry": project_country,
        "dateTime": date_time,
        "answerQ1": answer_q1,
        "answerQ2": answer_q2,
        "answerQ3": answer_q3,
        "score": score,
        "scoreFeedback": score_feedback,
        "quote": quote,
    }

    receipt = template["header"].format(**values)

    receipt += "\n"
    receipt += template["footer"].format(**values)

    return receipt


def get_festival_score_feedback(score, feedback_mapping):
    if 3 <= score <= 4:
        return feedback_mapping.get(
            "3-4",
            "",
        )

    if 5 <= score <= 6:
        return feedback_mapping.get(
            "5-6",
            "",
        )

    if 7 <= score <= 9:
        return feedback_mapping.get(
            "7-9",
            "",
        )

    logger.warning(
        "Unexpected Festival score: %s",
        score,
    )

    return ""