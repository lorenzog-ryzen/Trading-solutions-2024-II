import pytz
from datetime import datetime, timedelta
import time

class ArchiveLine:
    def __init__(self, array):
        self.date = array[0]
        self.time = array[1]
        self.bid = array[2]
        self.volume_bid = array[3]
        self.ask = array[4]
        self.volume_ask = array[5]

def p_calculator(wins, delta=40):
    return wins / delta

def balance_risk_calculator(wins):
    return (461) / (7 * (2 * p_calculator(wins) - 1))

def units_calculator(wins, geom_risk=5):
    return balance_risk_calculator(wins) // geom_risk

def search_ET_time():
    """Devuelve la hora actual en formato ET (Eastern Time)."""
    utc_now = datetime.now(pytz.utc)
    est = pytz.timezone('US/Eastern')
    est_time = utc_now.astimezone(est)
    return est_time.strftime('%H:%M:%S')  # Devuelve la hora en formato HH:MM:SS

def is_market_open():
    """Verifica si el mercado está abierto (8:30 AM - 4:00 PM UTC)."""
    utc_now = datetime.now(pytz.utc)
    current_hour = utc_now.hour
    current_minute = utc_now.minute
    return True

def load_bid_ask_data(file_path):
    bid_ask_data = []
    with open(file_path, 'r') as file:
        lineas = file.readlines()
        for linea in lineas:
            try:
                # Quitar comillas innecesarias y procesar línea
                linea = linea.strip().replace('"', '')
                items = linea.split(', ')
                bid_ask_dict = {}

                # Procesar clave-valor
                for item in items:
                    if ': ' in item:
                        key, value = item.split(': ', 1)
                        bid_ask_dict[key.strip()] = value.strip()

                # Combinar 'Date', 'Time' y 'Second' para crear un timestamp
                if 'Date' in bid_ask_dict and 'Time' in bid_ask_dict and 'Second' in bid_ask_dict:
                    full_datetime_str = f"{bid_ask_dict['Date']} {bid_ask_dict['Time']}:{bid_ask_dict['Second']}"
                    bid_ask_dict['Date-Time'] = datetime.strptime(full_datetime_str, '%Y.%m.%d %H:%M:%S')
                    bid_ask_data.append(bid_ask_dict)
                else:
                    print(f"Campos 'Date', 'Time' o 'Second' no encontrados en la línea: {linea}")

            except (ValueError, IndexError) as e:
                print(f"Error procesando línea: {linea}, Error: {e}")
                continue

    return bid_ask_data

def find_bid_ask_for_time(current_datetime, bid_ask_data):
    # Recorre los datos en la lista y compara la fecha-hora simulada con la lista cargada, ignorando segundos
    for entry in bid_ask_data:
        bid_ask_time = entry['Date-Time']
        # Comparar fecha completa y minutos, ignorando segundos
        if bid_ask_time.strftime('%Y-%m-%d %H:%M') == current_datetime.strftime('%Y-%m-%d %H:%M'):
            return entry  # Devuelve el primer dato que coincida en la misma hora y minuto
    return None

def log_trade(trade_type, price, units, balance, previous_balance, result, current_time, month):
    global trade_id
    trade_id += 1 
    filename = f"{trade_type}_trades_{month}.txt"
    
    with open(filename, 'a') as file:
        file.write(f"ID: {trade_id}, Time: {current_time}, Type: {trade_type}, Price: {price}, Units: {units}, "
                   f"Previous Balance: {previous_balance}, New Balance: {balance}, Result: {result}\n")

simulated_datetime = datetime.strptime("2024-06-01 03:00:00", "%Y-%m-%d %H:%M:%S")

def get_simulated_datetime():
    global simulated_datetime
    simulated_datetime += timedelta(minutes=1)  # Avanzar un minuto en cada llamada
    return simulated_datetime  # Devolver el objeto datetime

operation_opened = False  # Para controlar si ya se ha abierto una operación en este ciclo de hora

