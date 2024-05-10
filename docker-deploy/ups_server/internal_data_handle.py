from concurrent.futures import ThreadPoolExecutor
from db_operation import *
from socket_handle import *
from utils import *

def change_dest(package_id, amazon_socket):
  try:
    UCommand = amazon_ups_pb2.UCommand()
    change = UCommand.changed.add()
    track_number, end_x, end_y = get_package_track_number_and_destination(package_id)
    change.packageID = int(track_number)
    change.NewDestination.x = int(end_x)
    change.NewDestination.y = int(end_y)
    change.seqnum = get_curr_seqnum()
    send_msg(UCommand, amazon_socket)
  except Exception as e:
    print("Error in change destination: ", e)

def internal_recv(client_socket, amazon_socket):
    num_threads = 5
    pool = ThreadPoolExecutor(num_threads)
    while True:
      try:
        package_id = recv_internal(client_socket)
        if package_id:
            print(package_id)
            pool.submit(change_dest, package_id, amazon_socket)
            package_id = None
      except Exception as e:
        print("Internal receiver multithread error:", e)