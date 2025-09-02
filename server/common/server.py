import socket
import logging
import signal
import sys
from common.transport import Transport
from common.utils import store_bets, load_bets, has_won

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_agencies_connections = []
        self._listen_backlog = listen_backlog
        self._finished_agencies = 0
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
        
        self._active_agencies_connections.append(transport)
        try:
            self.__recv_bets(transport)
            self._finished_agencies += 1
           
            if self._finished_agencies != self._listen_backlog:
                return
            
            self._send_lottery_result_to_agencies()
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            self.__close_connection(transport)
      
    def __recv_bets(self, transport):
        while True:
            mtype = transport.receive_message_type()
            if mtype is None:
                raise OSError("connection closed by peer")
            if transport.is_chunk_message(mtype):
                try:
                    bets = transport.receive_chunk()
                except Exception as e:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    raise OSError(f"receive_chunk: {e}")

                store_bets(bets)
                logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                try:
                    transport.send_ack()
                    logging.info("action: send_ack | result: success")
                except Exception as e:
                    raise OSError(f"send_ack: {e}")

            elif transport.is_end_of_chunks_message(mtype):
                logging.info(f"action: agency_finished | result: success | agency_id: {transport.agency_id}")
                break
            elif transport.is_agency_id_message(mtype):
                transport.receive_agency_id()
                logging.info("action: receive_agency_id | result: success")
            else:
                raise OSError(f"invalid message type: {mtype}")
    
    def _send_lottery_result_to_agencies(self):
        logging.info("action: sorteo | result: success")
        winners_by_agency = {}
        winners = [bet for bet in load_bets() if has_won(bet)]
        
        for bet in winners:
            if bet.agency not in winners_by_agency:
                winners_by_agency[bet.agency] = []
            winners_by_agency[bet.agency].append(bet)
        
        for transport in self._active_agencies_connections:
            try:
                transport.send_lottery_result(winners_by_agency.get(transport.agency_id, []))
                logging.info(f"action: send_lottery_result | result: success | agency socket: {transport.addr()}")
            except Exception as e:
                logging.error(f"action: send_lottery_result | result: fail | agency socket: {transport.addr()} | error: {e}")
            finally:
                self.__close_connection(transport)
        self._active_agencies_connections = []
        self._finished_agencies = 0
              
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
    
    def __close_connection(self, transport):
        logging.info(f"action: close_agency_connection | result: in_progress | agency socket: {transport.addr()}")
        transport.close()
        self._active_agencies_connections.remove(transport)
    
    def __handle_sigterm_signal(self, signum, frame):
        self._listening = False
        logging.info('action: SIGTERM signal received | result: in_progress')
        for transport in self._active_agencies_connections:
            transport.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket: {transport._agency_socket}')
        socket_addr = self._server_socket.getsockname()[0]
        self._server_socket.close()            
        logging.info(f'action: SIGTERM signal received | result: success | server socket: {socket_addr}')

        
