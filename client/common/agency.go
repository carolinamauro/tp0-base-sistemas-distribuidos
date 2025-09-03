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
	protocol   				 	*Protocol
	running           	bool
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
	
	// Crear socket
  if err := a.createAgencySocket(); err != nil {
      log.Criticalf("action: create_socket | result: fail | agency_id: %v | error: %v", a.config.ID, err)
      betReader.Close()
      signal.Stop(signalChannel)
      return
  }

	if err := a.sendAgencyID(); err != nil {
		betReader.Close()
		signal.Stop(signalChannel)
		a.CloseConnection()
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

	// Wait for lottery results

	betReader.Close()
	a.getLotteryResult()
	a.CloseConnection()
	signal.Stop(signalChannel)
}

// CloseConnection closes the Agency connection gracefully
func (a *Agency) CloseConnection() {
	a.running = false
	if a.protocol != nil {
		a.protocol.Close()
		log.Infof("action: close_connection | result: success | agency_id: %v", a.config.ID)
	}
}

// recvAck receives the ACK message from the server
// and logs the result
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
	return ackMessage
}

func (a *Agency) getLotteryResult() {

	lotteryMessage := a.protocol.ReceiveAll()
	if lotteryMessage == nil {
		log.Criticalf("action: recv_lottery | result: fail | agency_id: %v",
			a.config.ID)
		a.CloseConnection()
		return
	}

	if len(lotteryMessage) > 0 && lotteryMessage[0] == MESSAGE_TYPE_LOTTERY_RESULT { 
		lotteryWinners := NewLotteryWinners()
		lotteryWinners.Deserialize(lotteryMessage[3:])
		log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", lotteryWinners.GetWinnersAmount())
	}
}

func (a *Agency) sendAgencyID() error {
	agencyIDBytes := []byte(a.config.ID)
	if err := a.protocol.SendMessage(MESSAGE_TYPE_AGENCY_ID, agencyIDBytes); err != nil {
		log.Criticalf("action: send_agency_id | result: fail | agency_id: %v | error: %v",
			a.config.ID,
			err,
		)
		return err
	}
	return nil
}

