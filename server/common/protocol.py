import socket
from common.utils import Bet

MESSAGE_TYPE_BET = 1
SIZE_SERIALIZED_MESSAGE_LENGHT = 2
MESSAGE_TYPE_SIZE = 1

ACK_MESSAGE_TYPE = 0xFF
ACK_OK = 0x00

class Protocol:
  def __init__(self, agencySocket: socket):
    self._agency_socket = agencySocket
  
   
  def __receive_all(self):
    """" 
    Receives all the bytes of the message
    
    First, it reads the message length (2 bytes) and then
    it reads the message itself.
    
    Returns ConnectionError in case of failure
    """
    bytes = b""
    message_length_bytes = self._agency_socket.recv(SIZE_SERIALIZED_MESSAGE_LENGHT) 
    message_length = int.from_bytes(message_length_bytes, byteorder='big')
    while len(bytes) < message_length:
      data = self._agency_socket.recv(message_length - len(bytes))
      if not data:
        raise ConnectionError("Connection closed by the other side")
      bytes += data
    return bytes
  
  def receive_menssage(self):
    """
    Receives a message from the agency socket
    
    Returns a Bet object in case of success when the message type is
    MESSAGE_TYPE_BET. Otherwise, it returns None.
    """
    message_type = self._agency_socket.recv(MESSAGE_TYPE_SIZE)
    data = self.__receive_all()
    
    if message_type and message_type[0] == MESSAGE_TYPE_BET:
      return Bet.deserialize(data)
    else:
      pass
    
  def __send_all(self, bytes: bytes):
    """
    Sends all the bytes of the message passed as parameter.
    
    Returns the number of bytes sent. Raises ConnectionError in case of failure.
    """
    bytes_sent = 0
    while bytes_sent < len(bytes):
      bytes_sent += self._agency_socket.send(bytes[bytes_sent:])
      if bytes_sent == 0:
        raise ConnectionError("Connection closed by the other side")
    
    return bytes_sent
  
  def send_ack(self):
    """
    Sends an ACK message to the agency socket
    """
    self.send_message(ACK_MESSAGE_TYPE, ACK_OK.to_bytes(1, byteorder='big'))
    
  def send_message(self, message_type: int, data: bytes):
    """
    Sends a message to the agency socket. The message is composed by:
    - message type (1 byte)
    - message length (2 bytes)
    - message data (message length bytes)
    
    Returns the number of bytes sent. Raises ConnectionError in case of failure.
    """
    message = bytearray()
    message.append(message_type)
    message.extend(len(data).to_bytes(2, byteorder='big'))
    message.extend(data)
    
    self.__send_all(message)
  
  def close(self):
    """
    Closes the agency socket
    """
    self._agency_socket.close()
    
  def addr(self):
    """
    Returns the IP address of the agency socket
    """
    return self._agency_socket.getpeername()[0]
  
  def is_same(self, protocol):
    """
    Compares the agency socket with another socket passed as parameter
    
    Returns True if both sockets are the same, False otherwise
    """
    return self._agency_socket == protocol._agency_socket
  