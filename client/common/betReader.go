package common

import (
	"encoding/csv"
	"os"
	"io"
	"strconv"
)

type BetReader struct {
	batchMaxAmount 	int
	file 						*os.File
	fileReader    	*csv.Reader
	allBetsRead  		bool
	unsentBet 			*Bet

}

func NewBetReader(batchMaxAmount int) *BetReader {
	file, err := os.Open(BETS_FILE_PATH)
	if err != nil {
		return nil
	}
	return &BetReader{
		batchMaxAmount: batchMaxAmount,
		file:          file,
		fileReader:    csv.NewReader(file),
		allBetsRead:   false,
	}
}

func parseToUint16(value string) uint16 {
	parsedValue, err := strconv.ParseUint(value, 10, 16)
	if err != nil {
		return 0
	}
	return uint16(parsedValue)
}

func (br *BetReader) getChunk(agencyId string) []byte {
	var chunk []byte
	betsRead := 0

	if br.unsentBet != nil {
		serializedBet := br.unsentBet.Serialize()
		chunk = append(chunk, serializedBet...)
		br.unsentBet = nil
		betsRead++
	}

	for betsRead < br.batchMaxAmount && !br.allBetsRead {
		record, err := br.fileReader.Read()
		if err == io.EOF {
			br.allBetsRead = true
			break
		}
		if err != nil {
			continue
		}
		bet := NewBet(parseToUint16(agencyId), parseToUint16(record[4]), record[0], record[1], record[2], record[3])
		serializedBet := bet.Serialize()
		if len(chunk)+len(serializedBet) > MAX_CHUNK_SIZE - HEADER_SIZE {
			br.unsentBet = bet
			break
		}
		chunk = append(chunk, bet.Serialize()...)
		betsRead++
	}

	return chunk
}