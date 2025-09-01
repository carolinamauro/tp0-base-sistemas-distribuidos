package common

import (
	"encoding/binary"
)
// uint16ToBytes converts a uint16 to a byte slice in big-endian order
func uint16ToBytes(num uint16) []byte {
	bytes := make([]byte, SIZE_UINT16)
	binary.BigEndian.PutUint16(bytes, num)
	return bytes
}