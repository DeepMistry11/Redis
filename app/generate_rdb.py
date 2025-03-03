import struct
import time
import os
from storage import RESP_STORAGE, EXPIRATION_TIMES

def get_datetime():
    """Returns the current date and time as 19-byte fixed string."""
    # return time.strftime("%Y-%m-%d %H:%M:%S").encode().ljust(19, b' ')
    return time.strftime("%Y-%m-%d %H:%M:%S").encode()

def generate_RDB(SERVER_CONFIG):
    """Generates and writes an RDB file"""
    db_dir = SERVER_CONFIG["dir"]
    db_filename = SERVER_CONFIG["dbfilename"]
    rdb_path = os.path.join(db_dir, db_filename)
    
    os.makedirs(db_dir, exist_ok=True) # Checks if directory exists
    current_time = get_datetime()
    
    if os.path.exists(rdb_path):
        try:
            with open(rdb_path, "rb") as rdb:
                rdb.seek(9)
                creation_time = rdb.read(19)
        except Exception:
            creation_time = current_time
    else:
        creation_time = current_time
    
    with open(rdb_path, "wb") as rdb:
        rdb.write(b"REDIS0009") # Header with Magic string "Redis" with version 9
        rdb.write(struct.pack("<B", 0xFA))
        rdb.write(creation_time)
        rdb.write(current_time) # This is to update last modified time.
        
        for key, val in RESP_STORAGE.items():
            expire_time = EXPIRATION_TIMES.get(key, 0)
            
            if expire_time:
                rdb.write(struct.pack("<B", 0xFD))
                rdb.write(struct.pack("<I", expire_time))
            
            rdb.write(struct.pack("<B", len(key)))
            rdb.write(key.encode())
            rdb.write(struct.pack("<B", len(val)))
            rdb.write(val.encode())
            
        rdb.write(struct.pack("<B", 255))
        rdb.write(struct.pack("<Q", 0))