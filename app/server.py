import socket  # noqa: F401
import threading

def handle_client_connection(connection, address):
    print(f"New connection from {address}")
    while True:
        data = connection.recv(1024).decode()        
        
        if not data:
            break
        print(f"Received from {address}: {data}")
        
        if "PING" in data:
            connection.send("PONG\r\n".encode())
        elif data.strip().startswith("ECHO "):
            message = data.strip()[5:]
            connection.sendall(f"${len(message)}\r\n{message}\r\n".encode())
        else:
            connection.sendall(b"-ERR unknown command\r\n")

    print(f"Connection closed from {address}\n")
    connection.close()
    

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Server is running on localhost:6379")
    
    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    while True:
        connection, address = server_socket.accept() # wait for client
        threading.Thread(target=handle_client_connection, args=(connection, address), daemon=True).start()


if __name__ == "__main__":
    main()
