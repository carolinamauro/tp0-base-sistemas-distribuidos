import socket
import logging
from common.utils import Bet

SIZE_SERIALIZED_MESSAGE_LENGHT = 2
MESSAGE_TYPE_SIZE = 1

MESSAGE_TYPE_BET = 1
MESSAGE_TYPE_CHUNK = 2
MESSAGE_TYPE_END_OF_CHUNKS = 3
MESSAGE_TYPE_AGENCY_ID = 4
MESSAGE_TYPE_LOTTERY_RESULT = 5
MESSAGE_TYPE_ACK = 0xFF
ACK_OK = 0x00

class Protocol:
  def __init__(self, agencySocket: socket):
    self._agency_socket = agencySocket
    self.agency_id = None
   
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
  
  def receive_message_type(self):
    """
    Receives the message type from the agency socket
    
    Returns the message type as an integer in case of success.
    Otherwise, it returns None.
    """
    message_type = self._agency_socket.recv(MESSAGE_TYPE_SIZE)
    if message_type:
      return message_type[0]
    else:
      return None
    
  def is_chunk_message(self, message_type):
    return message_type == MESSAGE_TYPE_CHUNK

  def is_end_of_chunks_message(self, message_type):
    return message_type == MESSAGE_TYPE_END_OF_CHUNKS
  
  def is_agency_id_message(self, message_type):
    return message_type == MESSAGE_TYPE_AGENCY_ID
  
  def receive_chunk(self):
    """
    Receives a message from the agency socket
    
    Returns a Bet object in case of success when the message type is
    MESSAGE_TYPE_BET. Otherwise, it returns None.
    """
    data = self.__receive_all()
    bets = []
    while data:
      length = int.from_bytes(data[1:3], byteorder='big')
      bet_serialized = data[3:3+length]
      bet = Bet.deserialize(bet_serialized)
      bets.append(bet)
      data = data[3+length:]
      
    return bets
  
  def receive_agency_id(self):
    """
    Receives the agency ID from the agency socket
    
    Returns the agency ID as an integer in case of success.
    Otherwise, it returns None.
    """
    data = self.__receive_all()
    agency_id = int(data.decode())
    self.agency_id = agency_id
  
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
    self.send_message(MESSAGE_TYPE_ACK, ACK_OK.to_bytes(1, byteorder='big'))
    
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
    
  def send_lottery_result(self, winners: list[Bet]):
    message = bytearray()
    for bet in winners:
      serialized_dni = bet.serialize_dni_field()
      message.extend(serialized_dni)
      
    self.send_message(MESSAGE_TYPE_LOTTERY_RESULT, message)
  
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
  