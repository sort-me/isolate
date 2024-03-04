import os

blocks_limits = 32
block_size = os.statvfs('/').f_frsize

# Try to break the quota
try:
    with open('bigfile', 'wb') as f:
        f.write(b'x' * blocks_limits * block_size)
        f.flush()
        os.fsync(f.fileno())
except OSError as e:
    assert e.errno == 122
    print("OK")
    quit(0)

# Check if the quota is broken
with open('bigfile', 'rb') as f:
    assert f.read() == b'x' * blocks_limits * block_size
    f.flush()
    os.fsync(f.fileno())

