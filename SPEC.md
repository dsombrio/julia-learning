# Stock-Crypto Portfolio Matcher

## Project Overview
- **Purpose:** Given a publicly traded stock symbol, calculate the optimal split of MSTR, STRC, STRD, STRK, STRF, and BTC to match that stock's beta and return profile
- **Target Users:** Investors who want crypto exposure that mimics traditional stocks

## Functionality

### Input
- Stock symbol input field (e.g., AAPL, NVDA, TSLA)
- "Calculate" button

### Data Fetching
- Stock data: Use Yahoo Finance API (or Finnhub if available)
- Crypto data: CoinGecko for BTC, MSTR, STRC, STRD, STRK, STRF
- Fetch 30-day and 90-day historical data for beta calculation

### Calculation
1. **Beta Calculation:** Measure stock's volatility relative to BTC
2. **Return Profile:** Compare 30d/90d returns
3. **Optimization:** Find the weighted split across the 6 assets that minimizes tracking error to the input stock

### Output
- Display the calculated split (percentages)
- Show beta and return comparison
- Show the 6 assets with their weights

## Technical Stack
- Single HTML file with embedded CSS/JS
- Use CoinGecko API (free, no key needed for basic use)
- Use Yahoo Finance via proxy or Finnhub for stock data

## Assets to Optimize
| Ticker | Name | Type |
|--------|------|------|
| MSTR | MicroStrategy | Stock |
| STRC | Stratos Resources | Stock |
| STRD | Strate Resources | Stock |
| STRK | Stark Holdings | Stock |
| STRF | Stratos Financial | Stock |
| BTC | Bitcoin | Crypto |

## UI Design
- Clean, modern interface
- Input field prominently displayed
- Results in a clear table format
- Dark mode by default (matching crypto aesthetic)
