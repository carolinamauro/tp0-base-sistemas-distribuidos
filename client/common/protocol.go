package common

import (
	"net"
)

// Transport struct that encapsulates the connection
type Protocol struct{
	conn 	net.Conn
}

// NewProtocol Initializes a new Protocol receiving the connection
// as a parameter
func NewProtocol(conn net.Conn) *Protocol {
	return &Protocol{
		conn: conn,
	}
}

// SendMessage Sends a message with the given type and content
// Returns an error in case of failure
func (protocol *Protocol) SendMessage(messageType uint8, message []byte) error {
	totalSize := uint16ToBytes(uint16(len(message)))
	messageToSend := make([]byte, 0, len(message)+SIZE_MESSAGE_TYPE)
	messageToSend = append(messageToSend, messageType)
	messageToSend = append(messageToSend, totalSize...)
	messageToSend = append(messageToSend, message...)
	return protocol.SendAll(messageToSend)
}

// SendAll Sends all the bytes of the message
// Returns an error in case of failure
func (protocol *Protocol) SendAll(message []byte) error {
	totalSent := 0
	messageLength := len(message)
	
	for totalSent < messageLength {
		n, err := protocol.conn.Write(message[totalSent:])
		if err != nil {
			return err
		}
		totalSent += n
	}
	return nil
}

// ReceiveAll Receives all the bytes of the message
// Returns an error in case of failure
func (protocol *Protocol) ReceiveAll() []byte {

	buffer := make([]byte, HEADER_SIZE)

  n, err := protocol.conn.Read(buffer)
	if err != nil || n < HEADER_SIZE {
		return nil
	}

	totalSize := int(buffer[1])<<8 | int(buffer[2])
	buffer = append(buffer, make([]byte, totalSize)...)
	totalReceived := 0

	for totalReceived < totalSize {
		n, err := protocol.conn.Read(buffer[HEADER_SIZE + totalReceived:])
		if err != nil {
			return nil
		}
		totalReceived += n
	}
	return buffer
}

// SendEndOfChunks Sends an end of chunks message to the server
func (protocol *Protocol) SendEndOfChunks(agencyId string) {
	if err := protocol.SendMessage(MESSAGE_TYPE_END_OF_CHUNKS, nil); err != nil {
    log.Criticalf("action: end_of_chunks | result: fail | agency_id: %v | error: %v", agencyId, err)
	}
}

// Close closes the connection
func (protocol *Protocol) Close() error {
	return protocol.conn.Close()
}
