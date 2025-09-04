import socket
import logging
import signal
from common.protocol import Protocol
from common.utils import store_bets, load_bets, has_won

class Server:
    def __init__(self, port, listen_backlog, clients_amount):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_agencies_connections = []
        self._clients_amount = clients_amount
        self._finished_agencies = 0
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
        
        self._active_agencies_connections.append(protocol)
        try:
            self.__recv_bets(protocol)
            self._finished_agencies += 1
           
            if self._finished_agencies != self._clients_amount:
                return
            
            self._send_lottery_result_to_agencies()
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            self.__close_connection(protocol)
      
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
                    protocol.send_process_chunk_error()
                    logging.info(f"action: apuesta_recibida | result: fail")
                    raise OSError(f"receive_chunk: {e}")

                store_bets(bets)
                logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                try:
                    protocol.send_ack()
                except Exception as e:
                    raise OSError(f"send_ack: {e}")

            elif protocol.is_end_of_chunks_message(mtype):
                logging.info(f"action: agency_finished | result: success | agency_id: {protocol.agency_id}")
                break
            elif protocol.is_agency_id_message(mtype):
                protocol.receive_agency_id()
                logging.info("action: receive_agency_id | result: success")
            else:
                raise OSError(f"invalid message type: {mtype}")
    
    def _send_lottery_result_to_agencies(self):
        """
        Sends the lottery results to all connected agencies
        1. Loads all bets from storage
        2. Determines the winning bets and groups them by agency
        3. Sends the winning bets to each agency
        4. Closes each agency connection
        """
        logging.info("action: sorteo | result: success")
        winners_by_agency = {}
        winners = [bet for bet in load_bets() if has_won(bet)]
        
        for bet in winners:
            if bet.agency not in winners_by_agency:
                winners_by_agency[bet.agency] = []
            winners_by_agency[bet.agency].append(bet)
        
        for protocol in self._active_agencies_connections:
            try:
                protocol.send_lottery_result(winners_by_agency.get(protocol.agency_id, []))
                logging.info(f"action: send_lottery_result | result: success | agency socket: {protocol.addr()}")
            except Exception as e:
                logging.error(f"action: send_lottery_result | result: fail | agency socket: {protocol.addr()} | error: {e}")
            finally:
                self.__close_connection(protocol)
                self._finished_agencies -= 1

              
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
    
    def __close_connection(self, protocol):
        """
        Close a specific agency connection and removes it from the active connections list
        """
        logging.info(f"action: close_agency_connection | result: success | agency socket: {protocol.addr()}")
        self._active_agencies_connections = [p for p in self._active_agencies_connections if not p.is_same(protocol)]
        protocol.close()
        
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
        
        socket_addr = self._server_socket.getsockname()[0]
        logging.info(f'action: SIGTERM signal received | result: success | server socket: {socket_addr}')
        self.__close_server_socket()
        logging.info('action: SIGTERM signal received | result: in_progress')
        for protocol in self._active_agencies_connections:
            protocol.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket: {protocol.addr()}')

        
