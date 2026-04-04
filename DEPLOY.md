# Deployment Checklist

## Stock-Crypto Portfolio Matcher

### Quick Start (Open Directly)
- [ ] Navigate to `/Users/tradbot/.openclaw/workspace/stock-crypto-matcher.html` in file explorer
- [ ] Double-click to open in browser

### Local Server (Recommended)
```bash
cd /Users/tradbot/.openclaw/workspace
python3 -m http.server 8080
```
Then open http://localhost:8080/stock-crypto-matcher.html

### Features
- Enter any publicly traded stock symbol (AAPL, NVDA, TSLA, etc.)
- Fetches real-time data from Yahoo Finance + CoinGecko
- Calculates optimal split across: MSTR, STRC, STRD, STRK, STRF, BTC
- Shows stock metrics: 30d return, volatility, BTC correlation, effective beta

### Notes
- Uses CoinGecko free API (rate limited)
- Yahoo Finance data via CORS proxy
- Works best on desktop (Chrome/Safari/Firefox)
