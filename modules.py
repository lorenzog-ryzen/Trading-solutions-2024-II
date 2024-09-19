from datetime import datetime
import pytz
class Archive_line:
    def __init__(self, array):
       self.date = array[0]
       self.time = array[1]
       self.bid = array[2]
       self.volume_bid = array[3]
       self.ask = array[4]
       self.volume_ask = array[5]
       #self.instrument =  array[6]
       
def p_calculator(wins,delta=40):
    return wins/delta
       
def balance_risk_calculator(wins):
    return (461)/(7*(2*p_calculator(wins)-1))      
         
def units_calculator(wins, geom_risk = 5):
    return balance_risk_calculator(wins)//geom_risk

def time_detector_long(*, ET_time, current_state):
    return 'long'
    if ET_time[3:] == '55': # and  
        return 'sell'
    elif ET_time[3:] == '00':
        return 'buy'
    
def time_detector_short(*, ET_time, current_state):
    return 'short'
    if ET_time[3:] == '00': # and 
        return 'sell_short'
    elif ET_time[3:] == '55':
        return 'buy_to_cover'
def search_ET_time():
    utc_now = datetime.now(pytz.utc)
    est = pytz.timezone('US/Eastern')
    est_time = utc_now.astimezone(est)
    current_ET_time = str(est_time.strftime('%Y-%m-%d %H:%M:%S'))[11:]
    return current_ET_time

def broker_requester(instrument, side, number_units, limit_price) -> bool:
    return True

class Trade_Station:
    def __init__(self) -> None:
        pass
    def place_order(self, side, number_units, instrument = 'SYP', limit_price = 0) -> bool:
        return broker_requester(instrument, side, number_units, limit_price) 
    
    