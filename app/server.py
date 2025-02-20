import socket  # noqa: F401
import threading
import asyncio
import time
import argparse


async def expire_key(key, ttl):
    """Deletes a key after TTL expires."""
    await asyncio.sleep(ttl)
    if key in RESP_STORAGE:
        print(f"Key: {key} expired!")
        del RESP_STORAGE[key]
        del EXPIRATION_TIMES[key]


def process_RESP_commands(data):
    """Process RESP command, and send RESP response."""
    lines = data.split("\r\n") # lines = ["*3", "$3", "SET", "$3", "key", "$5", "value", "$2", "EX", "$4", "time"]
    
    if lines[0].startswith("*"): # RESP Array (e.g., *3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n$2EX\r\n$4time)
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
            if len(lines) > 7:
                additional_set_command = lines[8]
                ttl = int(lines[10])
                if additional_set_command == "EX":
                    EXPIRATION_TIMES[key] = time.time() + ttl
                    # Right after we call this function, it waits for TTL 
                    # seconds without blocking and the executes rest of the 
                    # expire_key function and deletes the key.
                    asyncio.create_task(expire_key(key, ttl)) 
                elif additional_set_command == "PX": # Set TTL in milliseconds.
                    EXPIRATION_TIMES[key] = (time.time() / 1000) + ttl
                    asyncio.create_task(expire_key(key, ttl))
            return "+OK\r\n"
        elif command == "GET":
            key = lines[4]
            
            if key in EXPIRATION_TIMES and EXPIRATION_TIMES[key] < time.time():
                del RESP_STORAGE[key]
                del EXPIRATION_TIMES[key]
                return "$-1\r\n"
            
            value = RESP_STORAGE.get(key, None) 
            
            return f"${len(value)}\r\n{value}\r\n" if value else "$-1\r\n"
        elif command == "CONFIG" and num_elements == 3 and lines[4].upper() == "GET":
            config_key = lines[6]

            if config_key in SERVER_CONFIG:
                value = SERVER_CONFIG[config_key]
                return f"*2\r\n${len(config_key)}\r\n{config_key}\r\n${len(value)}\r\n{value}\r\n"

            return "*0\r\n" 
            
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
    
    
def parse_args(args):
    global SERVER_CONFIG
    
    args_dict = vars(args)
    
    i = 0
    for key, value in args_dict.items():
        if value is not None:
            SERVER_CONFIG[key] = value
        # if args[key] == "--dir" and i+1 < len(args):
        #     SERVER_CONFIG["dir"] = args[i+1]
        #     i += 1
        # elif args[i] == "--dbfilename" and i+1 < len(args):
        #     SERVER_CONFIG["dbfilename"] = args[i+1]    
        #     i += 1
        # i += 1
        
    

async def main():
    """Start an asynchronous server."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str)
    parser.add_argument('--dbfilename', type=str)
    args = parser.parse_args()
    # print
    # global dir, dbfilename
    # if args.dir:
    #     SERVER_CONFIG[dir] = args.dir
    # if args.dbfilename:
    #     SERVER_CONFIG[dbfilename] = args.dbfilename
    parse_args(args)
    
    server = await asyncio.start_server(handle_client_connection, "localhost", 6379)
    
    addr = server.sockets[0].getsockname()
    print(f"Server is running on {addr}")
    
    async with server:
        await server.serve_forever() # Keep the server running
        
# In-memory storage for SET/GET commands
RESP_STORAGE = {}
EXPIRATION_TIMES = {}
SERVER_CONFIG = {}

if __name__ == "__main__":
    try:
        asyncio.run(main()) # Run the event loop
    except KeyboardInterrupt:
        print(f"Server stopped by user.")
