import time
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import world_ups_pb2
import amazon_ups_pb2

def send_msg(msg, socket):
    string = msg.SerializeToString()
    data = []
    _VarintEncoder()(data.append, len(string), None)
    size = b''.join(data)
    socket.sendall(size + string)

def recv_msg(socket, type):
    data = b''
    while True:
        try:
          data += socket.recv(1)
          size = _DecodeVarint32(data, 0)[0]
          break
        except Exception as e:
          time.sleep(1)
          print("Error occur while receiving: ", e)
          continue
    string = socket.recv(size)
    if type == "connected":
      UResponse = world_ups_pb2.UConnected()
    elif type == "world_msg":
      UResponse = world_ups_pb2.UResponses()
    elif type == "amazon_msg":
      UResponse = amazon_ups_pb2.ACommand()
    else:
      raise ValueError("Wrong receiving type")
    if type != "internal":
      UResponse.ParseFromString(string)
    return UResponse


def recv_internal(socket):
    data = b''
    while True:
        byte = socket.recv(1)
        if not byte:
            return
        data += byte
        try:
            size, pos = _DecodeVarint32(data, 0)
            if pos:
                break
        except IndexError:
            continue
    full_msg = b''
    remaining = size
    while remaining > 0:
        chunk = socket.recv(remaining)
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        full_msg += chunk
        remaining -= len(chunk)
    return full_msg.decode('utf-8')