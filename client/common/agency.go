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

const (
	SIZE_ACK_MESSAGE uint32 = 0x04
	ACK_MESSAGE_TYPE uint8 = 0xFF
	ACK_OK uint8 = 0x00
)


// AgencyConfig Configuration used by the agency client
type AgencyConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Agency Entity that encapsulates how
type Agency struct {
	config 							AgencyConfig
	transport   				*Transport
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
func (c *Agency) createAgencySocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | agency_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.transport = NewTransport(conn)
	return nil
}

func (c *Agency) handleSigtermSignal() {
	log.Infof("action: SIGTERM signal received| result: in_progress | agency_id: %v", c.config.ID)
	if c.transport.conn != nil {
		c.transport.Close()
	}
	log.Infof("action: SIGTERM signal received| result: success | agency_id: %v", c.config.ID)
}

// StartAgencyLoop Send messages to the Agency until some time threshold is met
func (c *Agency) StartAgencyLoop() {
	signalChannel := make(chan os.Signal, 2)
    signal.Notify(signalChannel, syscall.SIGTERM)
    go func() {
        <-signalChannel
        c.handleSigtermSignal()
    }()

	bet := getBetFromEnvironment()
	betMessage := bet.Serialize()
	c.createAgencySocket()

	err := c.transport.SendAll(betMessage)
	if err != nil {
		log.Errorf("action: send_bet | result: fail | agency_id: %v | error: %v",
			c.config.ID,
			err,
		)
		c.transport.Close()
	}
	ackMessage := make([]byte, SIZE_ACK_MESSAGE)
	err = c.transport.ReceiveAll(ackMessage)
	if err != nil {
		log.Errorf("action: receive_ack | result: fail | agency_id: %v | error: %v",
			c.config.ID,
			err,
		)
		c.transport.Close()
	}

	if ackMessage[0] == ACK_MESSAGE_TYPE && ackMessage[3] == ACK_OK {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			bet.clientDNI,
			bet.number,
		)
	}

	
	c.transport.Close()
}


func getBetFromEnvironment() *Bet {
	agencyId := os.Getenv("CLI_ID")
	clientName := os.Getenv("NOMBRE")
	clientSurname := os.Getenv("APELLIDO")
	clientDNI := os.Getenv("DNI")
	clientBirthDate := os.Getenv("NACIMIENTO")
	clientBetNumber := os.Getenv("NUMERO")

	agencyIdUint64, err := strconv.ParseUint(agencyId, 10, 32)
	if err != nil {
		log.Criticalf("action: convert_agency_id | result: fail | agency_id: %v | error: %v",
			agencyId, err)
			return nil
	}

	clientBetNumberUint64, err := strconv.ParseUint(clientBetNumber, 10, 32)
	if err != nil {
		log.Criticalf("action: convert_bet_number | result: fail | bet_number: %v | error: %v",
			clientBetNumber, err)
			return nil
	}


	bet := NewBet(uint32(agencyIdUint64), uint32(clientBetNumberUint64), clientName, clientSurname, clientDNI, clientBirthDate)
	return bet
}
