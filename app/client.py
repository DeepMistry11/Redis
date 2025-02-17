import socket
import threading
import asyncio


def encode_RESP_command(command):
    """Converts a user command into RESP format."""
    parts = command.split()
    resp_array = f"*{len(parts)}\r\n"
    
    for part in parts:
        resp_array += f"${len(part)}\r\n{part}\r\n" # Convert each to bulk string.
    return resp_array


async def send_ping():
    """Send a command to the server asynchronously."""
    reader, writer = await asyncio.open_connection("localhost", 6379)
    
    while True:
        command = input("> ")
        if command.upper() == "EXIT":
            print("Closing connection.")
            break
        
        resp_command = encode_RESP_command(command) # Convert user input to RESP format
        print(f"Sending: {command}")
        writer.write(resp_command.encode()) # Send message to server
        await writer.drain() # Ensure data is sent
        
        response = await reader.read(1024) # Non-blocking receive
        print(f"Server response: {response.decode().strip()}\n")
    
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