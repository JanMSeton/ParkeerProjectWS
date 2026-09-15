import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)


def create_receipt(data, yaml_text):
    """
    Existing WSF receipt flow.

    This is your current receipt implementation.
    """
    answer_text_mapping = yaml_text["answer_text_mapping"]
    dynamic_responses = yaml_text["dynamic_responses"]
    receipt_template_header = yaml_text["receipt_template"]["header"]
    receipt_template_footer = yaml_text["receipt_template"]["footer"]

    my_name = data.get("myName", "..........")
    answers = data.get("answers", {})

    date_today = datetime.now().strftime("%d %B %Y")

    receipt_template = (
        f"\n\nBon van Betekenis van\n{my_name}\n"
        f"{date_today}\n\n"
    )

    receipt_template += receipt_template_header

    for question_id, answer in answers.items():
        dynamic_text = process_dynamic_text(
            question_id,
            answer,
            answer_text_mapping,
            dynamic_responses,
        )

        # Existing flow
        if question_id in {
            "Q5",
            "Q6",
            "Q7",
            "Q8",
            "Q9",
            "Q10",
            "Q11",
            "Q13",
            "Q14",
            "Q15",
        }:
            receipt_template += f"{dynamic_text}\n"
        else:
            logger.warning(
                "Unexpected question ID for WSF flow: %s",
                question_id,
            )

    receipt_template += receipt_template_footer

    return receipt_template


def create_festival_receipt(data, yaml_text):
    """
    Receipt generator for the new Festival flow.
    """

    answers = data.get("answers", {})
    my_name = data.get("myName", "..........")
    project_country = data.get("projectCountry", "..........")

    config = yaml_text
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


def process_dynamic_text(
    question_id,
    answer,
    answer_text_mapping,
    dynamic_responses,
):
    if question_id in answer_text_mapping:
        specific_mapping = answer_text_mapping[question_id]

        return specific_mapping.get(
            str(answer).lower(),
            f"Onbekend antwoord voor {question_id}.",
        )

    if question_id in dynamic_responses:
        default_response = dynamic_responses[question_id].get(
            "default",
            "",
        )

        return default_response.replace(
            "{answer}",
            str(answer),
        )

    return f"Geen tekst gevonden voor vraag {question_id}."