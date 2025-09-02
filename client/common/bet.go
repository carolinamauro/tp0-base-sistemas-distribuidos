package common

// Bet struct that encapsulates the bet information
type Bet struct {
	agencyId			 			uint16
	number        			uint16    
	clientName    			string 
	clientSurname 			string 
	clientDNI    			  string 
	clientBirthDate     string 
}

// NewBet Initializes a new Bet with the given parameters
func NewBet(agencyId uint16, number uint16, clientName string, clientSurname string, clientDNI string, clientBirthDate string) *Bet {
	return &Bet{
		agencyId:       	agencyId,
		number:       		number,
		clientName:   		clientName,
		clientSurname: 		clientSurname,
		clientDNI:    		clientDNI,
		clientBirthDate:  clientBirthDate,
	}
}

// addBetField appends a field to the serialized bet byte slice
func addBetField(serializedBet *[]byte, fieldType uint8, fieldValue []byte) {
	*serializedBet = append(*serializedBet, fieldType, uint8(len(fieldValue)))
	*serializedBet = append(*serializedBet, fieldValue...)
}

// Serialize serializes the Bet struct into a byte slice according to the specified format
// The format includes the message type, total size, and each field with its type, length
// and value
func (bet *Bet) Serialize() []byte {
	var serializedBet []byte

	addBetField(&serializedBet, AGENCY_ID_TYPE, uint16ToBytes(bet.agencyId))
	addBetField(&serializedBet, CLIENT_NAME_TYPE, []byte(bet.clientName))
	addBetField(&serializedBet, CLIENT_SURNAME_TYPE, []byte(bet.clientSurname))
	addBetField(&serializedBet, CLIENT_DNI_TYPE, []byte(bet.clientDNI))
	addBetField(&serializedBet, CLIENT_BIRTHDATE_TYPE, []byte(bet.clientBirthDate))
	addBetField(&serializedBet, BET_NUMBER_TYPE, uint16ToBytes(bet.number))

	totalSize := uint16ToBytes(uint16(len(serializedBet)))
	messageToSend := make([]byte, 0, SIZE_MESSAGE_TYPE+SIZE_UINT16+len(serializedBet))
	messageToSend = append(messageToSend, MESSAGE_TYPE_BET)
	messageToSend = append(messageToSend, totalSize...)
	messageToSend = append(messageToSend, serializedBet...)
	return messageToSend
}