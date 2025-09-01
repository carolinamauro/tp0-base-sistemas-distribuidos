import socket
import logging
import signal
import sys
from common.transport import Transport
from common.utils import store_bets

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_agencies_connections = []
        self._listening = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a agency. After agency with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        signal.signal(signal.SIGTERM, self.__handle_sigterm_signal)
        while self._listening:
            try:
                agency_sock = self.__accept_new_connection()
                transport = Transport(agency_sock)
                self._active_agencies_connections.append(transport)
                self.__handle_agency_connection(transport)
            except OSError as e:
                if self._listening:
                    logging.error(f"action: accept_connections | result: fail | error: {e}")
                else:
                    logging.info("action: server_shutdown | result: in_progress")
                break           

    def __handle_agency_connection(self, transport):
        """
        Read message from a specific agency socket and closes the socket

        If a problem arises in the communication with the agency, the
        agency socket will also be closed
        """
        try:
            # Receive message from agency
            message = transport.receive_message_type()
            if message is None:
                raise OSError("Connection closed by the other side")
            if transport.is_chunk_message(message):
                self.__handle_chunck_message(transport)
                while True:
                    message = transport.receive_message_type()
                    if message is None:
                        raise OSError("Connection closed by the other side")
                    if transport.is_last_chunk_message(message):
                        self.__handle_chunck_message(transport)
                        break
                    elif transport.is_chunk_message(message):
                        self.__handle_chunck_message(transport)
                    else:
                        raise OSError("Invalid message type received")
            else:
                raise OSError("Invalid message type received")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            transport.close()
            self._active_agencies_connections.remove(transport)
            
    def __handle_chunck_message(self, transport):
        bets = transport.receive_chunk()
        store_bets(bets)
        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
        transport.send_ack()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a agency is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
    
    def __handle_sigterm_signal(self, signum, frame):
        self._listening = False
        logging.info('action: SIGTERM signal received | result: in_progress')
        for transport in self._active_agencies_connections:
            transport.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket: {transport._agency_socket}')
        socket_addr = self._server_socket.getsockname()[0]
        self._server_socket.close()            
        logging.info(f'action: SIGTERM signal received | result: success | server socket: {socket_addr}')

        
