from django.db import models
from django.contrib.auth.models import AbstractUser



class World(models.Model):
    __tablename__ = 'ups_world'
    id = models.CharField(primary_key=True, max_length=512)
    curr_world = models.BooleanField(default=True)


class User(AbstractUser):
    __tablename__ = 'ups_user'
    phone_number = models.CharField(max_length=15, default="1234567890")
    profile_image = models.ImageField(upload_to='profile_images/', default='img/profile.ico')
    # world_id = models.ForeignKey(World, on_delete=models.CASCADE)


class Truck(models.Model):
    __tablename__ = 'ups_truck'
    id = models.AutoField(primary_key=True)
    STATUS = (
        ('i', 'IDLE'),
        ('t', 'TRAVELING'),
        ('l', 'LOADING'),
        ('d', 'DELIVERING')
    )
    current_status = models.CharField(max_length=1, choices=STATUS, default='i')
    pos_x = models.CharField(max_length=30)
    pos_y = models.CharField(max_length=30)
    world = models.ForeignKey(World, on_delete=models.CASCADE)


class Warehouse(models.Model):
    __tablename__ = 'ups_warehouse'
    id = models.AutoField(primary_key=True)
    warehouse_name = models.CharField(max_length=512)
    pos_x = models.CharField(max_length=30)
    pos_y = models.CharField(max_length=30)


class Package(models.Model):
    __tablename__ = 'ups_package'
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, max_length=30, on_delete=models.CASCADE, related_name='packages')
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, null=True, related_name='packages')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, related_name='packages')
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    track_number = models.CharField(max_length=512)

    # start_location = models.CharField(max_length=255, default="n/a")
    # end_location = models.CharField(max_length=255, default="n/a")
    start_x = models.CharField(max_length=30, default="n/a")
    start_y = models.CharField(max_length=30, default="n/a")
    end_x = models.CharField(max_length=30, default="n/a")
    end_y = models.CharField(max_length=30, default="n/a")
    description = models.TextField(blank=True, null=True)

    STATUS = (
        ('p', 'wait for pick up'),
        ('o', 'out for delivery'),
        ('d', 'delivered for delivery')
    )

    package_status = models.CharField(max_length=20, choices=STATUS, default='d')

class subscribeEmail(models.Model):
    __tablename__ = 'ups_subscribeEmail'
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=254)