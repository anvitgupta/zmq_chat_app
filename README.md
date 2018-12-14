## ZMQ Chat App

#### Team Members: Suhaas Yerramreddy, Varun Arora, Anvit Gupta

## Functionality ##

* Encrypted single user chat
* Encrypted group chat
* In case of user disconnect, recovering all single user and group chat data for that user

## Techstack ##

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

* InfluxDB cluster: Resilient design made up of three meta nodes and a data set with three replicas

## Flow and logic ##

## Failure mode analysis

## Future design improvements ##







