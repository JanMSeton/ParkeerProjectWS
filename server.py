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
from printer import *
from receipt import *
import os
import time

printer = create_printer()
server_failed = False
logo_path = "./WS-logo-black.bmp"

# Mapping of answers to specific texts
with open("answer_text_mapping.yaml", encoding="utf-8") as f:
    yaml_text = yaml.safe_load(f)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    force=True
    )

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

        receipt_template = create_receipt(data, yaml_text)

        # Print the receipt
        global printer, server_failed
        try:
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
            else:
                logo = None            
                logger.warning(
                f"Logo not found: {logo_path}. Printing receipt without logo."
            )
            print_receipt(printer=printer, receipt_template=receipt_template, logo=logo)

        except Exception:
            logger.exception(f"Error while printing, recovering...")
            printer = recover_printer(printer=printer)

            self._set_response()

            if printer is None:
                # Both recovery attempts failed, tell the main server loop to stop accepting requests.
                server_failed = True
                response = {
                    "ok": False,
                    "error": "Printer could not be recovered. Server is stopping. Printing failed"
                }
                logger.error("Printer could not be recovered. Server will stop.")
            else:
                response = {
                    "ok": False,
                    "error": "Printer connection lost; printer was reset."
                }
                logger.info("Printer has been recovered. Server will wait for new request.")

            time.sleep(300)
            self.wfile.write(json.dumps(response).encode("utf-8")) 
            return

        # Only reached when printing succeeded
        self._set_response()
        response = {"ok": True}
        self.wfile.write(json.dumps(response).encode('utf-8'))



def run(server_class=HTTPServer, handler_class=S, port=5000):
    global server_failed

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    logger.info("Starting httpd...")

    try:
        while not server_failed:
            httpd.handle_request()

    except KeyboardInterrupt:
        logger.info("Stopping server...")

    finally:
        httpd.server_close()
        logger.info("HTTP server closed.")

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
