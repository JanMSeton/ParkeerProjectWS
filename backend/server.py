# CODE met hulp van AJ
#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers

Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import yaml
from PIL import Image
import os
import time

import printer
import receipt

p = printer.create_printer()
logo_path = "./WS-logo-black.bmp"

# Mapping of answers to specific texts
data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "data",
    "answer_text_mapping.yaml"
)

with open(data_path, encoding="utf-8") as f:
    yaml_text = yaml.safe_load(f)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    force=True
    )

RECOVERYTIME = 300

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins
        # self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')  # Allow specific methods
        # self.send_header('Access-Control-Allow-Headers', 'Content-Type')  # Allow specific headers
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        logger.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
           
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length)  # Get the data itself
        logger.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data.decode('utf-8'))
        body = post_data.decode('utf-8')
        data = json.loads(body)

        flow = data.get("flow", "wsf")

        if flow == "festival":
            receipt_template = receipt.create_festival_receipt(
                data,
                festival_yaml
            )
        else:
            receipt_template = receipt.create_receipt(
                data,
                wsf_yaml
            )

        # Print the receipt
        global p
        try:
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
            else:
                logo = None            
                logger.warning(
                f"Logo not found: {logo_path}. Printing receipt without logo."
            )
            
            printer.print_receipt(printer=p, receipt_template=receipt_template, logo=logo)

        except Exception:

            logger.exception(f"Error while printing, recovering...")
            p = printer.recover_printer(printer=p)

            self._set_response()

            if p is None:
                # Both recovery attempts failed, tell the main server loop to stop accepting requests.
                response = {
                    "ok": False,
                    "error": "FATAL",
                    "waittime": RECOVERYTIME,
                }
                logger.error("Printer could not be recovered. Server will stop.")
                self.wfile.write(json.dumps(response).encode("utf-8")) 
                logger.info("Sent response to browser")
                raise Exception
            
            else:
                response = {
                    "ok": False,
                    "error": "Printer connection lost; printer was reset.",
                    "cooldown": RECOVERYTIME
                }
                logger.info(f"Printer has been recovered. Server will recover for {RECOVERYTIME}s and wait for new request.")
                time.sleep(RECOVERYTIME)
                self.wfile.write(json.dumps(response).encode("utf-8")) 
                logger.info("Sent response to browser")
                return

        # Only reached when printing succeeded
        logger.info("Receipt printed successfully.")

        logger.info(f"Waiting {printer.COOLDOWN} seconds before printer is ready again...")
        time.sleep(printer.COOLDOWN)
        logger.info("Printer is ready again.")

        self._set_response()

        response = {
            "ok": True,
            "ready": True,
            "cooldown": printer.COOLDOWN
        }

        self.wfile.write(json.dumps(response).encode("utf-8"))
        logger.info("Sent response to browser")




def run(server_class=HTTPServer, handler_class=S, port=5000):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    logger.info("Starting httpd...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping server...")

    finally:
        httpd.server_close()
        logger.info("HTTP server closed.")

if __name__ == '__main__':
    from sys import argv
    # Parse yaml into json for browser
    base_dir = os.path.dirname(os.path.abspath(__file__))

    data_dir = os.path.join(base_dir, "..", "data")

    frontend_dir = os.path.join(base_dir, "..", "frontend")

    old_yaml_path = os.path.join(
        data_dir,
        "answer_text_mapping.yaml"
    )

    festival_yaml_path = os.path.join(
        data_dir,
        "answer_text_WSF.yaml"
    )

    with open(old_yaml_path, encoding="utf-8") as f:
        wsf_yaml = yaml.safe_load(f)

    with open(festival_yaml_path, encoding="utf-8") as f:
        festival_yaml = yaml.safe_load(f)

    # ---------------------------------------------------------
    # Convert question YAML to JSON for the frontend
    # ---------------------------------------------------------

    questions_yaml_path = os.path.join(
        data_dir,
        "questions_WSF.yaml"
    )

    questions_json_path = os.path.join(
        frontend_dir,
        "questions_WSF.json"
    )

    with open(questions_yaml_path, "r", encoding="utf-8") as yaml_in:
        questions_data = yaml.safe_load(yaml_in)

    with open(questions_json_path, "w", encoding="utf-8") as json_out:
        json.dump(
            questions_data,
            json_out,
            ensure_ascii=False,
            indent=2
        )

    logger.info(
        "Converted %s -> %s",
        questions_yaml_path,
        questions_json_path
    )

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
