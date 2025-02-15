import socket
import threading

def send_ping():
    """Connects to the server and sends a PING command."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 6379))
    print("Connected to the server. Type commands (PING, ECHO message, or EXIT to quit).")

    
    while True:
        command = input("> ")
        if command.upper() == "EXIT":
            print("Closing connection.")
            break

        client_socket.sendall(f"{command}\r\n".encode()) # Send PING
                
        response = client_socket.recv(1024).decode().strip()
        print(f"Server response: {response}")
    client_socket.close()
    

if __name__ == "__main__":
    send_ping()
    

# client1 = threading.Thread(target = send_ping, args = (1,))
# client2 = threading.Thread(target = send_ping, args = (2,))

# client1.start()
# client2.start()

# client1.join()
# client2.join()