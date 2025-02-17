import socket  # noqa: F401
import threading
import asyncio


def process_RESP_commands(data):
    """Process RESP command, and send RESP response."""
    lines = data.split("\r\n") # lines = ["*3", "$3", "SET", "$3", "key", "$5", "value"]
    
    if lines[0].startswith("*"): # RESP Array (e.g., *3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n)
        num_elements = int(lines[0][1:])
        command = lines[2].upper() # Extract command (e.g., SET)
        
        if command == "PING":
            return "+PONG\r\n"
        elif command == "ECHO":
            return f"${len(lines[4])}\r\n{data[5:]}\r\n" # bulk string response
        elif command == "SET":
            key = lines[4]
            value = lines[6]
            RESP_STORAGE[key] = value # Store in memory.
            return "+OK\r\n"
        elif command == "GET":
            key = lines[4]
            value = RESP_STORAGE.get(key, None) 
            return f"${len(value)}\r\n{value}\r\n" if value else "$-1\r\n"
        else:
            return "-ERR unknown command\r\n"
    elif data.upper() == "PING":
        return "+PING\r\n"
    elif data.upper().startswith("ECHO "):
        message = data[5:]
        return f"${len(message)}\r\n{message}\r\n"
    else:
        return "-ERR unknown command\r\n"
        

async def handle_client_connection(reader, writer):
    """Handles a single client connection asynchronously."""
    addr = writer.get_extra_info('peername')
    print(f"New connection from: {addr}")
    
    while True:
        data = await reader.read(1024) # Non-blocking read
        if not data:
            break
        
        message = data.decode().strip()
        print(f"Received from {addr}: {message}")

        response = process_RESP_commands(message)
        writer.write(response.encode())
            
        await writer.drain()
        
    print(f"Connection closed from {addr}")
    writer.close()
    await writer.wait_closed()
    

async def main():
    """Start an asynchronous server."""
    server = await asyncio.start_server(handle_client_connection, "localhost", 6379)
    
    addr = server.sockets[0].getsockname()
    print(f"Server is running on {addr}")
    
    async with server:
        await server.serve_forever() # Keep the server running
        
# In-memory storage for SET/GET commands
RESP_STORAGE = {}

if __name__ == "__main__":
    asyncio.run(main()) # Run the event loop
