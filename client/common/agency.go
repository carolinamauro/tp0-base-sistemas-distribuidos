package common

import (
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"
	"github.com/op/go-logging"
	"strconv"
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

	betReader := NewBetReader(a.config.BatchMaxAmount)

	a.createAgencySocket()
	
	while a.running && !betReader.allBetsRead {
		betChunk := betReader.getChunk()

		if err := a.transport.SendAll(betChunk); err != nil {
			log.Criticalf("action: send_chunk | result: fail | agency_id: %v | error: %v",
				a.config.ID,
				err,
			)
			a.CloseConnection()
			return
		}

		ackMessage := make([]byte, SIZE_ACK_MESSAGE)
		if err := a.transport.ReceiveAll(ackMessage); err != nil {
			log.Criticalf("action: recv_ack | result: fail | agency_id: %v | error: %v",
				a.config.ID, err)
			return
		}

		if len(ackMessage) > 0 && ackMessage[0] == MESSAGE_TYPE_ACK && ackMessage[3] == ACK_OK {
			log.Infof("action: apuesta_enviada | result: success | agency_id: %v",
				a.config.ID, 
			)
		}
		time.Sleep(a.config.LoopPeriod)
	}

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
