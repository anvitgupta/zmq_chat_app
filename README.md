## ZMQ Chat App

#### Team Members: Suhaas Yerramreddy, Varun Arora, Anvit Gupta

Our goal is to create an end-to-end chat application using ZMQ. ZMQ provides a high-level abstraction of sockets in order to enable communication between two different systems.  

* Requirements
  * The messages have to be delivered instantly (considering the slight overhead of ZMQ).
  * The users have to be informed in case of networking failure, so that they do not have to wait for a long time without receiving messages.
  * Messages have to be encrypted, so that personal/confidential messages are safe. 


Since we are building a system to accommodate multiple people sending and receiving messages, we design the system to have a broker, so that all of the messaging clients can publish to the broker. In order to secure the messages, we will use the CurveZMQ library to provide encryption. If time permits, we will attempt to use the Signal protocol for advanced end-to-end encryption of messages.
