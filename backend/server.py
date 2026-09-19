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
import time

import printer
import receiptVBW
import receiptWSF
import dataUtil

p = printer.create_printer()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    force=True
    )

busy_until = 0  # epoch timestamp; server rejects requests until this passes

RECOVERYTIME = 300

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins
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

        global busy_until
        if time.time() < busy_until:
            remaining = round(busy_until - time.time())
            logger.info(f"Server waiting, rejecting request. {remaining}s left.")
            self._set_response()
            response = {
                "ok": False,
                "error": "Printer is recovering, please try again shortly.",
                "cooldown": remaining,
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        body = post_data.decode('utf-8')
        data = json.loads(body)

        flow = data.get("flow", "wsf")

        if flow == "festival":
            receipt_template = receiptWSF.create_receipt_WSF(data)
        else:
            receipt_template = receiptVBW.create_receipt_VBW(data)

        # Print the receipt
        global p
        try:
            logo = dataUtil.load_logo()
            printer.print_receipt(printer=p, receipt_template=receipt_template, logo=logo)
            busy_until = printer.COOLDOWN + time.time()

        except Exception:

            logger.exception(f"Error while printing, recovering...")
            p = printer.recover_printer(printer=p)

            self._set_response()

            if p is None:
                # Both recovery attempts failed, tell the main server loop to stop accepting requests.
                response = {
                    "ok": False,
                    "error": "FATAL",
                    "cooldown": -1,
                }
                logger.error("Printer could not be recovered. Server will stop.")
                self.wfile.write(json.dumps(response).encode("utf-8")) 
                logger.info("Sent response to browser")
                raise Exception
            
            else:
                response = {
                    "ok": False,
                    "error": "RECOVERING",
                    "cooldown": RECOVERYTIME
                }
                logger.info(f"Printer has been recovered. Server will reject requests for {RECOVERYTIME}s.")
                busy_until = time.time() + RECOVERYTIME
                self.wfile.write(json.dumps(response).encode("utf-8"))
                logger.info("Sent response to browser")
                return

        # Only reached when printing succeeded
        logger.info("Printer is ready again.")

        self._set_response()

        response = {
            "ok": True,
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
    dataUtil.convert_question_yaml_to_json("questions_VBW.yaml", "questions_VBW.json")
    dataUtil.convert_question_yaml_to_json("questions_WSF.yaml", "questions_WSF.json")

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
