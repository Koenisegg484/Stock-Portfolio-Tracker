import os
import csv
import pandas as pd
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
BASE_URL = "https://www.alphavantage.co/query"
STOCK_SYMBOLS = [
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "MA",
    "PYPL",
    "BAC",
    "DIS",
    "NFLX",
    "INTC",
]

realTimeStocksData = "real_time_stock_data.csv"

######################################## PART 1 ########################################
def fetch_real_time_data_all():
    fields = ["symbol", "price", "volume", "timestamp"]

    try:
        with open(realTimeStocksData, mode = "w", newline="") as stocks_file:
            writer = csv.DictWriter(stocks_file, fieldnames=fields)
            writer.writeheader()

            toReturn = []

            for symbol in STOCK_SYMBOLS:
                params = {
                    "function" : "GLOBAL_QUOTE",
                    "symbol" : symbol,
                    "apikey" : API_KEY
                }

                try:
                    response = requests.get(BASE_URL, params=params)
                    data = response.json().get("Global Quote", {})

                    if data:
                        row = {
                            "symbol": data.get("01. symbol", "N/A"),
                            "price": data.get("05. price", "N/A"),
                            "volume": data.get("06. volume", "N/A"),
                            "timestamp": datetime.now()
                        }

                        toReturn.append(row)

                        writer.writerow(row)
                        print("row added")
                except requests.RequestException as e:
                    print(f"Error fetching data for {symbol}: {e}")
                except KeyError as e:
                    print(f"Key error while processing data for {symbol}: {e}")

        print(f"Real time data saved to {realTimeStocksData} file.")

        return toReturn
    except IOError as e:
        print(f"File I/O error: {e}")

# fetch_real_time_data()

def fetch_real_time_data(symbol):
    fields = ["symbol", "price", "volume", "timestamp"]

    try:
        with open(realTimeStocksData, mode = "a", newline="") as stocks_file:
            writer = csv.DictWriter(stocks_file, fieldnames=fields)

            params = {
                "function" : "GLOBAL_QUOTE",
                "symbol" : symbol,
                "apikey" : API_KEY
            }
            try: 
                response = requests.get(BASE_URL, params=params)
                data = response.json().get("Global Quote", {})
                if data:
                    row = {
                        "symbol": data.get("01. symbol", "N/A"),
                        "price": data.get("05. price", "N/A"),
                        "volume": data.get("06. volume", "N/A"),
                        "timestamp": datetime.now()
                    }
                    writer.writerow(row)
                    print("row added")
                    return float(row["price"]), row["volume"]
            except requests.RequestException as e:
                print(f"Error fetching data for {symbol}: {e}")
                return None, None

    except IOError as e:
        print(f"File I/O error: {e}")
        return None, None



def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    else:
        print(f"Folder '{folder_name}' already exists.")


def fetch_historical_data_in_file_all():
    for symbol in STOCK_SYMBOLS:
        params = {
            "function" : "TIME_SERIES_DAILY",
            "symbol" : symbol,
            "apikey" : API_KEY,
            "outputsize" : "compact"
        }

        
        try: 
            response = requests.get(BASE_URL, params=params)
            data = response.json().get("Time Series (Daily)", {})

            if not data:
                    print(f"No historical data received for {symbol}. Skipping.")
                    continue
            try:
                df = pd.DataFrame.from_dict(data=data, orient="index")
                df.columns = ["open", "high", "low", "close", "volume"]
                df.index.name = "date"
                create_folder("historical")

                csv_file = f"historical/{symbol}_historical.csv"
                df.to_csv(csv_file)
                print(f"Historical data for {symbol} saved to {csv_file}")
            
            except Exception as e:
                print(f"Error processing data for {symbol}: {e}")
        
        except requests.RequestException as e:
            print(f"Error fetching historical data for {symbol}: {e}")


# fetch_historical_data_in_file_all()



def fetch_historical_data_in_file(symbol):
    params = {
        "function" : "TIME_SERIES_DAILY",
        "symbol" : symbol,
        "apikey" : API_KEY,
        "outputsize" : "compact"
    }

    try:
            
        response = requests.get(BASE_URL, params=params)
        data = response.json().get("Time Series (Daily)", {})

        if not data:
            print(f"No historical data received for {symbol}.")
            return
        
        try :
            df = pd.DataFrame.from_dict(data=data, orient="index")
            df.columns = ["open", "high", "low", "close", "volume"]
            df.index.name = "date"
            create_folder("historical")

            symbol_file = f"historical/{symbol}_historical.csv"
            df.to_csv(symbol_file)
            print(f"Historical data for {symbol} saved to {symbol_file}")
        
        except Exception as e:
            print(f"Error processing data for {symbol}: {e}")
    
    except requests.RequestException as e:
        print(f"Error fetching historical data for {symbol}: {e}")



######################################## PART 2 ########################################
PORTFOLIO = {}

