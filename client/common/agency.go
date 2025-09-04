package common

import (
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// AgencyConfig Configuration used by the agency client
type AgencyConfig struct {
	ID            	string
	ServerAddress 	string
	LoopAmount    	int
	LoopPeriod    	time.Duration
	BatchMaxAmount 	int       
}

// Agency Entity that encapsulates how
type Agency struct {
	config 							AgencyConfig
	protocol   				 *Protocol
}

// NewAgency Initializes a new Agency receiving the configuration
// as a parameter
func NewAgency(config AgencyConfig) *Agency {
	agency := &Agency{
		config: config,
	}
	return agency
}

// CreateAgencySocket Initializes Agency socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (a *Agency) createAgencySocket() error {
	conn, err := net.Dial("tcp", a.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | agency_id: %v | error: %v",
			a.config.ID,
			err,
		)
		return err
	}
	a.protocol = NewProtocol(conn)
	return nil
}

// StartAgencyLoop Send messages to the Agency until some time threshold is met
func (a *Agency) StartAgencyLoop() {
	signalChannel := make(chan os.Signal, 2)
  signal.Notify(signalChannel, syscall.SIGTERM)

  betReader := NewBetReader(a.config.BatchMaxAmount)

	if connError := a.tryConnection(); connError != nil {
		log.Errorf(
		  "action: connect | result: fail | client_id: %v | error: could not establish connection after 3 attempts: %v",
		  a.config.ID, connError,
		)
		return
	}

  loop: for {
      select {
      case <-signalChannel:
          log.Infof("action: SIGTERM signal received | result: in_progress | agency_id: %v", a.config.ID)
          break loop
      default:
          chunk := betReader.getChunk(a.config.ID)
					if betReader.allBetsRead && len(chunk) == 0 {
						a.protocol.SendEndOfChunks(a.config.ID)
						break loop
					}

          if err := a.protocol.SendMessage(MESSAGE_TYPE_CHUNK, chunk); err != nil {
            log.Criticalf("action: send_chunk | result: fail | agency_id: %v | error: %v", a.config.ID, err)
						break loop
					}

          if ackMessage := a.recvAck(); ackMessage == nil {
            log.Criticalf("action: receive_ack | result: fail | agency_id: %v", a.config.ID)
						break loop
          }
      }	
  }

	betReader.Close()
  a.CloseConnection()
  signal.Stop(signalChannel)
		
}

// CloseConnection closes the Agency connection gracefully
func (a *Agency) CloseConnection() {
	if a.protocol != nil {
		a.protocol.Close()
		log.Infof("action: close_connection | result: success | agency_id: %v", a.config.ID)
	}
}

// recvAck receives the ACK message from the server:
// 		* ACK_OK if the chunk was processed successfully
// 		* PROCESS_CHUNK_ERROR if there was an error processing the chunk
// Returns the ackMessage or nil in case of failure.
func (a *Agency) recvAck() []byte {
	ackMessage := a.protocol.ReceiveAll()
	if ackMessage == nil {
		return nil
	}
	if len(ackMessage) > 0 && ackMessage[0] == MESSAGE_TYPE_ACK && ackMessage[3] == ACK_OK { 
		log.Infof("action: apuesta_enviada | result: success | agency_id: %v",
				a.config.ID, 
		)
	}
	if len(ackMessage) > 0 && ackMessage[0] == MESSAGE_TYPE_ACK && ackMessage[3] == PROCESS_CHUNK_ERROR {
		log.Errorf("action: apuesta_enviada | result: fail | agency_id: %v | error: process_chunk_error",
				a.config.ID, 
		)
	}
	
	return ackMessage
}

// tryConnection Tries to connect to the server 3 times before giving up
// and returning the last error encountered
func (a *Agency) tryConnection() error {
	var connError error
	connError = nil
	for tried := 1; tried <= 3; tried++ {
		connError = a.createAgencySocket()
		if connError == nil {
		    break
		}

    log.Criticalf(
      "action: connect | result: retrying | agency_id: %v | attempt: %d | error: %v",
      a.config.ID, tried, connError,
    )

    if tried < 3 {
      time.Sleep(a.config.LoopPeriod)
    }
	}

	return connError
}