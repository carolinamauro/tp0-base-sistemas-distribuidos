package common

import (
	"encoding/binary"
)

type LotteryWinners struct {
	Winners []string
}

func NewLotteryWinners(data []byte) *LotteryWinners {
	return &LotteryWinners{
		Winners: make([]string, 0),
	}
}

func (lw *LotteryWinners) Deserialize(data []byte) {
	
	for len(data) > 0 {
		fieldType := data[0]
		totalSize := int(buffer[1])<<8 | int(buffer[2])
		dni := data[2 : 2+fieldLength]
		if fieldType == WINNER_DNI_TYPE {
			lw.Winners = append(lw.Winners, parseToUint16(dni))
		}
		data = data[2+fieldLength:]
	}
}

func (lw *LotteryWinners) GetWinnersAmount() int {
	return len(lw.Winners)
}