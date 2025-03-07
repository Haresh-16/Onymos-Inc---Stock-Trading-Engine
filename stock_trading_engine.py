import threading
import random
import time

MAX_TICKERS = 1024
MAX_ORDERS  = 10000

class AtomicBool:
    def __init__(self, initial_value: bool = False):
        self._value = 1 if initial_value else 0
        self._lock = threading.Lock()
    def load(self):
        with self._lock:
            return self._value
    def compare_exchange_strong(self, expected: int, desired: int) -> bool:
        with self._lock:
            if self._value == expected:
                self._value = desired
                return True
            return False
    def store(self, new_value: bool):
        with self._lock:
            self._value = 1 if new_value else 0

class OrderType:
    BUY = 0
    SELL = 1

def create_order(order_type, ticker, quantity, price):
    return [
        AtomicBool(True),
        order_type,
        ticker,
        quantity,
        price
    ]

class TickerOrderBook:
    def __init__(self):
        self.buy_orders  = [None] * MAX_ORDERS
        self.sell_orders = [None] * MAX_ORDERS
        self.buy_count  = 0
        self.sell_count = 0

class StockEngine:
    def __init__(self):
        self.tickers = [""] * MAX_TICKERS
        self.order_books = [TickerOrderBook() for _ in range(MAX_TICKERS)]
        self.ticker_count = 0
    def get_ticker_index(self, ticker_symbol: str) -> int:
        current_count = self.ticker_count
        for i in range(current_count):
            if self.tickers[i] == ticker_symbol:
                return i
        if current_count < MAX_TICKERS:
            engine_lock.acquire()
            try:
                new_count = self.ticker_count
                for i in range(new_count):
                    if self.tickers[i] == ticker_symbol:
                        engine_lock.release()
                        return i
                if new_count < MAX_TICKERS:
                    self.tickers[new_count] = ticker_symbol
                    self.ticker_count += 1
                    return new_count
                else:
                    return -1
            finally:
                if engine_lock.locked():
                    engine_lock.release()
        return -1

engine = StockEngine()
engine_lock = threading.Lock()

def match_order(ticker_index: int, incoming_type: int, qty_needed: int, price: float):
    if ticker_index < 0:
        return
    book = engine.order_books[ticker_index]
    if incoming_type == OrderType.BUY:
        s_count = book.sell_count
        for i in range(s_count):
            if qty_needed <= 0:
                break
            order_entry = book.sell_orders[i]
            if order_entry is None:
                continue
            active_flag = order_entry[0]
            sell_type   = order_entry[1]
            sell_ticker = order_entry[2]
            sell_qty    = order_entry[3]
            sell_price  = order_entry[4]
            if active_flag.load() == 1 and sell_type == OrderType.SELL:
                if sell_price <= price:
                    if active_flag.compare_exchange_strong(1, 0):
                        matched_qty = sell_qty if sell_qty <= qty_needed else qty_needed
                        print(f"TRADE: BUY matched SELL at {sell_price:.2f} for quantity={matched_qty}")
                        qty_needed -= matched_qty
    else:
        b_count = book.buy_count
        for i in range(b_count):
            if qty_needed <= 0:
                break
            order_entry = book.buy_orders[i]
            if order_entry is None:
                continue
            active_flag = order_entry[0]
            buy_type    = order_entry[1]
            buy_ticker  = order_entry[2]
            buy_qty     = order_entry[3]
            buy_price   = order_entry[4]
            if active_flag.load() == 1 and buy_type == OrderType.BUY:
                if buy_price >= price:
                    if active_flag.compare_exchange_strong(1, 0):
                        matched_qty = buy_qty if buy_qty <= qty_needed else qty_needed
                        print(f"TRADE: SELL matched BUY at {buy_price:.2f} for quantity={matched_qty}")
                        qty_needed -= matched_qty

def add_order(order_type: int, ticker_symbol: str, quantity: int, price: float):
    idx = engine.get_ticker_index(ticker_symbol)
    if idx < 0:
        print(f"Failed to add order for ticker={ticker_symbol}. Ticker limit reached.")
        return
    book = engine.order_books[idx]
    new_order = create_order(order_type, ticker_symbol, quantity, price)
    if order_type == OrderType.BUY:
        position = book.buy_count
        if position >= MAX_ORDERS:
            print(f"Out of BUY slots for {ticker_symbol}")
            return
        book.buy_orders[position] = new_order
        book.buy_count += 1
    else:
        position = book.sell_count
        if position >= MAX_ORDERS:
            print(f"Out of SELL slots for {ticker_symbol}")
            return
        book.sell_orders[position] = new_order
        book.sell_count += 1
    match_order(idx, order_type, quantity, price)

def simulate_random_orders(num_orders: int):
    sample_tickers = [
        "AAPL", "AMZN", "MSFT", "GOOG", "TSLA",
        "NVDA", "META", "DIS",  "NFLX", "INTC"
    ]
    num_sample = len(sample_tickers)
    for _ in range(num_orders):
        order_type = OrderType.BUY if (random.randint(0,1) == 0) else OrderType.SELL
        ticker = sample_tickers[random.randint(0, num_sample-1)]
        quantity = random.randint(1, 100)
        price = float(random.randint(1, 1000))
        add_order(order_type, ticker, quantity, price)

if __name__ == "__main__":
    random.seed(int(time.time()))
    simulate_random_orders(20)
