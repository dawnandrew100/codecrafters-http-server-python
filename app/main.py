import socket

HOST = "localhost"
PORT = 4221

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    conn, addr = server_socket.accept() # wait for client
    with conn:
        print(f"Connected by {addr}")
        conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
        conn.close()

if __name__ == "__main__":
    main()
