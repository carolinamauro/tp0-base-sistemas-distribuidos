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
        while True:
            agency_sock = self.__accept_new_connection()
            self._active_agencies_connections.append(agency_sock)
            self.__handle_agency_connection(agency_sock)

    def __handle_agency_connection(self, agency_sock):
        """
        Read message from a specific agency socket and closes the socket

        If a problem arises in the communication with the agency, the
        agency socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            transport = Transport(agency_sock)
            bet = transport.receive_menssage()
            store_bets([bet])
            # Send ACK to agency
            transport.send_ack()
            # logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            agency_sock.close()
            self._active_agencies_connections.remove(agency_sock)

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
        logging.info('action: SIGTERM signal received | result: in_progress')
        for agency_socket in self._active_agencies_connections:
            agency_socket.close()
            logging.info('action: SIGTERM signal received | result: success | agency socket: {agency_socket}')
        self._server_socket.close()            
        logging.info('action: SIGTERM signal received | result: success | server socket: {self._server_socket}')
        sys.exit(0)

        
