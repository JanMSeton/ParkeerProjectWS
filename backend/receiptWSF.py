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

    template = dataUtil.parse_answer_YAML("answer_text_WSF.yaml")

    statement_questions = template.get("statement_questions", [])
    score = 0
    for question_id in statement_questions:
        answer = answers.get(question_id)

        if answer is None:
            logger.warning("Missing statement answer: %s", question_id)
            continue
        try:
            score += int(answer)
        except (TypeError, ValueError):
            logger.warning("Invalid statement answer for %s: %r", question_id, answer)

    score_feedback = get_festival_score_feedback(score, template.get("score_feedback", {}))

    quotes = template.get("quotes", [])
    quote = random.choice(quotes) if quotes else ""

    memory_questions = template.get("memory_questions", {})
    answer_q1 = answers.get(memory_questions.get("culture"),"")
    answer_q2 = answers.get(memory_questions.get("interaction"),"")
    answer_q3 = answers.get(memory_questions.get("self"),"")

    date_time = datetime.now().strftime("%d-%m-%Y %H:%M")

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
    receipt = template["receipt_template"].format(**values)

    return receipt


def get_festival_score_feedback(score, feedback_mapping):
    match score:
        case 3 | 4:
            return feedback_mapping.get("3-4", "")
        case 5 | 6:
            return feedback_mapping.get("5-6", "")
        case 7 | 8:
            return feedback_mapping.get("7-9", "")
        case _:
            logger.warning("Unexpected Festival score: %s", score)
            return ""