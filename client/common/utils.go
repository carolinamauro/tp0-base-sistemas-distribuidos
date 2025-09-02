package common

import (
	"encoding/binary"
	"strconv"
)
// uint16ToBytes converts a uint16 to a byte slice in big-endian order
func uint16ToBytes(num uint16) []byte {
	bytes := make([]byte, SIZE_UINT16)
	binary.BigEndian.PutUint16(bytes, num)
	return bytes
}

// parseToUint16 safely parses a string to uint16, returning 0 on error
func parseToUint16(value string) uint16 {
	parsedValue, err := strconv.ParseUint(value, 10, 16)
	if err != nil {
		return 0
	}
	return uint16(parsedValue)
}
