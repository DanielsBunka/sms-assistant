import yfinance as yf

def grab_stocks(ticker=None):
      message = "Stock Info: \n \n"

      if ticker:
            ticker_search = ticker.upper()
            portfolio = {ticker_search:ticker_search}
      else:
            portfolio = {
            "S&P 500": "^GSPC",
            "Google": "GOOGL",
            "Apple": "AAPL",
            "Microsoft": "MSFT"
      }

      # Loop through the portfolio      
      try:
            for name, symbol in portfolio.items():
                  stock = yf.Ticker(symbol)
                  # Grab 2 days of trading data - for comparision (need percentages)
                  recent_data = stock.history(period='2d')

                  # Check if we have 2 days of data
                  if len(recent_data) >= 2:
                        previous_close = recent_data['Close'].iloc[0]
                        current_price = recent_data['Close'].iloc[1]

                        # Calculate the percentage
                        percent_change = ((current_price - previous_close) / previous_close) * 100

                        # Set up the emojis and +/- signs
                        sign = "+" if percent_change > 0 else ""
                        emoji = "🟢" if percent_change > 0 else "🔴" if percent_change < 0 else "⚪"

                        message += f"{emoji} {name}: {sign}{percent_change:.2f}% \n\n"
                  else:
                        # If the data is not found or is missing
                        message += f"🔹 {name}: Data Unavailable (Invalid Ticker?) \n\n"

            return message

      except Exception as e:
            print(f"Stock error: {e}")
            return "⚠️ Error: Couldn't fetch the stock market data."