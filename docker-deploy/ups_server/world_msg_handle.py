from concurrent.futures import ThreadPoolExecutor
import os
from db_operation import *
from socket_handle import *
from utils import *


def truck_arrive_handler(completions, world_id, amazon_socket, world_socket):
  print("start world truck handler")
  try:
    UCommands_world = world_ups_pb2.UCommands()
    UCommands_world.acks.append(completions.seqnum)
    send_msg(UCommands_world, world_socket)
    truck_id = completions.truckid
    warehouse_x = completions.x
    warehouse_y = completions.y
    update_truck(truck_id, world_id, "l", warehouse_x, warehouse_y)
    UCommand_amazon = amazon_ups_pb2.UCommand()
    print("here is truck id: ", truck_id)
    package_id = get_package_at_warehouse(
        truck_id, str(world_id), str(warehouse_x), str(warehouse_y))
    print("here is found package id: ", package_id)
    arrive = UCommand_amazon.arrived.add()
    arrive.packageID = int(package_id)
    arrive.truckID = truck_id
    arrive.seqnum = get_curr_seqnum()
    send_msg(UCommand_amazon, amazon_socket)

  except Exception as e:
    print("error catch in truck arrive handler: ", e)

  print("end world truck handler")


def truck_deliver_finish_handler(completions, world_id, world_socket):
  print("start wolrd deliver finish handler")
  try:
    UCommands_world = world_ups_pb2.UCommands()
    UCommands_world.acks.append(completions.seqnum)
    send_msg(UCommands_world, world_socket)
    truck_id = completions.truckid
    warehouse_x = completions.x
    warehouse_y = completions.y
    update_truck(truck_id, world_id, "i", warehouse_x, warehouse_y)
  except Exception as e:
    print("error catch in truck deliver finish: ", e)
  print("end wolrd deliver finish handler")


def completion_handler(completions, world_id, amazon_socket, world_socket):
    if completions.status == "IDLE":
        truck_deliver_finish_handler(completions, world_id, world_socket)
    else:
        truck_arrive_handler(completions, world_id,
                             amazon_socket, world_socket)


def package_delivered_handler(delivered, world_id, amazon_socket, world_socket):
  print("start world package delivered handler")
  try:
    UCommands_world = world_ups_pb2.UCommands()
    UCommands_world.acks.append(delivered.seqnum)
    send_msg(UCommands_world, world_socket)
    package_id = delivered.packageid
    update_package_status_to(str(package_id), world_id, "delivered")
    UCommand_amazon = amazon_ups_pb2.UCommand()
    delivered = UCommand_amazon.delivered.add()
    delivered.packageID = package_id
    delivered.seqnum = get_curr_seqnum()
    send_msg(UCommand_amazon, amazon_socket)
    user_email = get_user_email(str(package_id), world_id)
    # if user_email:
    #     send_email(user_email, "Package has been delivered")
  except Exception as e:
    print("error catch in package delivered: ", e)
  print("end world package delivered handler")


def amazon_disconnect():
    os._exit(0)


def error_handler(error):
    print("Start to print error")
    print(error)


def world_recver(world_id, world_socket, amazon_socket):
    num_threads = 5
    pool = ThreadPoolExecutor(num_threads)
    while True:
      try:
        UResponse = recv_msg(world_socket, "world_msg")
        for i in range(0, len(UResponse.completions)):
            pool.submit(
                completion_handler, UResponse.completions[i], world_id, amazon_socket, world_socket)
        for i in range(0, len(UResponse.delivered)):
            pool.submit(package_delivered_handler,
                        UResponse.delivered[i], world_id, amazon_socket, world_socket)
        if len(UResponse.acks):
            pool.submit(ack_handler, UResponse.acks)
        for i in range(0, len(UResponse.error)):
            pool.submit(error_handler, UResponse.error[i])
        if UResponse.HasField("finished"):
            pool.submit(amazon_disconnect)
      except Exception as e:
        print("World receiver multithread error:", e)