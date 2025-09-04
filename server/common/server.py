from queue import Queue
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
        
        self._server_socket.settimeout(0.5) 
        self._threads = Queue()
        self._results_sent = 0
        self._all_results_sent = threading.Event()
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
                self._threads.put(t)
            except socket.timeout:
                if self._all_results_sent.is_set():
                    self.__join_and_reset()
                continue
            except OSError as e:
                if self._listening:
                    logging.error(f"action: accept_connections | result: fail | error: {e}")
                else:
                    logging.info("action: server_shutdown | result: in_progress")
                break   
        
        self.__close_server_socket()
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
                    t = threading.Thread(target=self.__run_lottery, args=())
                    t.start()
                    self._threads.put(t)
            
            self._lottery_done.wait()
            winners = self._winners_by_agency.get(protocol.agency_id, [])
            protocol.send_lottery_result(winners)
            
            with self._state_lock:
                self._results_sent += 1
                if self._results_sent == self._clients_amount:
                    self._all_results_sent.set() 
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
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
        """
        Runs the lottery and stores the winners by agency
        """
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
        
        self.__close_server_socket()
        logging.info(f'action: SIGTERM signal received | result: success | server socket')
        for protocol in self._active_agencies_connections:
            protocol.close()
            logging.info(f'action: SIGTERM signal received | result: success | agency socket')

    def __join_and_reset(self):
        while self._threads.qsize() > 0:
            thread = self._threads.get()
            thread.join()
        logging.info("action: finish_threads | result: success | reason: all_clients_finished")

        with self._state_lock:
            self._finished_agencies = 0
            self._results_sent = 0
            self._lottery_started = False
            self._winners_by_agency = {}
            self._lottery_done.clear()
            self._all_results_sent.clear()

        logging.info("action: round_cleanup | result: success")

