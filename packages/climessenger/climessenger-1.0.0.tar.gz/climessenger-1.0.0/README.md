climessenger
============

**climessenger** is a CLI messenger built on Flask with HTTPS, allowing text messages to be sent between machines. It supports multithreading and automatic SSL certificate generation upon installation.

Installation
------------

    pip install climessenger

Usage
-----

### 1\. Starting the server to receive messages

    climessenger receive

Starts an HTTPS server that listens on port 8864 and accepts messages from other devices.

### 2\. Sending a message to another server

    climessenger send 192.168.1.68 "Hello World"

Sends the message `Hello World` to the server running at the address `192.168.1.68`. The server must already be running using `receive`.

Author: RUIS

Email: [ruslan@ruisvip.ru](mailto:ruslan@ruisvip.ru)

GitHub: [https://github.com/Ruslan-Isaev/climessenger](https://github.com/Ruslan-Isaev/climessenger)
