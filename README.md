# Stock Matching Engine

This repository provides a **simplified** stock matching engine in Python, illustrating:

- **Atomic-like toggling** to simulate lock-free concepts (using `AtomicBool`).
- **Array-based** storage of orders, with separate **Buy** and **Sell** lists.
- Support for **up to 1024** distinct ticker symbols (no dictionaries or maps).
- A single-pass matching strategy (\(O(n)\)) to find and execute trades.

> **Note**: Python’s GIL prevents true lock-free concurrency at the hardware level. This project simply demonstrates the *concept* of atomic operations and a straightforward order-matching approach.

---

## Features

1. **Array-Only Ticker Management**  
   - Ticker symbols are stored in a fixed array.  
   - A simple function `get_ticker_index` finds or creates a ticker index.

2. **Array-Only Order Storage**  
   - Each ticker has **two arrays**: `buy_orders` and `sell_orders`.  
   - Each array can hold **up to 10,000** orders.  
   - Orders are simple lists `[AtomicBool, order_type, ticker, quantity, price]`.

3. **Order Matching**  
   - When a new order is added, the engine scans the *opposite* list in one pass:
     - **Buy** scans **Sell** for prices `<=` the buy price.  
     - **Sell** scans **Buy** for prices `>=` the sell price.  
   - A match uses **compare-and-swap** on the `AtomicBool` to mark an order as *taken*, preventing double fills.

4. **Concurrency Concept**  
   - An `AtomicBool` class simulates compare_exchange_strong logic.  
   - A global lock (`engine_lock`) is used for managing the ticker index array.  
   - In a real system, you would use hardware-level atomics and more advanced concurrency controls.

5. **Random Simulation**  
   - The function `simulate_random_orders` generates random Buy or Sell orders for random tickers, quantities, and prices.

---

## Getting Started

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Haresh-16/Onymos-Inc---Stock-Trading-Engine.git
   cd stock-matching-engine
   ```

2. **Run the Script**

   ```bash
   python stock_matching.py
   ```
   This will generate random orders and print any resulting trades to your console.

---

## Example Output

A short snippet of console output might look like:

```
TRADE: BUY matched SELL at 150.00 for quantity=10
TRADE: SELL matched BUY at 300.00 for quantity=5
```

Each line shows a successfully matched trade, the matched price, and quantity.

---

## How It Works

1. **Adding an Order**  
   - Call `add_order(order_type, ticker, quantity, price)`.  
   - The engine locates the ticker slot (or creates one), appends the order to the correct array (buy/sell), and then tries to match it immediately in one pass.

2. **Matching**  
   - The new order is compared against existing orders in the opposite array.  
   - Prices are checked (`buy_price >= sell_price` or vice versa).  
   - If a match is possible, an **atomic compare-and-swap** attempts to inactivate the matched order so only one thread can claim it.  
   - Any successful match logs a “TRADE” message.

3. **Concurrency & Lock-Free Concept**  
   - **`AtomicBool`** simulates an atomic variable:  
     - `compare_exchange_strong(expected, desired)` tries to set the active status from `expected` to `desired`. 

---
