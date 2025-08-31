package common

import (
	"encoding/csv"
	"os"
	"io"
)

type BetReader struct {
	batchMaxAMount 	int
	file 						*os.File
	fileReader    	*csv.Reader
	allBetsRead  		bool

}

func NewBetReader(batchMaxAMount int) *BetReader {
	file, err := os.Open(BETS_FILE_PATH)
	if err != nil {
		return nil
	}
	return &BetReader{
		batchMaxAMount: batchAMaxMount,
		file:          file,
		fileReader:    csv.NewReader(file),
		allBetsRead:   false,
	}
}

func (br *BetReader) getChunk(agencyId uint32) []byte {
	var chunk []byte
	var betsInChunk [][]string
	betsRead := 0

	while betsRead < br.batchMaxAMount && !br.allBetsRead {
		record, err := br.fileReader.Read()
		if err == io.EOF {
			br.allBetsRead = true
			break
		}
		if err != nil {
			continue
		}
		bet := NewBet(parseAgencyId(record[0]), parseBetNumber(record[1]), record[2], record[3], record[4], record[5])
	}
}