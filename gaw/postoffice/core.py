import json

class ConnectionTerminated(Exception):
    def __init__(self): super(ConnectionTerminated, self).__init__('Connection Terminated')

def send(socket, data):
    # serialize
    try:
        serialized = json.dumps(data)
    except (TypeError, ValueError) as e:
        raise Exception('You can only send JSON-serializable data')

    # send the data
    socket.send(bytearray('{}\n'.format(len(serialized)), 'ascii'))
    socket.sendall(bytearray(serialized, 'utf-8'))

def recieve(socket):
    # read the length of the data, letter by letter until we reach EOL
    length_str = b''
    char = socket.recv(1)

    # check termination
    if not char:
        raise ConnectionTerminated()

    # got a message
    # read message length
    while char != b'\n':
        length_str += char
        char = socket.recv(1)

    payload_length = int(length_str)

    # get the payload
    buffer = memoryview(bytearray(payload_length))
    next_offset = 0
    while payload_length - next_offset > 0:
        recv_size = socket.recv_into(buffer[next_offset:], payload_length - next_offset)
        next_offset += recv_size

    # deserialize payload
    try:
        data = json.loads(buffer.tobytes().decode('utf-8'))
    except (TypeError, ValueError) as e:
        raise Exception('Data received was not in JSON format')

    return data