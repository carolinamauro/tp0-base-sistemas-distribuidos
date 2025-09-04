import socket
import logging
import signal
from common.protocol import Protocol
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

        signal.signal(signal.SIGTERM, self.__handle_sigterm_signal)
        while self._listening:
            try:
                agency_sock = self.__accept_new_connection()
                protocol = Protocol(agency_sock)
                self._active_agencies_connections.append(protocol)
                self.__handle_agency_connection(protocol)
            except OSError as e:
                if self._listening:
                    logging.error(f"action: accept_connections | result: fail | error: {e}")
                else:
                    logging.info("action: server_shutdown | result: in_progress")
                break 
                 
        self.__close_server_socket()
        logging.info("action: server_shutdown | result: success")     

    def __handle_agency_connection(self, protocol):
        """
        Read message from a specific agency socket and closes the socket

        If a problem arises in the communication with the agency, the
        agency socket will also be closed
        """
        try:
            # Receive message from agency
            bet = protocol.receive_menssage()
            logging.info(f'action: receive_message | result: success | ip: {protocol.addr()} | msg: {bet.agency}, {bet.first_name}, {bet.last_name}, {bet.document}, {bet.birthdate}, {bet.number}')
            # Store bet information
            store_bets([bet])
            # Log bet storage
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
             # Send ACK to agency
            protocol.send_ack()
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            protocol.close()
            self._active_agencies_connections = [p for p in self._active_agencies_connections if p.is_same_socket(protocol) == False]

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
    
    def __close_server_socket(self):
        """
        Close server socket and stops listening for new connections
        """
        
        self._listening = False
        self._server_socket.close()
    
    def __handle_sigterm_signal(self, signum, frame):
        """
        Handles the SIGTERM signal to close all connections gracefully
        1. Closes the server socket to stop accepting new connections
        2. Closes all active client connections
        """
        
        self.__close_server_socket()
        logging.info('action: SIGTERM signal received | result: in_progress')
        for protocol in self._active_agencies_connections:
            protocol.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket: {protocol._agency_socket}')
        socket_addr = self._server_socket.getsockname()[0]
        logging.info(f'action: SIGTERM signal received | result: success | server socket: {socket_addr}')

        
