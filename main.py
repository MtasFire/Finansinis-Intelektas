import os
import sys
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed


class Logger:
    def __init__(self):
        self.terminal = sys.stdout
        self.history = []

    def write(self, message):
        self.terminal.write(message)
        self.history.append(message)

    def flush(self):
        self.terminal.flush()

    def save(self):
        with open("action_history.txt", "w", encoding="utf-8") as file:
            file.write("".join(self.history))
        print("Action history saved to action_history.txt.")


def read(prompt):
    value = input(prompt).strip()
    sys.stdout.history.append(value + "\n")
    return value


def connect_api():
    load_dotenv()
    key = os.getenv("ALPACA_API_KEY")
    secret = os.getenv("ALPACA_SECRET_KEY")

    if not key or not secret:
        raise ValueError("API keys not found.")

    trading = TradingClient(key, secret, paper=True)
    data = StockHistoricalDataClient(key, secret)
    account = trading.get_account()

    print("Successfully connected to Alpaca Paper Trading.")
    print("Status:", account.status, "| Balance:", account.cash, "USD")

    return trading, data


def live_data(data, symbol, interval, updates):
    request = StockLatestTradeRequest(
        symbol_or_symbols=symbol, feed=DataFeed.IEX
    )

    print("IEX data feed - limited US market coverage.")

    try:
        for i in range(updates):
            trade = data.get_stock_latest_trade(request)[symbol]
            age = (datetime.now(timezone.utc) - trade.timestamp).total_seconds()

            print(f"{trade.timestamp} | {symbol} | {trade.price:.2f} USD | Data age: {age:.1f} s")

            if age > 60:
                print("Warning: the latest trade is older than 60 seconds.")

            if i < updates - 1:
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMarket data monitoring stopped.")


def historical_data(data, symbol, days):
    end = datetime.now(timezone.utc)

    request = StockBarsRequest(
        symbol_or_symbols=symbol, timeframe=TimeFrame.Day,
        start=end - timedelta(days=days), end=end, feed=DataFeed.IEX
    )

    bars = data.get_stock_bars(request).df

    if bars.empty:
        print("No historical data found.")
    else:
        print(bars[["open", "high", "low", "close", "volume"]].to_string())


def print_order(order):
    print("-" * 50)
    print(f"Order ID: {order.id}")
    print(f"Client order ID: {order.client_order_id}")
    print(f"Symbol: {order.symbol} | Type: {order.type.value}")
    print(f"Side: {order.side.value} | Quantity: {order.qty}")
    print(f"Status: {order.status.value} | Filled quantity: {order.filled_qty}")
    print(f"Limit price: {order.limit_price}")
    print(f"Average execution price: {order.filled_avg_price}")
    print(f"Submitted at: {order.submitted_at}")


def submit_order(trading, symbol, qty, side, price=None):
    params = dict(
        symbol=symbol, qty=qty, side=side,
        time_in_force=TimeInForce.DAY
    )

    if price is None:
        request = MarketOrderRequest(**params)
    else:
        request = LimitOrderRequest(**params, limit_price=price)

    order = trading.submit_order(order_data=request)

    print("Broker response received:")
    print_order(order)


def cancel_order(trading, order_id):
    trading.cancel_order_by_id(order_id)
    print("Cancellation request submitted.")

    for _ in range(10):
        order = trading.get_order_by_id(order_id)

        if order.status.value in ("canceled", "filled", "expired", "rejected"):
            break

        time.sleep(1)

    print_order(order)

    if order.status.value == "canceled":
        print("Order cancellation confirmed.")
    else:
        print("Order cancellation not confirmed.")


def show_orders(trading, status=QueryOrderStatus.ALL):
    orders = trading.get_orders(
        filter=GetOrdersRequest(status=status, limit=100)
    )

    if not orders:
        print("No orders found.")

    for order in orders:
        print_order(order)


def positive(prompt, number_type=float):
    value = number_type(read(prompt))

    if not 0 < value < float("inf"):
        raise ValueError("Value must be positive and finite.")

    return value


def main():
    logger = Logger()
    sys.stdout = logger

    try:
        trading, data = connect_api()

    except Exception as e:
        print("Connection error:", e)
        return

    while True:
        print("""
===== ALPACA PAPER TRADING =====
1. Account information
2. Real-time market data
3. Historical market data
4. Submit market order
5. Submit limit order
6. Cancel order
7. View all orders
8. View open orders
9. Check specific order status
10. Save action history to TXT
0. Exit program
""")

        choice = read("Select an option: ")

        try:
            if choice == "0":
                print("Program terminated.")
                break

            elif choice == "1":
                account = trading.get_account()
                print("Balance:", account.cash, "USD")
                print("Buying power:", account.buying_power, "USD")
                print("Market open:", trading.get_clock().is_open)

            elif choice in ("2", "3", "4", "5"):
                symbol = read("Stock symbol: ").upper()

                if not symbol:
                    raise ValueError("Stock symbol cannot be empty.")

                if choice == "2":
                    live_data(
                        data, symbol,
                        positive("Update interval (seconds): "),
                        positive("Number of updates: ", int)
                    )

                elif choice == "3":
                    historical_data(
                        data, symbol,
                        positive("Number of days: ", int)
                    )

                else:
                    qty = positive("Number of shares: ", int)
                    side = OrderSide(read("Order side (buy/sell): ").lower())
                    price = positive("Limit price (USD): ") if choice == "5" else None

                    submit_order(trading, symbol, qty, side, price)

            elif choice == "6":
                show_orders(trading, QueryOrderStatus.OPEN)
                cancel_order(trading, read("Order ID: "))

            elif choice == "7":
                show_orders(trading)

            elif choice == "8":
                show_orders(trading, QueryOrderStatus.OPEN)

            elif choice == "9":
                print_order(
                    trading.get_order_by_id(read("Order ID: "))
                )

            elif choice == "10":
                logger.save()

            else:
                print("Invalid option.")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    original_stdout = sys.stdout

    try:
        main()
    finally:
        sys.stdout = original_stdout