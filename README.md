## ZMQ Chat App

#### Team Members: Suhaas Yerramreddy, Varun Arora, Anvit Gupta

## Functionality ##

* Encrypted single user chat
* Encrypted group chat
* In case of user disconnect, recovering all single user and group chat data for that user

## Tech Stack ##

* Python
* ZeroMQ
* Amazon EC2
* InfluxDB Enterprise
* Flask

## Architecture ##

![Architecture](https://github.com/vu-resilient-distributed-18/team-dark/blob/master/Capture.JPG)

* Client: Uses two sockets, a REQ to send messages and a SUB to listen to messages for the client

* Load balancer: Forwards requests and responses between client and server using round robin

* Server: Contains logic to create a user, create a group, write to InfluxDB, and send messages between clients. 

* InfluxDB cluster: Resilient database made up of three meta nodes and a data set with three replicas

## Flow and logic ##

1) User logs in via a login name and a REQ and SUB socket are created with the REQ being connected to the load balancer
2) Client sends a request to load balancer with its name so that a ZMQ topic can be created 
3) Server is notified of a new user
4) A topic is created with the users name that the SUB socket in the client subscribes to
5) An entry is created in Influx with the new users name

* One on one chat: 
1) When sending a message, the client sends a JSON to the server containing information about who the message is going to and the contents of the message
2) Influx saves this data for both the sender and receiver
3) The message is then forwarded to the receiver via the SUB socket

* Multichat:
1) A client creates the group using the REQ socket which contains the names of everyone in the group and a group name
3) Influx saves the group name and everyone in the group to a seperate measurement than the message storage 
4) All users in the chat are notified that they have been added
5) When sending a message, a user uses the REQ socket to send a JSON containing the group name and the message to be sent
6) Each message in the chat is saved to each users personal message storage in Influx  
7) The server queries for all the users in the group and forwards the message to each individual user via their own SUB socket

## Encryption

Since we have adopted a mailbox model for delivering messages (both individual and group messages), it was simple to encrypt messages. Each message is encrypted with the recipient's public key (which is generated client-side and sent to the server when a user is created, then stored in a database and in memory). Since group messages are really just a number of one-to-one messages(for the server) with our data model, we can encrypt messages with different public keys and all users can all decode with their own private key. The encryption library we used was pycrypto, and the encryption scheme we used to generate the key pair was RSA.

## Failure mode analysis

* Mailbox architecture for messages
* Load balancer
    * Problem: Clients have a single point of communication and in the case of failure will lead to the app crashing
    * Tentative solution: Vertically scale load balancer or use RDNS with servers
* Server
    * Problem: Can tolerate up to 2 failures 
    * Tentative solution: Add more machines
* InfluxDB cluster
    * Problem: Can tolerate up to 2 failures per shard
    * Tentative solution: Increase number of meta nodes(too much overhead) and shard replica sets

