package common

import (
	"encoding/csv"
	"os"
	"io"
)

// BetReader struct that reads bets from a CSV file and provides them in chunks
type BetReader struct {
	batchMaxAmount 	int
	file 						*os.File
	fileReader    	*csv.Reader
	allBetsRead  		bool
	unsentBet 			*Bet

}

// NewBetReader Initializes a new BetReader with the given batch size and opens the CSV file
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

// getChunk reads bets from the CSV file and returns a serialized chunk of bets
// It reads up to batchMaxAmount bets or until the chunk size limit is reached
// If a bet cannot fit in the current chunk, it is stored for the next call
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

// Close closes the BetReader's file
func (br *BetReader) Close() {
	if br.file == nil {
		return
	}
	if err := br.file.Close(); err != nil {
		log.Errorf("action: close_bet_reader | result: fail | error: %v", err)
	} else {
		log.Infof("action: close_bet_reader | result: success")
	}
}