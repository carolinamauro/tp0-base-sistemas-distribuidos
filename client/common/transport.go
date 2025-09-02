package common

import (
	"net"
)

// Transport struct that encapsulates the connection
type Transport struct{
	conn 	net.Conn
}

// NewTransport Initializes a new Transport receiving the connection
// as a parameter
func NewTransport(conn net.Conn) *Transport {
	return &Transport{
		conn: conn,
	}
}

// SendMessage Sends a message with the given type and content
// Returns an error in case of failure
func (tm *Transport) SendMessage(messageType uint8, message []byte) error {
	totalSize := uint16ToBytes(uint16(len(message)))
	messageToSend := make([]byte, 0, len(message)+SIZE_MESSAGE_TYPE)
	messageToSend = append(messageToSend, messageType)
	messageToSend = append(messageToSend, totalSize...)
	messageToSend = append(messageToSend, message...)
	return tm.SendAll(messageToSend)
}

// SendAll Sends all the bytes of the message
// Returns an error in case of failure
func (tm *Transport) SendAll(message []byte) error {
	totalSent := 0
	messageLength := len(message)
	
	for totalSent < messageLength {
		n, err := tm.conn.Write(message[totalSent:])
		if err != nil {
			return err
		}
		totalSent += n
	}
	return nil
}

// ReceiveAll Receives all the bytes of the message
// Returns an error in case of failure
func (tm *Transport) ReceiveAll() []byte {

	buffer := make([]byte, HEADER_SIZE)

  n, err := tm.conn.Read(buffer)
	if err != nil || n < HEADER_SIZE {
		return nil
	}

	totalSize := int(buffer[1])<<8 | int(buffer[2])
	buffer = append(buffer, make([]byte, totalSize)...)
	totalReceived := 0

	for totalReceived < totalSize {
		n, err := tm.conn.Read(buffer[HEADER_SIZE + totalReceived:])
		if err != nil {
			return nil
		}
		totalReceived += n
	}
	return buffer
}

// Close closes the connection
func (tm *Transport) Close() error {
	return tm.conn.Close()
}
