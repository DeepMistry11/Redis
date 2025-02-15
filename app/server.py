import socket  # noqa: F401
import threading
import asyncio

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
        
        if message == "PING":
            writer.write(b"+PONG\r\n")
        elif message.startswith("ECHO "):
            response = message[5:] # Extract message after "ECHO "
            writer.write(f"{response}\r\n".encode())
        else:
            writer.write(b"-ERR Unknown command\r\n")
            
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


if __name__ == "__main__":
    asyncio.run(main()) # Run the event loop
