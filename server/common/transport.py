import socket
from server.common.utils import Bet

MESSAGE_TYPE_BET = 0x01
SIZE_SERIALIZED_MESSAGE_LENGHT = 0x02
MESSAGE_TYPE_SIZE = 0x01

ACK_MESSAGE_TYPE = 0xFF
ACK_OK = 0x00

class Transport:
  def __init__(self, agencySocket: socket):
    self._agency_socket = agencySocket
  
  def __receive_all(self):
    bytes_received = 0
    message_length =  self._agency_socket.recv(SIZE_SERIALIZED_MESSAGE_LENGHT) 
    while bytes_received < message_length:
      bytes_received += self._agency_socket.recv(message_length - bytes_received)
    
    return bytes_received
  
  def receive_menssage(self):
    message_type = self._agency_socket.recv(MESSAGE_TYPE_SIZE) 
    data = self.__receive_all()
    
    if message_type == MESSAGE_TYPE_BET:
      return Bet.deserialize(data)
    else:
      raise ValueError("Unknown message type")
    
  def __send_all(self, bytes: bytes):
    bytes_sent = 0
    while bytes_sent < len(bytes):
      bytes_sent += self._agency_socket.send(bytes[bytes_sent:])
    
    return bytes_sent
  
  def send_ack(self):
    self.send_message(ACK_MESSAGE_TYPE, ACK_OK.to_bytes(1, byteorder='big'))
    
  def send_message(self, message_type: int, data: bytes):
    message = bytearray()
    message.append(message_type)
    message.append(len(data).to_bytes(2, byteorder='big'))
    message.extend(data)
    
    self.__send_all(message)
  
  def close(self):
    self._agency_socket.close()
  