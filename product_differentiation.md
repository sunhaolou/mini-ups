# Product Differentiation

## 1. Interactive Homepage

We understand the importance of keeping our users engaged and entertained while they interact with our platform. As such, we have incorporated a fun and interactive feature that enables users to play music directly from our homepage. Users can control the music by clicking on the note icon located at the top left corner of the page.


## 2. User-Friendly Password Reset

Our platform offers a user-friendly password reset feature. Users who forget their passwords can easily reset them by providing their first name, last name, and email address. The server then sends a unique link to the user's email, allowing them to reset their password securely and efficiently.

## 3. Personal Information Update

Users can conveniently update their personal information, such as email addresses and phone numbers, directly on the website.

## 4. Background Music Setting

Our website provides users with background music that seamlessly continues playing as they navigate the site. The music does not restart when users move to different pages, enhancing the overall user experience.

## 5. Email Notifications

The server sends email notifications to users when there is a change in their package status. This feature enables users to stay informed about their package status and prepare for pickup accordingly.

## 6. Contact Info
Users can easily send query emails through the website by providing subject titles, email addresses, and messages. Upon sending the contact email, users receive an automatic reply from the server. Additionally, users can view orders with associated statuses by clicking different buttons, providing them with a better way to manage their orders.

## 7. Package Searching

Users can search for their packages using various keywords such as status, destination, and tracking number, enhancing convenience and efficiency.

## 8. Change Destination

In addition to the basic package management functions, users can request changes to their package's destination. Upon receiving a change destination request, our system allows users to edit the package's destination through the packages table. To ensure consistency, changes to destinations are only permitted before the package reaches the delivery status.

## 9. Tracking History

Our website provides users with a dedicated page to view all their packages and their respective statuses. Users can track when their package's status changes and monitor the delivery locations.

## 10. Registration and Login

We prioritize security by using the Django Framework for user registration and login. User passwords are encrypted before being inserted into the database, mitigating the risk of hackers accessing raw passwords directly.

## 11. Thread and Thread Pool

To handle high concurrency, we utilize threads and thread pools to manage requests efficiently. We create two threads—one for interaction with the external world and another for interaction with Amazon. Each thread splits the message into smaller pieces, and a thread pool handles nested messages. This approach allows for the reuse of threads instead of creating a large number of threads for multithreaded tasks.
