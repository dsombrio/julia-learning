const BLOCKCHAIR_API_KEY = process.env.BLOCKCHAIR_API_KEY || '';
const FINNHUB_KEY = 'd6f31jhr01qvn4o1lap0d6f31jhr01qvn4o1lapg';

// Accumulator stocks to track
const ACCUMULATORS = ['MSTR', 'GIGA', 'ETC', 'HUT', 'CLBT', 'BTG'];

async function getBitcoinPrice() {
  const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd');
  const data = await response.json();
  return data.bitcoin?.usd || 0;
}

async function getLargeTransactions() {
  // Get recent large Bitcoin transactions from Blockchair
  if (!BLOCKCHAIR_API_KEY) {
    return { error: 'No Blockchair API key configured' };
  }
  
  try {
    const response = await fetch(
      `https://api.blockchair.com/bitcoin/outputs?q=is_spent:0,amount:100000000-(${new Date().getTime() / 1000 - 86400 * 7}),recipient:legacy&limit=10`,
      {
        headers: {
          'Authorization': `Bearer ${BLOCKCHAIR_API_KEY}`
        }
      }
    );
    const data = await response.json();
    return data;
  } catch (e) {
    return { error: e.message };
  }
}

async function getAccumulatorStockData() {
  const results = {};
  
  for (const symbol of ACCUMULATORS) {
    try {
      const response = await fetch(
        `https://finnhub.io/api/v1/quote?symbol=${symbol}&token=${FINNHUB_KEY}`
      );
      const quote = await response.json();
      results[symbol] = {
        price: quote.c || 0,
        change: quote.dp || 0,
        high: quote.h || 0,
        low: quote.l || 0
      };
    } catch (e) {
      results[symbol] = { error: e.message };
    }
  }
  
  return results;
}

async function analyzeAccumulation() {
  const btcPrice = await getBitcoinPrice();
  const stocks = await getAccumulatorStockData();
  
  const analysis = {
    btcPrice,
    timestamp: new Date().toISOString(),
    accumulators: {},
    signals: []
  };
  
  // Analyze each accumulator
  for (const [symbol, data] of Object.entries(stocks)) {
    if (data.error) continue;
    
    const premium = btcPrice > 0 ? ((data.price / btcPrice - 1) * 100) : 0;
    
    analysis.accumulators[symbol] = {
      price: data.price,
      dailyChange: data.change.toFixed(2) + '%',
      premiumToBTC: premium.toFixed(2) + '%'
    };
    
    // Generate signals based on movements
    if (data.change > 5) {
      analysis.signals.push({
        type: 'STRONG_UP',
        symbol,
        message: `${symbol} up ${data.change.toFixed(1)}% today. Premium to BTC: ${premium.toFixed(1)}%`
      });
    } else if (data.change < -5) {
      analysis.signals.push({
        type: 'STRONG_DOWN',
        symbol,
        message: `${symbol} down ${Math.abs(data.change).toFixed(1)}% today.`
      });
    }
    
    if (premium > 50) {
      analysis.signals.push({
        type: 'HIGH_PREMIUM',
        symbol,
        message: `${symbol} trading at ${premium.toFixed(0)}% premium to BTC. Possible overvaluation?`
      });
    }
  }
  
  return analysis;
}

async function generatePost() {
  const analysis = await analyzeAccumulation();
  
  if (analysis.error) {
    return { error: analysis.error };
  }
  
  const posts = [];
  
  // Educational post
  posts.push({
    type: 'EDUCATIONAL',
    content: `🐋 What are Bitcoin Accumulators?\n\nCompanies that buy BTC and hold it on their balance sheet. Like MSTR, GIGA, ETC.\n\nThey trade at a "premium" to BTC because investors pay for the management team & strategy.\n\nWhen BTC goes up, these stocks typically go up more (leverage).\n\n🧠 Thinking in Bets: Always consider probability. What's the chance the premium collapses vs continues?`
  });
  
  // Signal posts
  if (analysis.signals.length > 0) {
    for (const signal of analysis.signals.slice(0, 2)) {
      posts.push({
        type: 'SIGNAL',
        content: `📊 ${signal.message}\n\n#${signal.symbol} #Bitcoin #Crypto`
      });
    }
  }
  
  // Price update
  const priceLines = Object.entries(analysis.accumulators)
    .map(([sym, d]) => `${sym}: $${d.price.toFixed(2)} (${d.dailyChange})`)
    .join(' | ');
  
  posts.push({
    type: 'PRICE_UPDATE',
    content: `📈 BTC: $${analysis.btcPrice.toLocaleString()}\n\n${priceLines}\n\n#MSTR #GIGA #BTC`
  });
  
  return {
    analysis,
    posts,
    disclaimer: 'Educational only. Not financial advice. Do your own research.'
  };
}

// Command handlers
const commands = {
  // !whale-track - Track accumulators
  async whaleTrack(args) {
    const analysis = await analyzeAccumulation();
    
    let response = `🐋 **Whale Tracker**\n\n`;
    response += `BTC: $${analysis.btcPrice.toLocaleString()}\n\n`;
    response += `**Accumulators:**\n`;
    
    for (const [symbol, data] of Object.entries(analysis.accumulators)) {
      response += `${symbol}: $${data.price.toFixed(2)} (${data.dailyChange}) - Premium: ${data.premiumToBTC}\n`;
    }
    
    if (analysis.signals.length > 0) {
      response += `\n**Signals:**\n`;
      for (const signal of analysis.signals) {
        response += `• ${signal.message}\n`;
      }
    }
    
    return response;
  },
  
  // !whale-post - Generate X post
  async whalePost(args) {
    const result = await generatePost();
    
    if (result.error) {
      return { error: result.error };
    }
    
    // Return the first educational post as the default
    const post = result.posts.find(p => p.type === 'EDUCATIONAL') || result.posts[0];
    
    return {
      content: post.content,
      disclaimer: result.disclaimer,
      allPosts: result.posts.map(p => p.content)
    };
  },
  
  // !whale-signals - Get just the signals
  async whaleSignals(args) {
    const analysis = await analyzeAccumulation();
    
    if (analysis.signals.length === 0) {
      return "No significant signals detected today.";
    }
    
    return {
      signals: analysis.signals,
      disclaimer: 'Educational only. Not financial advice.'
    };
  }
};

// Main handler
async function handleWhaleCommand(command, args) {
  const cmd = commands[command];
  if (!cmd) {
    return { error: `Unknown command: ${command}. Use: whaleTrack, whalePost, whaleSignals` };
  }
  
  return await cmd(args);
}

module.exports = {
  handleWhaleCommand,
  analyzeAccumulation,
  generatePost
};
