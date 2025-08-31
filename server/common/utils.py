import csv
import datetime
import time


""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574

AGENCY_ID_TYPE        = 0x10
CLIENT_NAME_TYPE      = 0x11
CLIENT_SURNAME_TYPE   = 0x12
CLIENT_DNI_TYPE       = 0x13
CLIENT_BIRTHDATE_TYPE = 0x14
BET_NUMBER_TYPE       = 0x15


""" A lottery bet registry. """
class Bet:
    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        self.agency = int(agency)
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = datetime.date.fromisoformat(birthdate)
        self.number = int(number)
        
    def deserialize(bytes: str):
        n = 0
        bet = {}
        while n < len(bytes):
            t = bytes[n]
            l = bytes[n+1]
            v = bytes[n+2:n+2+l]
            n += 2 + l
            
            if t == AGENCY_ID_TYPE:
                bet["agency"] = int.from_bytes(v, byteorder='big')
            elif t == CLIENT_NAME_TYPE:
                bet["first_name"] = v.decode('utf-8')
            elif t == CLIENT_SURNAME_TYPE:
                bet["last_name"] = v.decode('utf-8')
            elif t == CLIENT_DNI_TYPE:
                bet["document"] = v.decode('utf-8')
            elif t == CLIENT_BIRTHDATE_TYPE:
                bet["birthdate"] = v.decode('utf-8')
            elif t == BET_NUMBER_TYPE:
                bet["number"] = int.from_bytes(v, byteorder='big')
            else:
                pass
            
        return Bet(bet["agency"], bet["first_name"], bet["last_name"], bet["document"], bet["birthdate"], bet["number"])
        
        

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])

