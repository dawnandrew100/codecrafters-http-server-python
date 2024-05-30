import socket
import threading
import sys

HOST = "localhost"
PORT = 4221

OK = "HTTP/1.1 200 OK\r\n"
NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"
BAD_REQUEST = "HTTP/1.1 400 Bad Request\r\n\r\n"
CREATED     = "HTTP/1.1 201 Created\r\n"

ACCEPTED_ENCODINGS = ["gzip"]

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    print("Waiting for connection")
    while True:
        connection, addr = server_socket.accept() # wait for client
        print("Received connection from", addr[0], "port", addr[1])
        t = threading.Thread(target=lambda: requestHandler(connection))
        t.start()

def parseRequest(buf):
    request = buf.split("\r\n")
    request_line = request[0].split(" ")
    

    headers = {}
    header = request[1:len(request)-2]
    for h in header:
        hs = h.split(": ")
        headers[hs[0]] = hs[1]

    body = buf.split("\r\n\r\n")[1]
    
    Request = {
            "method": request_line[0],
            "path": request_line[1],
            "version": request_line[2],
            "headers":headers,
            "body": body
            }
    return Request

def requestHandler(conn):
    # get buffer
    buffer = conn.recv(1024).decode("utf-8")
    print(buffer)
    
    req = parseRequest(buffer)
    method = req["method"]
    path = req["path"]
    headers = req["headers"]
    body = req["body"]
    

    response = f"{NOT_FOUND}\r\n".encode("utf-8")

    if path == "/":
        response = f"{OK}\r\n".encode("utf-8")
    elif path.startswith("/echo"):
        path_echo = path.split("/")
        echo_text = path_echo[2]
        if "Accept-Encoding" in headers and headers["Accept-Encoding"] in ACCEPTED_ENCODINGS:
            response = compressedResponseBuilder(OK, headers["Accept-Encoding"], "text/plain", len(echo_text), echo_text).encode("utf-8")
        else:
            response = responseBuilder(OK, "text/plain", len(echo_text), echo_text).encode("utf-8")
    elif path.startswith("/user-agent"):
        response = responseBuilder(OK, "text/plain", len(headers["User-Agent"]), headers["User-Agent"]).encode("utf-8")
    elif path.startswith("/files/"):
        directory = sys.argv[2]
        filename = path.split("/")[2]
        file_path = f"{directory}/{filename}"
        if method == "GET":
            try:
                with open(file_path, "r") as file:
                    file_contents = file.read()
                response = responseBuilder(OK, "application/octet-stream", len(file_contents), file_contents).encode("utf-8")
            except Exception as e:
                print(f"Error: Reading/{file_path} failed. Exception: {e}")
        elif method == "POST":
            try:
                with open(file_path, "wb") as file:
                    file.write(body.encode("utf-8"))
                response = responseBuilder(CREATED, "application/octet-stream", len(body), body).encode("utf-8")
            except Exception as e:
                print(f"Error: Reading/{file_path} failed. Exception: {e}")

    
    conn.send(response)
    conn.close() 

def responseBuilder(statusLine: str, contentType: str, contentLength: int, body: str) -> str:
    return f"{statusLine}Content-Type: {contentType}\r\nContent-Length: {contentLength}\r\n\r\n{body}"

def compressedResponseBuilder(statusLine: str, encoding: str, contentType: str, contentLength: int, body: str) -> str:
    return f"{statusLine}Content-Encoding: {encoding}\r\nContent-Type: {contentType}\r\nContent-Length: {contentLength}\r\n\r\n{body}"

if __name__ == "__main__":
    main()
