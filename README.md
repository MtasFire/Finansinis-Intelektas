# Alpaca API Trading Program

## Project Description

This program uses the Alpaca API to retrieve financial
market data, submit trading orders, cancel orders and
monitor their execution status.

The program is written in Python and uses an Alpaca
Paper Trading account. No real money is involved.

## Installation and Setup

1. Install Python.

2. Install the required libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create an Alpaca Paper Trading account.

4. Generate an API key and a secret key.

5. Create a `.env` file in the project directory:

   ```env
   ALPACA_API_KEY=your_api_key
   ALPACA_SECRET_KEY=your_secret_key
   ```

6. Run the program:

   ```bash
   python main.py
   ```

7. Select an option from the program menu.

## Features

- API authentication and connection verification.
- Account information retrieval.
- Real-time market data retrieval.
- Historical market data retrieval.
- Market order submission.
- Limit order submission.
- Order cancellation.
- Order identifiers and status monitoring.
- Action history export to a TXT file.

## Program Menu

| Option | Description |
|--------|-------------|
| 1 | Account information |
| 2 | Real-time market data |
| 3 | Historical market data |
| 4 | Submit market order |
| 5 | Submit limit order |
| 6 | Cancel order |
| 7 | View all orders |
| 8 | View open orders |
| 9 | Check specific order status |
| 10 | Save action history to TXT |
| 0 | Exit program |

## Market Data Limitations

The program uses the IEX market data feed, which
provides limited coverage of the US stock market.

Market data is updated through periodic REST API
requests.

The program displays the age of the latest trade
and provides a warning if it is older than 60 seconds.

The age of the latest trade does not necessarily
represent API latency.

When the market is closed, prices may not update,
and orders may remain pending until the next
eligible trading session.

## Execution Results

Selecting option 10 saves the current session's
actions, user inputs, market data, order statuses
and broker responses to `action_history.txt`.

The file can be used to demonstrate the program's
functionality.

## Security

API credentials are stored separately in the `.env`
file and are not hardcoded into the source code.

The `.env` file is excluded from the Git repository
using `.gitignore`.

## Technologies

- Python
- Alpaca API
- alpaca-py
- pandas
- python-dotenv