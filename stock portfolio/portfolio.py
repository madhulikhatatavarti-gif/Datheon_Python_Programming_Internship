#!/usr/bin/env python3
"""Investment portfolio tracker.

- Enter ticker symbols, buy prices and share quantities.
- Tickers are checked against the S&P 500 dataset (constituents.csv).
- Current prices come from sample_prices.csv (illustrative sample data),
  or live from Yahoo Finance when run with:  python portfolio.py --live
  (requires:  pip install yfinance).
- Shows total invested vs. current market value and the % gain/loss per holding.
- Writes the results to portfolio_summary.csv using the built-in csv module.
"""

import csv
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTITUENTS_FILE = os.path.join(BASE_DIR, "constituents.csv")
PRICES_FILE = os.path.join(BASE_DIR, "sample_prices.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")

USE_LIVE = "--live" in sys.argv


# ----------------------------------------------------------------- data loading
def load_constituents():
    """Return {symbol: (company name, sector)} from the S&P 500 dataset."""
    companies = {}
    try:
        with open(CONSTITUENTS_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                companies[row["Symbol"].upper()] = (row["Security"], row["GICS Sector"])
    except OSError:
        print(f"Note: {CONSTITUENTS_FILE} not found - ticker names will not be checked.")
    return companies


def load_sample_prices():
    """Return {symbol: price} from the sample prices CSV."""
    prices = {}
    try:
        with open(PRICES_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                prices[row["Symbol"].upper()] = float(row["Price"])
    except (OSError, ValueError, KeyError):
        print(f"Note: could not read {PRICES_FILE}.")
    return prices


def get_live_price(ticker):
    """Fetch the latest price with yfinance. Returns None if unavailable."""
    try:
        import yfinance as yf

        history = yf.Ticker(ticker).history(period="1d")
        if not history.empty:
            return float(history["Close"].iloc[-1])
    except Exception:
        pass
    return None


def get_current_price(ticker, sample_prices):
    """Live price (if --live), else sample price, else None."""
    if USE_LIVE:
        price = get_live_price(ticker)
        if price is not None:
            return price
    return sample_prices.get(ticker)


# ------------------------------------------------------------------ user input
def ask_float(prompt):
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("  Please enter a number greater than 0.")


def ask_int(prompt):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("  Please enter a whole number greater than 0.")


def add_position(portfolio, companies, sample_prices):
    ticker = input("\n  Ticker symbol (e.g. AAPL): ").strip().upper()
    if not ticker:
        return
    if companies and ticker not in companies:
        print(f"  '{ticker}' is not in the S&P 500 dataset. Check the symbol and try again.")
        return

    buy_price = ask_float("  Buy price per share ($): ")
    shares = ask_int("  Number of shares: ")

    if ticker in portfolio:
        # Merge with the existing holding using a weighted average buy price.
        old = portfolio[ticker]
        total_shares = old["shares"] + shares
        old["avg_price"] = (old["avg_price"] * old["shares"] + buy_price * shares) / total_shares
        old["shares"] = total_shares
        print(f"  Updated {ticker}: now {total_shares} shares at an average of ${old['avg_price']:,.2f}.")
    else:
        portfolio[ticker] = {"shares": shares, "avg_price": buy_price}
        print(f"  Added {shares} shares of {ticker} at ${buy_price:,.2f}.")

    if get_current_price(ticker, sample_prices) is None:
        print(f"  No price found for {ticker}; you will be asked for its current price when viewing.")


# ----------------------------------------------------------------- calculations
def build_rows(portfolio, companies, sample_prices, manual_prices):
    """Compute one result row per holding, plus the grand totals."""
    rows = []
    for ticker, pos in sorted(portfolio.items()):
        price = get_current_price(ticker, sample_prices)
        if price is None:
            if ticker not in manual_prices:
                manual_prices[ticker] = ask_float(f"  Current price of {ticker} ($): ")
            price = manual_prices[ticker]

        invested = pos["shares"] * pos["avg_price"]
        value = pos["shares"] * price
        gain = value - invested
        gain_pct = gain / invested * 100
        rows.append({
            "ticker": ticker,
            "company": companies.get(ticker, ("", ""))[0],
            "shares": pos["shares"],
            "buy_price": pos["avg_price"],
            "current_price": price,
            "invested": invested,
            "value": value,
            "gain": gain,
            "gain_pct": gain_pct,
        })

    total_invested = sum(r["invested"] for r in rows)
    total_value = sum(r["value"] for r in rows)
    total_gain = total_value - total_invested
    total_pct = (total_gain / total_invested * 100) if total_invested else 0.0
    totals = {"invested": total_invested, "value": total_value,
              "gain": total_gain, "gain_pct": total_pct}
    return rows, totals


# ------------------------------------------------------------------ presenting
def show_summary(rows, totals):
    source = "live Yahoo Finance prices" if USE_LIVE else "sample prices (sample_prices.csv)"
    print("\n" + "=" * 92)
    print(f"  PORTFOLIO SUMMARY   -   {source}")
    print("=" * 92)
    print(f"  {'Ticker':<7}{'Shares':>7}{'Buy $':>11}{'Now $':>11}"
          f"{'Invested $':>14}{'Value $':>14}{'Gain/Loss $':>14}{'Gain %':>9}")
    print("  " + "-" * 88)
    for r in rows:
        print(f"  {r['ticker']:<7}{r['shares']:>7}{r['buy_price']:>11,.2f}{r['current_price']:>11,.2f}"
              f"{r['invested']:>14,.2f}{r['value']:>14,.2f}{r['gain']:>+14,.2f}{r['gain_pct']:>+8.2f}%")
    print("  " + "-" * 88)
    print(f"  {'TOTAL':<7}{'':>7}{'':>11}{'':>11}"
          f"{totals['invested']:>14,.2f}{totals['value']:>14,.2f}"
          f"{totals['gain']:>+14,.2f}{totals['gain_pct']:>+8.2f}%")
    print("=" * 92)
    if not USE_LIVE:
        print("  Note: sample prices are illustrative, not real market data.")
        print("  Run with  python portfolio.py --live  for live prices (needs yfinance).")


def save_summary(rows, totals):
    """Write the summary to portfolio_summary.csv (overwritten each time)."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = ["Timestamp", "Ticker", "Company", "Shares", "Buy Price", "Current Price",
              "Invested", "Market Value", "Gain/Loss", "Gain/Loss %"]
    with open(SUMMARY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r in rows:
            writer.writerow([stamp, r["ticker"], r["company"], r["shares"],
                             f"{r['buy_price']:.2f}", f"{r['current_price']:.2f}",
                             f"{r['invested']:.2f}", f"{r['value']:.2f}",
                             f"{r['gain']:.2f}", f"{r['gain_pct']:.2f}"])
        writer.writerow([stamp, "TOTAL", "", "", "", "",
                         f"{totals['invested']:.2f}", f"{totals['value']:.2f}",
                         f"{totals['gain']:.2f}", f"{totals['gain_pct']:.2f}"])
    print(f"\n  Saved to {SUMMARY_FILE}")


# ------------------------------------------------------------------------ main
def main():
    companies = load_constituents()
    sample_prices = load_sample_prices()
    portfolio = {}      # {ticker: {"shares": int, "avg_price": float}}
    manual_prices = {}  # prices the user typed for tickers with no known price

    print("\n  === INVESTMENT PORTFOLIO TRACKER ===")
    while True:
        print("\n  1) Add a holding")
        print("  2) View portfolio summary")
        print("  3) Save summary to CSV and quit")
        print("  4) Quit without saving")
        choice = input("  Choose 1-4: ").strip()

        if choice == "1":
            add_position(portfolio, companies, sample_prices)
        elif choice == "2":
            if not portfolio:
                print("  Your portfolio is empty. Add a holding first.")
            else:
                rows, totals = build_rows(portfolio, companies, sample_prices, manual_prices)
                show_summary(rows, totals)
        elif choice == "3":
            if not portfolio:
                print("  Your portfolio is empty. Add a holding first.")
                continue
            rows, totals = build_rows(portfolio, companies, sample_prices, manual_prices)
            show_summary(rows, totals)
            save_summary(rows, totals)
            break
        elif choice == "4":
            break
        else:
            print("  Please choose 1, 2, 3 or 4.")
    print("\n  Goodbye!\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Interrupted. Goodbye!\n")
