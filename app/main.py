import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    connection, _ = server_socket.accept() # wait for client
    while connection:
        if "PING" in connection.recv(1024).decode():
            connection.send("+PONG\r\n".encode())
    # while True:
    #     data = connection.recv(1024).decode()        
        
    #     if not data:
    #         break
        
    #     if "PING" in data:
    #         connection.send("PONG\r\n".encode())
    #     elif data.strip().startswith("ECHO "):
    #         message = data.strip()[5:]
    #         connection.sendall(f"${len(message)}\r\n{message}\r\n".encode())
    #     else:
    #         connection.sendall(b"-ERR unknown command\r\n")

    # connection.close()

if __name__ == "__main__":
    main()
