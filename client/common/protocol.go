package common

import (
	"net"
)

// Protocol struct that encapsulates the connection
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
func (protocol *Protocol) ReceiveAll(buffer []byte) error {
	totalReceived := 0
	bufferLength := len(buffer)

	for totalReceived < bufferLength {
		n, err := protocol.conn.Read(buffer[totalReceived:])
		if err != nil {
			return err
		}
		totalReceived += n
	}
	return nil
}

// Close closes the connection
func (protocol *Protocol) Close() error {
	return protocol.conn.Close()
}
