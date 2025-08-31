package common

import (
	"encoding/binary"
)

const (
	MESSAGE_TYPE_BET uint8 = 0x01
	
	SIZE_MESSAGE_TYPE	int = 0x01
	SIZE_SERIALIZED_BET_LENGHT int = 0x02
	SIZE_UINT32 uint8 = 0x04

	AGENCY_ID_TYPE = 0x10
	CLIENT_NAME_TYPE = 0x11
	CLIENT_SURNAME_TYPE = 0x12
	CLIENT_DNI_TYPE = 0x13
	CLIENT_BIRTHDATE_TYPE = 0x14
	BET_NUMBER_TYPE = 0x15
)

type Bet struct {
	agencyId			 			uint32
	number        			uint32    
	clientName    			string 
	clientSurname 			string 
	clientDNI    			  string 
	clientBirthDate     string 
}

func NewBet(agencyId uint32, number uint32, clientName string, clientSurname string, clientDNI string, clientBirthDate string) *Bet {
	return &Bet{
		agencyId:       	agencyId,
		number:       		number,
		clientName:   		clientName,
		clientSurname: 		clientSurname,
		clientDNI:    		clientDNI,
		clientBirthDate:  clientBirthDate,
	}
}

func uint32ToBytes(num uint32) []byte {
	bytes := make([]byte, SIZE_UINT32)
	binary.BigEndian.PutUint32(bytes, num)
	return bytes
}

func uint16ToBytes(num uint16) []byte {
	bytes := make([]byte, 2)
	binary.BigEndian.PutUint16(bytes, num)
	return bytes
}

func addBetField(serializedBet *[]byte, fieldType uint8, fieldValue []byte) {
	*serializedBet = append(*serializedBet, fieldType, uint8(len(fieldValue)))
	*serializedBet = append(*serializedBet, fieldValue...)
}

func (bet *Bet) Serialize() []byte {
	var serializedBet []byte

	addBetField(&serializedBet, AGENCY_ID_TYPE, uint32ToBytes(bet.agencyId))
	addBetField(&serializedBet, CLIENT_NAME_TYPE, []byte(bet.clientName))
	addBetField(&serializedBet, CLIENT_SURNAME_TYPE, []byte(bet.clientSurname))
	addBetField(&serializedBet, CLIENT_DNI_TYPE, []byte(bet.clientDNI))
	addBetField(&serializedBet, CLIENT_BIRTHDATE_TYPE, []byte(bet.clientBirthDate))
	addBetField(&serializedBet, BET_NUMBER_TYPE, uint32ToBytes(bet.number))

	totalSize := uint16ToBytes(uint16(len(serializedBet)))
	messageToSend := make([]byte, 0, SIZE_MESSAGE_TYPE+SIZE_SERIALIZED_BET_LENGHT+len(serializedBet))
	messageToSend = append(messageToSend, MESSAGE_TYPE_BET)
	messageToSend = append(messageToSend, totalSize...)
	messageToSend = append(messageToSend, serializedBet...)
	return messageToSend
}