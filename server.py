# -*- coding: utf-8 -*-
import socket
import threading
import os
import mimetypes
from datetime import datetime

HOST = '127.0.0.1'
PORT = 8080
WWW_ROOT = './www'
LOG = './log.txt'

def log(method, path, status):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{now}] {method} {path} => {status}"
    print(log_entry)
    with open(LOG, 'a') as logfile:
        logfile.write(log_entry + '\n')

def serve_file(client, path):
    if path == '/':
        path = '/index.html'
    filepath = os.path.realpath(WWW_ROOT + path)

    if not filepath.startswith(os.path.realpath(WWW_ROOT)):
        response = "HTTP/1.1 403 Forbidden\r\n\r\n403 - Accesso negato"
        client.sendall(response.encode())
        log("GET", path, 403)
        return

    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            content = f.read()
        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'
        header = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(content)}\r\n\r\n"
        client.sendall(header.encode() + content)
        log("GET", path, 200)
    else:
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 - File non trovato</h1>"
        client.sendall(response.encode())
        log("GET", path, 404)

def handle_client(client, addr):
    try:
        request = client.recv(1024).decode('utf-8')
        if not request:
            return
        line = request.splitlines()[0]
        parts = line.split()
        if len(parts) < 2 or parts[0] != 'GET':
            client.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\nMetodo non supportato")
            log("UNKNOWN", "-", 405)
            return
        method, path = parts[0], parts[1]
        serve_file(client, path)
    finally:
        client.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(10)
        print(f"Server attivo su http://{HOST}:{PORT}")
        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    start_server()
