const form = document.getElementById('quote-form');
const statusEl = document.getElementById('status');
const symbolInput = document.getElementById('symbol');

const symbolLabel = document.getElementById('symbol-label');
const priceLabel = document.getElementById('price-label');
const openLabel = document.getElementById('open-label');
const highLabel = document.getElementById('high-label');
const lowLabel = document.getElementById('low-label');
const volumeLabel = document.getElementById('volume-label');
const sourceLabel = document.getElementById('source-label');
const insightLabel = document.getElementById('insight-label');

function formatValue(value, decimals = 2) {
  if (value === null || value === undefined) return '--';
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatVolume(value) {
  if (value === null || value === undefined) return '--';
  return Number(value).toLocaleString();
}

async function loadQuote(symbol) {
  statusEl.textContent = `Loading ${symbol.toUpperCase()}...`;
  const response = await fetch(`/api/quote?symbol=${encodeURIComponent(symbol)}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Unable to load quote.');
  }

  symbolLabel.textContent = data.symbol;
  priceLabel.textContent = `$${formatValue(data.price)}`;
  openLabel.textContent = formatValue(data.open);
  highLabel.textContent = formatValue(data.high);
  lowLabel.textContent = formatValue(data.low);
  volumeLabel.textContent = formatVolume(data.volume);
  sourceLabel.textContent = `Source: ${data.source}`;
  statusEl.textContent = `Showing the latest available quote for ${data.symbol}.`;
}

async function loadInsight(symbol) {
  insightLabel.textContent = 'Generating a short AI insight...';
  const response = await fetch(`/api/stock-story?symbol=${encodeURIComponent(symbol)}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Unable to generate insight.');
  }

  insightLabel.textContent = data.story;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const symbol = symbolInput.value.trim();

  try {
    await loadQuote(symbol);
    await loadInsight(symbol);
  } catch (error) {
    statusEl.textContent = error.message;
  }
});

loadQuote('AAPL').catch(() => {
  statusEl.textContent = 'Enter a symbol to fetch a stock quote.';
});

loadInsight('AAPL').catch(() => {
  insightLabel.textContent = 'AI insight will appear here after a successful quote lookup.';
});