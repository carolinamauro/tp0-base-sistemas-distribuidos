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
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Agency Entity that encapsulates how
type Agency struct {
	config 							AgencyConfig
	protocol   					*Protocol
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
    }()

	bet := getBetFromEnvironment()
	if bet == nil {
		log.Criticalf("action: load_env | result: fail | agency_id: %v", a.config.ID)
		return
	}

	if connError := a.tryConnection(); connError != nil {
		log.Errorf(
		  "action: connect | result: fail | client_id: %v | error: could not establish connection after 3 attempts: %v",
		  a.config.ID, connError,
		)
		return
	}

	if err := a.sendBet(bet); err != nil {
		log.Criticalf("action: send_bet | result: fail | agency_id: %v | error: %v",
			a.config.ID,
			err,
		)
		a.CloseConnection()
		return
	}

	if err := a.recvAck(bet); err != nil {
		log.Criticalf("action: receive_ack | result: fail | agency_id: %v | error: %v",
			a.config.ID,
			err,
		)
	}

	a.CloseConnection()

}

// CloseConnection closes the Agency connection gracefully
func (a *Agency) CloseConnection() {
	if a.protocol != nil {
		a.protocol.Close()
		log.Infof("action: close_connection | result: success | agency_id: %v", a.config.ID)
	}
}

// sendBet sends the serialized bet to the server
func (a *Agency) sendBet(bet *Bet) error {
	serializedBet := bet.Serialize()
	err := a.protocol.SendAll(serializedBet)
	if err != nil {
		return err
	}
	return nil
}

// recvAck receives the ACK message from the server
// and logs the result
func (a *Agency) recvAck(bet *Bet) error {
	ackMessage := make([]byte, SIZE_ACK_MESSAGE)
	err := a.protocol.ReceiveAll(ackMessage)
	if err != nil {
		return err
	}
	if len(ackMessage) > 0 && ackMessage[0] == MESSAGE_TYPE_ACK && ackMessage[3] == ACK_OK { 
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			bet.clientDNI,
			bet.number,
		)
	}
	return nil
}

// getBetFromEnvironment retrieves bet information from environment variables
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


	bet := NewBet(uint16(agencyIdUint64), uint16(clientBetNumberUint64), clientName, clientSurname, clientDNI, clientBirthDate)
	return bet
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