def execute_trades(current_datetime, bid_ask_data, month):
    global operation_opened

    minute = current_datetime.minute
    hour = current_datetime.hour

    if 0 <= minute <= 55:
        if not operation_opened:
            print(f"Operación abierta a las {current_datetime}")
            # Busca los datos correspondientes para la hora simulada
            entry = find_bid_ask_for_time(current_datetime, bid_ask_data)
            if entry:
                ask_price = float(entry['Ask'])  # Precio ASK para operación short
                bid_price = float(entry['Bid'])  # Precio BID para operación long

                # Ejecutar la operación long con el precio BID
                demo_long.execute_long_trade(bid_price, current_datetime.strftime('%Y-%m-%d %H:%M:%S'), month)

                # Ejecutar la operación short con el precio ASK
                demo_short.execute_short_trade(ask_price, current_datetime.strftime('%Y-%m-%d %H:%M:%S'), month)

                operation_opened = True
            else:
                print(f"No se encontraron datos para {current_datetime.strftime('%Y-%m-%d %H:%M')}")

    elif 56 <= minute <= 59:
        if operation_opened:
            print(f"Cerrando operación a las {current_datetime}")
            entry = find_bid_ask_for_time(current_datetime, bid_ask_data)
            if entry:
                ask_price = float(entry['Ask'])  # Precio ASK para operación short
                bid_price = float(entry['Bid'])  # Precio BID para operación long

                # Cerrar la operación long con el precio BID
                demo_long.close_trade(current_datetime.strftime('%Y-%m-%d %H:%M:%S'), bid_price, ask_price, month)

                # Cerrar la operación short con el precio ASK
                demo_short.close_trade(current_datetime.strftime('%Y-%m-%d %H:%M:%S'), bid_price, ask_price, month)

                operation_opened = False
            else:
                print(f"No se encontraron datos para {current_datetime.strftime('%Y-%m-%d %H:%M')}")

class TradeStation:
    def __init__(self, account_name):
        self.account_name = account_name
        self.balance_long = 99465.90000000005
        self.balance_short = 99465.91999999998
        self.initial_balance_long = None
        self.initial_balance_short = None
        self.open_trade = None

    def execute_long_trade(self, bid_price, current_time, month):
        self.initial_balance_long = self.balance_long
        self.balance_long -= bid_price  # Utilizar el precio BID para long
        self.open_trade = ('long', bid_price, current_time)
        result = "trade executed"
        log_trade('long', bid_price, 1, self.balance_long, self.initial_balance_long, result, current_time, month)

    def execute_short_trade(self, ask_price, current_time, month):
        self.initial_balance_short = self.balance_short
        self.balance_short -= ask_price  # Utilizar el precio ASK para short
        self.open_trade = ('short', ask_price, current_time)
        result = "trade executed"
        log_trade('short', ask_price, 1, self.balance_short, self.initial_balance_short, result, current_time, month)

    def close_trade(self, current_time, bid_price, ask_price, month):
        if self.open_trade:
            trade_type, trade_price, trade_time = self.open_trade  # trade_price es el precio de apertura
            previous_balance = self.initial_balance_long if trade_type == 'long' else self.initial_balance_short
            current_balance = self.balance_long if trade_type == 'long' else self.balance_short

            # Usar el precio de cierre correcto según el tipo de operación
            if trade_type == 'long':
                self.balance_long += bid_price  # Aquí se usa el precio de cierre (bid_price)
                current_balance = self.balance_long
                closing_price = bid_price  # Precio de cierre para 'long'
            elif trade_type == 'short':
                self.balance_short += ask_price  # Aquí se usa el precio de cierre (ask_price)
                current_balance = self.balance_short
                closing_price = ask_price  # Precio de cierre para 'short'

            result = "win" if current_balance > previous_balance else "loss"
            log_trade(trade_type, closing_price, 1, current_balance, previous_balance, result, current_time, month)
            self.open_trade = None  # Cerrar la operación

# Inicialización global
trade_id = 390
demo_long = TradeStation('demo Long')
demo_short = TradeStation('demo Short')

# Rutas de archivos por mes
files_by_month = {
    "junio": "/Users/juansebastianquintanacontreras/Desktop/traiding/MONTHS_EDIT/SPY_06_2024_BidAndAsk_Formatted.txt",
}

# Procesar por mes basando la simulación en los datos disponibles
for month, file_path in files_by_month.items():
    if month == "junio":
        simulated_datetime = datetime.strptime("2024-06-01 08:00:00", "%Y-%m-%d %H:%M:%S")
        print(f"Procesando archivo para el mes: {month}")
        bid_ask_data = load_bid_ask_data(file_path)

        # Continuar la simulación mientras haya datos en bid_ask_data
        while bid_ask_data:
            current_datetime = get_simulated_datetime()
            print(f"Fecha y hora simulada: {current_datetime}")

            # Llamar a la función de trades y verificar la respuesta
            try:
                execute_trades(current_datetime, bid_ask_data, month)
            except Exception as e:
                print(f"Error al ejecutar operaciones para {current_datetime}: {e}")

            # Si la fecha simulada ha avanzado más allá del mes actual, romper el bucle
            if current_datetime.month != simulated_datetime.month:
                print(f"Finalizado el procesamiento para el mes: {month}")
                break
