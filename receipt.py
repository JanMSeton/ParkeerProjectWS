import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_receipt(data, yaml_text):
    answer_text_mapping = yaml_text["answer_text_mapping"]
    dynamic_responses = yaml_text["dynamic_responses"]
    receipt_template_header = yaml_text["receipt_template"]["header"]
    receipt_template_footer = yaml_text["receipt_template"]["footer"]

    my_name = data.get('myName', '..........')
    answers = data.get('answers', {})
    # Date for the receipt
    date_today = datetime.now().strftime("%d %B %Y")

    receipt_template = (
    f"""\n\nBon van Betekenis van\n{my_name}\n"""
    f"{date_today}"
    "\n\n")

    receipt_template += receipt_template_header

    for question_id, answer in answers.items():
        dynamic_text = process_dynamic_text(question_id, answer, answer_text_mapping, dynamic_responses)
        # if/elif: only the first statement/answer asked in randomPage1 will be executed
        if question_id == "Q5": #stelling 1
            # Insert the corresponding text for Q5
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        elif question_id == "Q6": #stelling 1
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        elif question_id == "Q7": #stelling 2
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        elif question_id == "Q8": #stelling 3
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        elif question_id == "Q9": #stelling 4
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        elif question_id == "Q10": #stelling 5
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        elif question_id == "Q11": #stelling 6
            receipt_template += f"{dynamic_text}\n" # tekst van "Vraag 5" moet uiteindelijk weg
        # Q12 removed
        elif question_id == "Q13":  # Vraag 1: smileys
            receipt_template += f"""{dynamic_text}\n"""                
        elif question_id == "14":  # Vraag 2: gek
            receipt_template += f"{dynamic_text}\n"                
        elif question_id == "Q15":  # Vraag 3: fronsen
            receipt_template += f"{dynamic_text}\n"                
        else: # HIER ONTSTAAT EEN LOOP als er tekst in staat. Dus alleen logging.
            logger.warning(f"Unexpected question ID: {question_id}. No matching text found.")

    # Append to receipt
    receipt_template += receipt_template_footer

    return receipt_template

# 2x process_dynamic_text combined:
def process_dynamic_text(question_id, answer, answer_text_mapping, dynamic_responses):

    # Check if the question ID exists in the static mapping
    if question_id in answer_text_mapping:
        # Get the specific answer mapping
        specific_mapping = answer_text_mapping[question_id]
        # Return the corresponding text if the answer exists
        return specific_mapping.get(str(answer), f"Onbekend antwoord voor {question_id}.")
    
    elif question_id in dynamic_responses:
        # Handle dynamic responses with placeholders
        default_response = dynamic_responses[question_id].get("default", "")
        return default_response.replace("{answer}", str(answer))
    
    # Fallback if no match is found
    return f"Geen tekst gevonden voor vraag {question_id}."