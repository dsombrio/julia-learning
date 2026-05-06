#!/bin/bash
RESP=$(curl -s -X POST "https://login.microsoftonline.com/3ac44adf-88d3-4ffe-aa18-d7ac71dc866f/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=af03f985-1424-465a-bdbf-0cee6b59743b&client_secret=yx58Q~ztCwAayJ3XO5650qc9N1cNcXmLbSAfTbRl&grant_type=client_credentials&scope=https://graph.microsoft.com/.default")
TOKEN=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "https://graph.microsoft.com/v1.0/users/tradbot@traditionsales.com/sendMail" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "message": {
      "subject": "Daily Brief - May 1, 2026",
      "body": {
        "contentType": "HTML",
        "content": "<html><body style=\"font-family: Arial, sans-serif; line-height: 1.6; max-width: 700px;\"><h2>Daily Brief - Friday, May 1, 2026</h2><hr/><h3>CALENDAR</h3><p><em>No events found in calendar for this week.</em></p><hr/><h3>WEATHER - College Station</h3><p><strong>Now:</strong> 61F, Rain, feels like 61F, 96% humidity<br/><strong>Today:</strong> High 63F / Low 55F, 100% precip<br/><strong>Fri:</strong> High 70F / Low 52F, 15%<br/><strong>Sat:</strong> High 75F / Low 53F, 0%<br/><strong>Sun:</strong> High 81F / Low 56F, 1%<br/><strong>Mon:</strong> High 86F / Low 66F, 7%</p><hr/><h3>MARKET</h3><p><strong>Crypto:</strong> BTC $77,240 (CoinGecko). Finnhub unavailable.</p><hr/><h3>POLITICS</h3><ul><li><strong>TX Senate Primary:</strong> Cornyn vs. Paxton — uncalled by AP. <a href=\"https://www.nytimes.com/interactive/2026/us/elections/results-texas-us-senate-primary.html\">NYT</a></li><li><strong>TX House Runoffs:</strong> May 26 for races w/o 50% winner in March primary. <a href=\"https://en.wikipedia.org/wiki/2026_United_States_House_of_Representatives_elections_in_Texas\">Wiki</a></li><li><strong>TX Senate Gen:</strong> James Talarico (D) vs. GOP winner in November. <a href=\"https://en.wikipedia.org/wiki/2026_United_States_Senate_election_in_Texas\">Wiki</a></li></ul><hr/><h3>TAIWAN</h3><p>No significant US-impacting news in past 24h.</p><hr/><h3>CONSTRUCTION</h3><p>No new significant news in TX/OK/LA/MS.</p><hr/><h3>SPORTS</h3><p><strong>TX A&M:</strong> Ranked #8 CBS post-spring. LB Sanford (star) out with lower-leg injury. <a href=\"https://aggieswire-eu.usatoday.com/story/sports/college/aggies/football/2026/04/30/texas-aggies-football-cbs-sports-post-spring-rankings/89864920007/\">AggiesWire</a></p><p><strong>Dallas Stars:</strong> 2026 playoffs — 1st round vs. Minnesota Wild. 112 pts, 2nd in Central. <a href=\"https://www.nhl.com/stars/fans/playoffs/\">NHL.com</a></p><p><strong>NY Mets:</strong> Season active — no major news last 24h.</p><hr/><h3>KIDS ACTIVITIES - May 2-4, College Station/Austin</h3><p>No specific event data available. Consider: George Bush Presidential Library, Downtown Bryan, Zilker Park/Austin Childrens Museum.</p><hr/><p style=\"color:#666;font-size:0.85em;\">TradBot | May 1, 2026 6:00 AM CST</p></body></html>"
      },
      "toRecipients": [{"emailAddress": {"address": "david@traditionsales.com"}}]
    }
  }')
echo "HTTP Status: $HTTP_CODE"