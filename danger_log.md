# Danger Log

This document outlines issues encountered in package handling, front-end development, and their respective solutions.

## 1. Migration Problems

**Problem:** Failure to migrate in Docker, resulting in the creation of duplicate relations even when they already exist.

**Solution:** Modify the docker-compose.yml file to perform `makemigrations` and `migrate` commands only once.

## 2. Password Reset Server

**Problem:** Unable to create a unique password reset server on Docker, leading to an error indicating inability to open at 127.0.0.1.

**Solution:** Change the server address in the password reset link from 127.0.0.1 to localhost.

## 3. Stuck Shipment

**Problem:** Shipment remains stuck in its current status if commands are not successfully sent to the world due to a closed connection.

**Solution:** Implement an acknowledgment confirmation message system to record missed messages and resend them until receiving a confirmation from the world after a certain time.

## 4. Not Null Foreign Key for Truck, Warehouse, and Package

**Problem:** Packages may not initially have truck and warehouse foreign keys.

**Solution:** Add `Null=True` in the package's declaration of truck and warehouse to allow for null values initially.

## 5. Concurrent Request Handling Issue with Amazon

**Problem:** The system struggles to process and acknowledge multiple simultaneous requests from Amazon.

**Solution:** We restructured the data handling operations to enable atomic transactions, ensuring each request is processed independently and reliably.

## 6. Backend and Frontend Socket Connection Error

**Problem:** The backend, after receiving a message from the frontend, sends an "index out of range" error repeatedly upon receiving a package ID from the frontend.

**Solution:** Modify the communication protocol to first transmit the length of the message, followed by the main message itself. This sequential approach helps to manage the data flow and prevent indexing errors.