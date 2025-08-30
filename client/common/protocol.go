package common

import (
	"net"
)

type TransportMessage struct{
	conn 	net.Conn
}

func NewTransportMessage(conn net.Conn) *TransportMessage {
	return &TransportMessage{
		conn: conn,
	}
}

func (tm *TransportMessage) SendAll(message []byte) error {
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

func (tm *TransportMessage) ReceiveAll(buffer []byte) error {
	totalReceived := 0
	bufferLength := len(buffer)

	for totalReceived < bufferLength {
		n, err := tm.conn.Read(buffer[totalReceived:])
		if err != nil {
			return err
		}
		totalReceived += n
	}
	return nil
}

func (tm *TransportMessage) Close() error {
	return tm.conn.Close()
}
