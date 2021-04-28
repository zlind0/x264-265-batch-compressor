import sys
from threading import Thread
from time import sleep
fileno = sys.stdin.fileno()

buffer_read=None
buffer_write=None

def putbuffer():
    global buffer_write
    if buffer_write is not None:
        sys.stdout.buffer.write(buffer_write)


if __name__ == "__main__":
    with open(fileno, "rb", closefd=False) as f:
        while True:
            thread = Thread(target = putbuffer, daemon=True)
            thread.start()
            buffer_read = f.read(1024*1024*128)
            thread.join()
            if not buffer_read:
                break
            buffer_write=buffer_read