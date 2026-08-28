#!/bin/bash

python3 -u server.py &
PRINTER_PID=$!

npx http-server -p 5503 -c-1 &
HTTP_PID=$!

sleep 5

firefox http://127.0.0.1:5503/ --no-first-run &
FIREFOX_PID=$!

cleanup() {
    echo ""
    echo "Stopping servers..."

    kill "$FIREFOX_PID" "$PRINTER_PID" "$HTTP_PID" 2>/dev/null

    wait "$FIREFOX_PID" "$PRINTER_PID" "$HTTP_PID" 2>/dev/null

    echo "Servers stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

wait