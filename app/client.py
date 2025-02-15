import socket
import threading
import asyncio

async def send_ping():
    """Send a command to the server asynchronously."""
    reader, writer = await asyncio.open_connection("localhost", 6379)
    
    while True:
        command = input("> ")
        if command.upper() == "EXIT":
            print("Closing connection.")
            break

        print(f"Sending: {command}")
        writer.write(f"{command}\r\n".encode()) # Send message to server
        await writer.drain() # Ensure data is sent
        
        response = await reader.read(1024) # Non-blocking receive
        print(f"Server response: {response.decode().strip()}")
    
    writer.close()
    await writer.wait_closed() # Close connection
    

# async def main():
#     """Run multiple async commands concurrently."""
#     await asyncio.gather(
#         send_ping("PING"),
#         send_ping("ECHO Hello, Async!")
#     )

if __name__ == "__main__":
    asyncio.run(send_ping()) # Run the event loop