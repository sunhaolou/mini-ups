import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import create_engine, MetaData, func, inspect, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.automap import automap_base



engine = create_engine(
    'postgresql://postgres:postgres@db:5432/ups_database'
)

Session = scoped_session(sessionmaker(bind=engine))
metadata = sqlalchemy.MetaData()
Base = automap_base()
Base.prepare(autoload_with=engine)

World = Base.classes.ups_world
User = Base.classes.ups_user
Truck = Base.classes.ups_truck
Warehouse = Base.classes.ups_warehouse
Package = Base.classes.ups_package


def drop_all_and_init():
    session = Session()
    try:
        meta = MetaData()
        meta.reflect(bind=engine)
        for table in reversed(meta.sorted_tables):
            session.execute(table.delete())
        inspector = inspect(engine)
        for seq in inspector.get_sequence_names():
            session.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))
        session.commit()
    except Exception as e:
        print(f"Error occur when drop and init: {e}")
        session.rollback()
    finally:
        session.close()


def check_world_exist(world_id):
    session = Session()
    try:
        result = session.query(World).filter(World.id == world_id).first()
    except Exception as e:
        print("error catch in check world: ", e)
    finally:
        session.close()
        return result is not None


def check_user_exist(username):
    session = Session()
    try:
        result = session.query(User).filter(User.username == username).first()
    except Exception as e:
        print("error catch in check user: ", e)
    finally:
        session.close()
        return result is not None


def get_user_id_by_username(username):
    session = Session()
    try:
        result = session.query(User).filter(
            User.username == username).first()
    except Exception as e:
        print("error catch in get user by username: ", e)
    finally:
        session.close()
        return result.id


def create_new_world(world_id):
    session = Session()
    try:
        world = World(id=world_id, curr_world=True)
        session.add(world)
        session.commit()
    except Exception as e:
        session.rollback()
        print("error catch in create new world: ", e)
    finally:
        session.close()


def create_trucks_for_world(world_id):
  try:
    session = Session()
    session.query(Truck).delete()
    session.execute(text("ALTER SEQUENCE ups_truck_id_seq RESTART WITH 1;"))
    for i in range(100):
        session.add(Truck(current_status='i', pos_x=0,
                    pos_y=0, world_id=world_id))
    session.commit()
  except Exception as e:
      print("error catch in create trucks for world: ", e)
  finally:
      session.close()


def update_world(world_id):
    session = Session()
    try:
        session.query(World).filter(
            World.id != world_id).update({"curr_world": False})
        world = session.query(World).filter(World.id == world_id).first()
        if world is not None:
            world.curr_world = True
        session.commit()
    except Exception as e:
        print("error catch in update world: ", e)
    finally:
        session.close()


def update_truck(truck_id, world_id, truck_status, new_pos_x, new_pos_y):
    session = Session()
    try:
        truck = session.query(Truck).filter(
            Truck.id == truck_id, Truck.world_id == world_id).first()
        if truck is not None:
            truck.current_status = truck_status
            if new_pos_x is not None:
                truck.pos_x = new_pos_x
            if new_pos_y is not None:
                truck.pos_y = new_pos_y
            session.commit()
        else:
            print("Truck not found")
    except Exception as e:
        print("error catch in update truck: ", e)
    finally:
        session.close()


def create_new_package(user_id, truck_id, warehouse_id, world_id, track_number, start_x, start_y, end_x, end_y, description):
    session = Session()
    try:
      get_warehouse = session.query(Warehouse).filter(Warehouse.pos_x == start_x, Warehouse.pos_y == start_y).first()
      if get_warehouse is None:
          session.add(Warehouse(warehouse_name=warehouse_id, pos_x=start_x, pos_y=start_y))
      curr_warehouse = session.query(Warehouse).filter(Warehouse.pos_x == start_x, Warehouse.pos_y == start_y).first()
      package = Package(
          user_id=user_id,
          truck_id=truck_id,
          warehouse_id=curr_warehouse.id,
          world_id=world_id,
          track_number=track_number,
          start_x=start_x,
          start_y=start_y,
          end_x=end_x,
          end_y=end_y,
          description=description,
          package_status='p'
      )
      session.add(package)
      session.commit()
    except Exception as e:
        print("error catch in create new package: ", e)
    finally:
      session.close()


