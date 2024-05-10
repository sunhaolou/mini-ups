import socket
import threading
from db_operation import *
import world_ups_pb2
from socket_handle import *
from world_msg_handle import *
from amazon_msg_handle import *
from internal_data_handle import *


drop_all_and_init()

world_host = "vcm-39267.vm.duke.edu"
world_port = 12345

world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
world_address = (world_host, world_port)
UConnect = world_ups_pb2.UConnect()
try:
    world_socket.connect(world_address)
    print("Connection established with the world simulator.")
except socket.error as e:
    print(f'Error occur in connecting: {e}')

# TODO: need to specify the world_id here
world_id = "86"
world_exist = check_world_exist(world_id)
if not world_exist:
    create_new_world(world_id)
    create_trucks_for_world(world_id)
while True:
    try:
        start = 0
        for i in range(0, 100):
            truck = UConnect.trucks.add()
            truck.id = start
            truck.x = 0
            truck.y = 0
            start += 1
        UConnect.isAmazon = False
        UConnect.worldid = int(world_id)
        send_msg(UConnect, world_socket)
        UConnected = recv_msg(world_socket, "connected")
        print(UConnected.result)
        if UConnected.result != "connected!":
            continue
        world_id = str(UConnected.worldid)
        break
    except Exception as e:
        print("error catch in server wolrd while loop: ", e)

update_world(world_id)
UCommands = world_ups_pb2.UCommands()
UCommands.simspeed = 100
send_msg(UCommands, world_socket)


amazon_port = 34567
amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
while True:
  try:
    amazon_socket.connect(("vcm-40425.vm.duke.edu", amazon_port))
    print('Connected to amazon')
    break
  except Exception as e:
    print("error occur when connect to amazon: ", e)
    time.sleep(3)

print(world_id)

thread_1 = threading.Thread(target=world_recver, name="world", args=(world_id, world_socket, amazon_socket,))
thread_1.start()

thread_2 = threading.Thread(target=amazon_recver, name="amazon", args=(world_id, amazon_socket, world_socket,))
thread_2.start()

server_internal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_internal.bind(("0.0.0.0", 8888))
server_internal.listen(10)

while True:
  try:
    client_socket, client_address = server_internal.accept()
    print(f"Connection from {client_address}")
    break
  except Exception as e:
    print("Error occur when connect to client: ", e)

thread_3 = threading.Thread(target=internal_recv, name="internal", args=(client_socket, amazon_socket,))
thread_3.start()

while True:
  pass