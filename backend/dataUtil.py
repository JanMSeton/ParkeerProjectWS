import os
import yaml
import json
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# dir constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
LOGO_PATH = "./WS-logo-black.bmp"

def parse_answer_YAML(filename):
    YAML_data_path = os.path.join(
        DATA_DIR,
        filename
    )

    with open(YAML_data_path, encoding="utf-8") as f:
        answerObject = yaml.safe_load(f)

    return answerObject

def load_logo():
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH)
    else:
        logo = None            
        logger.warning(
        f"Logo not found: {LOGO_PATH}. Printing receipt without logo."
        )
    return logo

def convert_question_yaml_to_json(yaml_filename, json_filename):
    yaml_path = os.path.join(
        DATA_DIR,
        yaml_filename
    )

    json_path = os.path.join(
        FRONTEND_DIR,
        json_filename
    )
    with open(yaml_path, "r", encoding="utf-8") as yaml_in:
        questions_data = yaml.safe_load(yaml_in)

    with open(json_path, "w", encoding="utf-8") as json_out:
        json.dump(
            questions_data,
            json_out,
            ensure_ascii=False,
            indent=2
        )

    logger.info(
        "Converted %s -> %s",
        yaml_path,
        json_path
    )