def update_package_destination(package_id, world_id, new_pos_x, new_pos_y):
    session = Session()
    try:
        package = session.query(Package).filter_by(
            track_number=package_id, world_id=world_id).first()
        if package:
            package.end_x = new_pos_x
            package.end_y = new_pos_y
            session.commit()
    except Exception as e:
        print("error catch in update package destination: ", e)
    finally:
        session.close()


def update_package_status_to(package_id, world_id, new_status):
    session = Session()
    try:
        package = session.query(Package).filter_by(
            track_number=package_id, world_id=world_id).first()
        if package:
            if new_status == "delivering":
                package.package_status = 'o'
            elif new_status == "delivered":
                package.package_status = 'd'
            else:
                raise ValueError("Wrong status for package")
        session.commit()
    except Exception as e:
        print("error catch in update package status: ", e)
    finally:
        session.close()


def get_package_truck_and_destination(package_id):
    session = Session()
    try:
        package = session.query(Package).filter_by(track_number=package_id).first()
        if package:
            truck_id = package.truck_id
            end_x = package.end_x
            end_y = package.end_y
        else:
            raise ValueError(f"Package with track number {package_id} not found.")
    except Exception as e:
        print("error catch in get package truck and destination: ", e)
    finally:
        session.close()
        return truck_id, end_x, end_y


def get_package_track_number_and_destination(id):
    session = Session()
    try:
        package = session.query(Package).filter_by(id=id).first()
        if package:
            track_number = package.track_number
            end_x = package.end_x
            end_y = package.end_y
        else:
            raise ValueError(f"Package with id {id} not found.")
    except Exception as e:
        print("error catch in get package track_number and destination: ", e)
    finally:
        session.close()
        return track_number, end_x, end_y

def get_user_email(package_id, world_id):
    session = Session()
    try:
        user_id = session.query(Package.user_id).filter(
            Package.track_number == package_id, Package.world_id == world_id).scalar_subquery()
        result = session.query(User).filter(User.id == user_id).first()
        if result is None:
            print("no email found")
        return result.email
    except Exception as e:
        print("error catch in get user email: ", e)
    finally:
        session.close()


def get_package_at_warehouse(truck_id, world_id, warehouse_x, warehouse_y):
    session = Session()
    try:
        warehouse = session.query(Warehouse).filter(
            Warehouse.pos_x == warehouse_x, Warehouse.pos_y == warehouse_y).first()
        if warehouse is None:
            print("No warehouse found at the specified coordinates.")
            return None


        result = session.query(Package).filter(
            Package.truck_id == truck_id,
            Package.world_id == world_id,
            Package.warehouse_id == warehouse.id,
            Package.package_status == 'p'
        ).first()

        if result is None:
            print("No package found at this warehouse.")
            return None
        return result.track_number
    except Exception as e:
        print("error catch in get package at warehouse: ", e)
    finally:
        session.close()



def get_free_truck(world_id):
    session = Session()
    try:
        result = session.query(Truck).filter(
            Truck.current_status == 'i', Truck.world_id == world_id).first()
        if result is None:
            print("No free truck found, please wait")
            return None
        return result.id
    except Exception as e:
        print("error catch in get free truck: ", e)
    finally:
        session.close()


def get_package_status_and_truck(package_id, world_id):
    session = Session()
    try:
        package = session.query(Package).filter(
            Package.track_number == package_id, Package.world_id == world_id).first()
        if package:
            status = package.package_status
            truck_id = package.truck_id
            return status, truck_id
        else:
          return None
    except Exception as e:
        print("error catch in get package status and truck: ", e)
    finally:
        session.close()