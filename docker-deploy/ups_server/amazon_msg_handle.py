from concurrent.futures import ThreadPoolExecutor
import time
from db_operation import *
from utils import *
from socket_handle import *
import world_ups_pb2
import amazon_ups_pb2


def order_pickup(order_truck, world_id, world_socket, amazon_socket):
  print("start order truck")
  try:
    UCommand_amazon = amazon_ups_pb2.UCommand()
    UCommand_amazon.acks.append(order_truck.seqnum)
    send_msg(UCommand_amazon, amazon_socket)
    seqnum = get_curr_seqnum()
    package_id = order_truck.packageID
    username = order_truck.upsUsername
    truck_id = 0
    while True:
        truck_id = get_free_truck(world_id)
        if truck_id != None:
            break
    user_id = get_user_id_by_username(username)
    warehouse_id = order_truck.warehouseInfo.warehouseID
    start_x = order_truck.warehouseInfo.x
    start_y = order_truck.warehouseInfo.y
    end_x = order_truck.destinationInfo.x
    end_y = order_truck.destinationInfo.y
    description = ""
    for i in range(len(order_truck.productInfo)):
      description += order_truck.productInfo[i].description + "\n"
    create_new_package(user_id, truck_id, str(warehouse_id), world_id,
                       str(package_id), str(start_x), str(start_y), str(end_x), str(end_y), description)
    UCommand = world_ups_pb2.UCommands()
    pickup = UCommand.pickups.add()
    pickup.truckid = truck_id
    pickup.whid = warehouse_id
    pickup.seqnum = seqnum
    update_truck(truck_id, world_id, "t", None, None)
    while True:
        send_msg(UCommand, world_socket)
        if check_ack(seqnum):
            break
  except BaseException as e:
    print("catch exception in world pickup: ", e)
  print("end order truck")


def order_deliver(init_delivery, world_id, world_socket, amazon_socket):
  print("start order deliver")
  try:
    UCommand_amazon = amazon_ups_pb2.UCommand()
    UCommand_amazon.acks.append(init_delivery.seqnum)
    send_msg(UCommand_amazon, amazon_socket)
    seqnum = get_curr_seqnum()
    package_id = init_delivery.packageID
    truck_id, end_x, end_y = get_package_truck_and_destination(str(package_id))
    UCommand = world_ups_pb2.UCommands()
    deliver = UCommand.deliveries.add()
    deliver.truckid = truck_id
    deliver.seqnum = seqnum
    first_deliver = UCommand.deliveries[0]
    location = first_deliver.packages.add()
    location.packageid = package_id
    location.x = int(end_x)
    location.y = int(end_y)
    update_truck(truck_id, world_id, "d", None, None)
    update_package_status_to(str(package_id), world_id, "delivering")
    user_email = get_user_email(str(package_id), world_id)
    # if user_email:
    #     send_email(user_email, "Package on the way")
    while True:
        send_msg(UCommand, world_socket)
        if check_ack(seqnum):
            break
  except Exception as e:
    print("error catch in order deliver: ", e)
  print("end order deliver")

def check_users(check_user, amazon_socket):
  print("start check user")
  try:
    username = check_user.upsUsername
    UCommand_amazon = amazon_ups_pb2.UCommand()
    UCommand_amazon.acks.append(check_user.seqnum)
    send_msg(UCommand_amazon, amazon_socket)
    if not check_user_exist(username):
        generate_username_response(check_user, username, -1, amazon_socket)
    else:
        upsUserID = get_user_id_by_username(username)
        generate_username_response(check_user, username, upsUserID, amazon_socket)
  except Exception as e:
    print("error catch in check user: ", e)
  print("end check user")


def generate_username_response(check_user, username, upsUserID, amazon_socket):
  try:
    UCommand_amazon = amazon_ups_pb2.UCommand()
    check_user_response = UCommand_amazon.checkUser.add()
    check_user_response.upsUsername = username
    check_user_response.upsUserID = upsUserID
    check_user_response.seqnum = check_user.seqnum
    send_msg(UCommand_amazon, amazon_socket)
  except Exception as e:
    print("error occur when generate check user response: ", e)


def amazon_recver(world_id, amazon_socket, world_socket):
    num_threads = 5
    pool = ThreadPoolExecutor(num_threads)
    while True:
      try:
        ACommand = recv_msg(amazon_socket, "amazon_msg")
        for i in range(len(ACommand.toOrder)):
            pool.submit(order_pickup, ACommand.toOrder[i], world_id,
                        world_socket, amazon_socket)
        for i in range(len(ACommand.toStart)):
            pool.submit(order_deliver, ACommand.toStart[i],
                        world_id, world_socket, amazon_socket)
        for i in range(len(ACommand.checkUsers)):
            pool.submit(check_users, ACommand.checkUsers[i], amazon_socket)
        if len(ACommand.acks):
            pool.submit(ack_handler_amazon, ACommand.acks)
      except Exception as e:
        print("Amazon receiver multithread error:", e)