def create_portfolio():
    PORTFOLIO["name"] = input("Enter your name: ")
    n = int(input("Enter the number of stocks you own: "))
    if n < 0:
        raise ValueError("The number of stocks cannot be negative.")
    
    PORTFOLIO["stocks"] = []
    for i in range(n):
        stock = input("Enter the symbol of stock: ").strip()
        n_stocks = int(input(f"Enter the number of shares you own of {stock}: "))
        if n_stocks < 0:
            raise ValueError("The number of shares cannot be negative.")
        PORTFOLIO["stocks"].append({
            "stock": stock,
            "shares": n_stocks
        })
    print(PORTFOLIO)



def fetch_realtime_data_from_file(symbol):

    try:    
        if not os.path.isfile(realTimeStocksData):
            fetch_real_time_data()
        with open (realTimeStocksData, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[0] == symbol:
                    return float(row[1]), row[2]

        # Returning price and volume values
        return fetch_real_time_data(symbol=symbol)
    except FileNotFoundError:
        print(f"Error: Real-time data file '{realTimeStocksData}' not found.")
        return None, None
    except ValueError as ve:
        print(f"Error parsing real-time data for {symbol}: {ve}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred while fetching real-time data: {e}")
        return None, None




def fetch_historical_data_from_file(symbol):

    try:

        symbol_historical_file = f"historical/{symbol}_historical.csv"
        if not os.path.isfile(symbol_historical_file):
            fetch_historical_data_in_file(symbol)
        
        with open(symbol_historical_file, mode="r") as file:
            reader = csv.reader(file)
            next(reader)

            data = list(reader)
            last_day = data[-1]
            
            # Returning open and close values
            return float(last_day[1]), float(last_day[4])
    
    except FileNotFoundError:
        print(f"Error: Historical data file for {symbol} not found.")
        return None, None
    except ValueError as ve:
        print(f"Error parsing historical data for {symbol}: {ve}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred while fetching historical data: {e}")
        return None, None



def calculate_portfolio_value():
    try:
        total_value = 0
        for item in PORTFOLIO["stocks"]:
            price, _ = fetch_realtime_data_from_file(item["stock"])
            if price is None:
                print(f"Skipping stock {item['stock']} due to data error.")
                continue
            total_value += price * item["shares"]
        
        return total_value
    except Exception as e:
        print(f"An unexpected error occurred while calculating portfolio value: {e}")
        return 0


def calculate_performance():

    try:    
        current_value = calculate_portfolio_value()
        initial_value = 0
        gains = {}

        for item in PORTFOLIO["stocks"]:
            st = item["stock"]
            sh = item["shares"]
            
            initial_price, _ = fetch_historical_data_from_file(symbol=st)
            initial_value += initial_price * sh
            price, _ = fetch_realtime_data_from_file(st)


            gain_loss = ((price - initial_price) / initial_price) * 100
            gains[st] = gain_loss
        
        portfolio_gain_loss = ((current_value - initial_value) / initial_value) * 100
        return current_value, initial_value, portfolio_gain_loss, gains
    
    except ZeroDivisionError:
        print("Error: Initial portfolio value is zero. Cannot calculate performance.")
        return 0, 0, 0, {}
    except Exception as e:
        print(f"An unexpected error occurred while calculating performance: {e}")
        return 0, 0, 0, {}

def display_portfolio_summary():
    try:
        current_value, initial_value, portfolio_gain_loss, gains = calculate_performance()

        print("Portfolio Summary:")
        print(f"Initial Portfolio Value: ${initial_value:.2f}")
        print(f"Current Portfolio Value: ${current_value:.2f}")
        print(f"Total Portfolio Gain/Loss: {portfolio_gain_loss:.2f}%")

        print("\nIndividual Stock Performance:")
        for symbol, gain_loss in gains.items():
            print(f"{symbol}: {gain_loss:.2f}%")
    except Exception as e:
        print(f"An unexpected error occurred while displaying portfolio summary: {e}")




######################################## PART 3 ########################################

def get_stock_dataframe(symbol):
    stock_file = f"historical/{symbol}_historical.csv"
    try: 
        if not os.path.isfile(stock_file):
            fetch_historical_data_in_file(symbol=symbol)
        
        df = pd.read_csv(stock_file)
        df["close"] = df["close"].astype(float)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        # print(df)
        # print(df.index)
        return df
    except FileNotFoundError:
        print(f"Error: Historical data file for {symbol} not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: Historical data file for {symbol} is empty.")
    except Exception as e:
        print(f"Error processing data for {symbol}: {e}")
    return None



def calculate_moving_averages(df):
    try:    
        df["MA_5"] = df["close"].rolling(window=5).mean()
        df["MA_20"] = df["close"].rolling(window=20).mean()
    except KeyError as e:
        print(f"Error: Missing required columns in the DataFrame - {e}")
    except Exception as e:
        print(f"Unexpected error while calculating moving averages: {e}")




def generate_trade_signals(df, symbol):
    signals = []
    try:
        for i in range(1, len(df)):
            if df["MA_5"].iloc[i] > df["MA_20"].iloc[i] and df["MA_5"].iloc[i-1] <= df["MA_20"].iloc[i-1]:
                signals.append({
                    "stock" : symbol,
                    "date" : df.index[i],
                    "signal" : "BUY"
                })
            elif df["MA_5"].iloc[i] < df["MA_20"].iloc[i] and df["MA_5"].iloc[i-1] >= df["MA_20"].iloc[i-1]:
                signals.append({
                    "stock" : symbol,
                    "date" : df.index[i],
                    "signal" : "BUY"
                })
    except KeyError as e:
        print(f"Error: Missing required columns in the DataFrame for {symbol} - {e}")
    except Exception as e:
        print(f"Unexpected error generating trade signals for {symbol}: {e}")
    
    return signals



def trade_analyzer(stocks_list):
    all_signals = []

    try:
        for stock in stocks_list:
            print(f"Processing {stock}")
            df = get_stock_dataframe(stock)
            if df is not None:
                calculate_moving_averages(df)
                signals = generate_trade_signals(df, stock)
                all_signals.extend(signals)
            else:
                print(f"failed to fetch data for {stock}.")
    except Exception as e:
        print(f"Unexpected error analyzing trades: {e}")
    return all_signals




def display_signals(signals):
    print("\n\nTrade Signals\n")
    for signal in signals:
        print(f"Stock: {signal['stock']}, Date: {signal['date'].strftime('%Y-%m-%d')}, Signal: {signal['signal']}")




def simulate_trades(signals, df, initial_capital = 10000):
    capital = initial_capital
    portfolio_stocks = PORTFOLIO["stocks"]
    trade_history = []

    for signal in signals:
        try:
            date = signal["date"]
            stock = signal["stock"]
            action = signal["signal"]

            if date not in df.index:
                logging.warning(f"Missing data for date {date} for stock")
                continue

            close_price = df.loc[date, "close"]

            if action == "BUY":
                if capital < close_price:
                    logging.warning(
                        f"Insufficient funds to BUY {stock} on {date}. Capital: {capital}, Price: {close_price}"
                    )
                    continue

                capital -= close_price
                stock_entry = next((item for item in portfolio_stocks if item["stock"] == stock), None)
                if stock_entry:
                    stock_entry["shares"] += 1
                else:
                    portfolio_stocks.append({"stock": stock, "shares": 1})


                trade_history.append({
                    "data" : date,
                    "stock" : stock,
                    "action" : "BUY",
                    "price" : close_price
                })

                logging.info(f"Buy : {stock} at ${close_price:.2f} on {date}. Remaining Capital: ${capital:.2f}")

            elif action == "SELL":
                stock_entry = next((item for item in portfolio_stocks if item["stock"] == stock), None)
                if not stock_entry or stock_entry["shares"] <= 0:
                    logging.warning(f"No holdings to SELL {stock} on {date}.")
                    continue

                capital += close_price
                stock_entry["shares"] -= 1

                if stock_entry["shares"] == 0:
                    portfolio_stocks.remove(stock_entry)

                trade_history.append({
                    "date": date,
                    "stock": stock,
                    "action": "SELL",
                    "price": close_price
                })

                logging.info(f"SELL: {stock} at ${close_price:.2f} on {date}. Remaining Capital: ${capital:.2f}")

        except KeyError as e:
            logging.error(f"Key error processing signal {signal}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during trade simulation: {e}")

        
        portfolio_value = sum(
            df.loc[signals[-1]['date'], "close"] * stock["shares"]
            for stock in portfolio_stocks
            )


    
    return capital, portfolio_value, trade_history



def run_simulator():
    # CREATE PORTFOLIO
    # create_portfolio()
    total_capital = 0
    total_portfolio_value = 0
    full_trade_history = []
    
    signals = trade_analyzer(stock["stock"] for stock in PORTFOLIO.get("stocks", []))
    for item in PORTFOLIO["stocks"]:

        df = get_stock_dataframe(item["stock"])
        
        capital, portfolio_value, trade_history = simulate_trades(signals=signals, df=df, initial_capital=10000)
        total_capital = capital
        total_portfolio_value += portfolio_value
        full_trade_history.extend(trade_history)
    
    logging.info("Simulation completed.")
    logging.info(f"Final Capital: ${total_capital:.2f}, Portfolio Value: ${total_portfolio_value:.2f}")
    print(f"Final Capital: ${total_capital:.2f}")
    print(f"Portfolio Value: ${total_portfolio_value:.2f}")
    print(f"Total Value: ${total_capital + total_portfolio_value:.2f}")
    return total_capital, total_portfolio_value, full_trade_history


# run_simulator()