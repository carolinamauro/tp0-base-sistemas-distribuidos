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
	transport   				*Transport
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
	a.transport = NewTransport(conn)
	return nil
}

// handleSigtermSignal Handles the SIGTERM signal by closing the connection gracefully
func (a *Agency) handleSigtermSignal() {
	log.Infof("action: SIGTERM signal received | result: in_progress | agency_id: %v", a.config.ID)
	a.CloseConnection()
}

// StartAgencyLoop Send messages to the Agency until some time threshold is met
func (a *Agency) StartAgencyLoop() {
	signalChannel := make(chan os.Signal, 2)
    signal.Notify(signalChannel, syscall.SIGTERM)
    go func() {
        <-signalChannel
        a.handleSigtermSignal()
				close(signalChannel)
    }()

	a.running = true
	betReader := NewBetReader(a.config.BatchMaxAmount)
	a.createAgencySocket()
	
	a.sendAgencyID()

	for a.running && !betReader.allBetsRead {
		betChunk := betReader.getChunk(a.config.ID)
		
		if len(betChunk) == 0 {
			break
		}

		messageType := MESSAGE_TYPE_CHUNK
		if betReader.allBetsRead {
			messageType = MESSAGE_TYPE_LAST_CHUNK
		}

		if err := a.transport.SendMessage(messageType, betChunk); err != nil {
			log.Criticalf("action: send_chunk | result: fail | agency_id: %v | error: %v",
				a.config.ID,
				err,
			)
			a.CloseConnection()
			return
		}

		ackMessage := a.transport.ReceiveAll()
		if ackMessage == nil {
			log.Criticalf("action: recv_ack | result: fail | agency_id: %v",
				a.config.ID)
			a.CloseConnection()
			return
		}

		if len(ackMessage) > 0 && ackMessage[0] == MESSAGE_TYPE_ACK && ackMessage[3] == ACK_OK {
			log.Infof("action: apuesta_enviada | result: success | agency_id: %v",
				a.config.ID, 
			)
		}
		time.Sleep(a.config.LoopPeriod)
	}

	a.getLotteryResult()
	a.CloseConnection()

}

// CloseConnection closes the Agency connection gracefully
func (a *Agency) CloseConnection() {
	a.running = false
	if a.transport != nil {
		a.transport.Close()
		log.Infof("action: close_connection | result: success | agency_id: %v", a.config.ID)
	}
}

func (a *Agency) getLotteryResult() {

	lotteryMessage := a.transport.ReceiveAll()
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
	if err := a.transport.SendMessage(MESSAGE_TYPE_AGENCY_ID, agencyIDBytes); err != nil {
		log.Criticalf("action: send_agency_id | result: fail | agency_id: %v | error: %v",
			a.config.ID,
			err,
		)
		return err
	}
	return nil
}