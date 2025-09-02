package common

type LotteryWinners struct {
	Winners []string
}

func NewLotteryWinners() *LotteryWinners {
	return &LotteryWinners{
		Winners: make([]string, 0),
	}
}

func (lw *LotteryWinners) Deserialize(data []byte) {
	
	for len(data) > 0 {
		fieldType := data[0]
		fieldLength := int(data[1])<<8 | int(data[2])
		dni := data[3 : 3+fieldLength]
		if fieldType == CLIENT_DNI_TYPE {
			lw.Winners = append(lw.Winners, string(dni))
		}
		data = data[3+fieldLength:]
	}
}

func (lw *LotteryWinners) GetWinnersAmount() int {
	return len(lw.Winners)
}