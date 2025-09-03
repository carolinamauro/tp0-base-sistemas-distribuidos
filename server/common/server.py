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

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        signal.signal(signal.SIGTERM, self.__handle_sigterm_signal)
        while self._listening:
            try:
                agency_sock = self.__accept_new_connection()
                protocol = Protocol(agency_sock)
                self.__handle_agency_connection(protocol)
            except OSError as e:
                if self._listening:
                    logging.error(f"action: accept_connections | result: fail | error: {e}")
                else:
                    logging.info("action: server_shutdown | result: in_progress")
                break           

    def __handle_agency_connection(self, protocol):
        """
        Read message from a specific agency socket and closes the socket

        If a problem arises in the communication with the agency, the
        agency socket will also be closed
        """
        
        self._active_agencies_connections.append(protocol)
        try:
            self.__recv_bets(protocol)
        except OSError as e:
            logging.error(f"action: agency_communication | result: fail | error: {e}")
        finally:
            logging.info(f"action: close_agency_connection | result: in_progress | agency socket: {protocol.addr()}")
            protocol.close()
            self._active_agencies_connections = [p for p in self._active_agencies_connections if p._agency_socket != protocol._agency_socket]

    def __recv_bets(self, protocol):
        """
        Receive bets from a specific agency socket

        Function blocks until the agency sends all the bets or an error
        arises. In case of success, the bets received are returned.
        Otherwise, an exception is raised
        """

        while True:
            mtype = protocol.receive_message_type()
            if mtype is None:
                raise OSError("connection closed by peer")

            if protocol.is_chunk_message(mtype):
                try:
                    bets = protocol.receive_chunk()
                except Exception as e:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    raise OSError(f"receive_chunk: {e}")

                logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                try:
                    protocol.send_ack()
                except Exception as e:
                    raise OSError(f"send_ack: {e}")

            elif protocol.is_end_of_chunks_message(mtype):
                logging.info(f"action: agency_finished | result: success | agency_ip: {protocol.addr()}")
                break
            else:
                raise OSError(f"invalid message type: {mtype}")

            
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
        for protocol in self._active_agencies_connections:
            protocol.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket: {protocol._agency_socket}')
        socket_addr = self._server_socket.getsockname()[0]
        self._server_socket.close()            
        logging.info(f'action: SIGTERM signal received | result: success | server socket: {socket_addr}')

        
