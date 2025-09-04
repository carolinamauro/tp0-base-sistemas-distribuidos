import socket
import logging
import signal
from common.protocol import Protocol
from common.utils import store_bets, load_bets, has_won
import threading

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
        self._lottery_started = False
        self._winners_by_agency = {}
        
        self._lottery_done = threading.Event()
        self._state_lock = threading.Lock()
        self._lock_store_bets = threading.Lock()
        

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
                t = threading.Thread(target=self.__handle_agency_connection, args=(agency_sock,))
                t.start()
            except OSError as e:
                if self._listening:
                    logging.error(f"action: accept_connections | result: fail | error: {e}")
                else:
                    logging.info("action: server_shutdown | result: in_progress")
                break   
        
        self._listening = False
        self._server_socket.close()
        logging.info("action: server_shutdown | result: success")        

    def __handle_agency_connection(self, agency_sock):
        """
        Read message from a specific agency socket and closes the socket

        If a problem arises in the communication with the agency, the
        agency socket will also be closed
        """
        
        protocol = Protocol(agency_sock)
        self._active_agencies_connections.append(protocol)
        try:
            self.__recv_bets(protocol)
            logging.info(f"action: all_bets_received | result: success | agency_id: {protocol.agency_id}")
            with self._state_lock:
                should_start_lottery = False
                self._finished_agencies += 1
                if self._finished_agencies == self._clients_amount and not self._lottery_started:
                    self._lottery_started = True
                    should_start_lottery = True
                if should_start_lottery:
                    threading.Thread(target=self.__run_lottery, daemon=True).start()
            
            self._lottery_done.wait()
            winners = self._winners_by_agency.get(protocol.agency_id, [])
            protocol.send_lottery_result(winners)
            
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            self.__close_connection(protocol)
            
        finally:
            self.__close_connection(protocol)
      
    def __recv_bets(self, protocol):
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
                with self._lock_store_bets:
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
            
    def __run_lottery(self):
        winners_by_agency = {}
        
        winners = [bet for bet in load_bets() if has_won(bet)]
        
        for bet in winners:
            if bet.agency not in winners_by_agency:
                winners_by_agency[bet.agency] = []
            winners_by_agency[bet.agency].append(bet)
        
        with self._state_lock:
            self._winners_by_agency = winners_by_agency
        
        logging.info("action: sorteo | result: success")
        self._lottery_done.set()
              
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
        logging.info(f"action: close_agency_connection | result: in_progress | agency socket: {protocol.addr()}")
        protocol.close()
        self._active_agencies_connections = [t for t in self._active_agencies_connections if t.agency_id != protocol.agency_id]
        self._finished_agencies -= 1
    
    def __handle_sigterm_signal(self, signum, frame):
        self._listening = False
        logging.info('action: SIGTERM signal received | result: in_progress')
        for protocol in self._active_agencies_connections:
            protocol.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket: {protocol._agency_socket}')
        socket_addr = self._server_socket.getsockname()[0]
        self._server_socket.close()            
        logging.info(f'action: SIGTERM signal received | result: success | server socket: {socket_addr}')

        
