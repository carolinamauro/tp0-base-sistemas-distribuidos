package common

import (
	"net"
)

type Transport struct{
	conn 	net.Conn
}

func NewTransport(conn net.Conn) *Transport {
	return &Transport{
		conn: conn,
	}
}

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

func (tm *Transport) ReceiveAll(buffer []byte) error {
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

func (tm *Transport) Close() error {
	return tm.conn.Close()
}
