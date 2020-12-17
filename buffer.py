import sys

fileno = sys.stdin.fileno()

# async def putbuffer(inp):
    

with open(fileno, "rb", closefd=False) as f:
    while True:
        inp = f.read(1024*1024*256)
        if not inp:
            break
        sys.stdout.buffer.write(inp)
#         print("Got:", inp)

