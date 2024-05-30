import socket

HOST = "localhost"
PORT = 4221

OK = "HTTP/1.1 200 OK\r\n"
NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    conn, addr = server_socket.accept() # wait for client
    print("Received connection from", addr[0], "port", addr[1])
    
    # get buffer
    buffer = conn.recv(1024).decode("utf-8")
    print(buffer)
    request = buffer.split("\r\n")
    request_line = request[0].split(" ")
    
    method = request_line[0]
    path = request_line[1]
    version = request_line[2]

    headers = {}
    header = request[1:len(request)-2]
    for h in header:
        hs = h.split(": ")
        headers[hs[0]] = hs[1]

    body = buffer.split("\r\n\r\n")[1]

    if path == "/":
        conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
    elif "echo" in path:
        path_echo = path.split("/")
        echo_text = path_echo[2]
        response = responseBuilder(OK,"text/plain",len(echo_text),echo_text).encode("utf-8")
        conn.send(response)
    else:
        conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
    
    conn.close()

def responseBuilder(statusLine:str , contentType: str, contentLength: int, body: str) -> str:
    return f"{statusLine}Content-Type: {contentType}\r\nContent-Length: {contentLength}\r\n\r\n{body}"

if __name__ == "__main__":
    main()
