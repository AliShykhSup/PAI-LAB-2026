const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const samplePrompts = document.getElementById('samplePrompts');
const resultsPanel = document.getElementById('resultsPanel');
const resultCount = document.getElementById('resultCount');

function scrollResultsToTop() {
    resultsPanel.scrollTop = 0;
}

function buildResultCard(result, isBestMatch = false) {
    const article = document.createElement('article');
    article.className = `result-card${isBestMatch ? ' best-match' : ''}`;

    const header = document.createElement('div');
    header.className = 'result-header';

    const title = document.createElement('h3');
    title.textContent = result.question;

    const badge = document.createElement('span');
    badge.className = 'score-badge';
    badge.textContent = `${Math.round(result.score * 100)}% match`;

    header.appendChild(title);
    header.appendChild(badge);

    const topic = document.createElement('p');
    topic.className = 'result-topic';
    topic.textContent = result.topic;

    const answer = document.createElement('p');
    answer.className = 'result-answer';
    answer.textContent = result.answer;

    article.appendChild(header);
    article.appendChild(topic);
    article.appendChild(answer);

    return article;
}

function renderEmptyState(message) {
    resultsPanel.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.className = 'message bot';

    const bubble = document.createElement('div');
    bubble.className = 'bubble bubble-empty';
    bubble.textContent = message;

    wrapper.appendChild(bubble);
    resultsPanel.appendChild(wrapper);
}

function renderResults(query, results) {
    resultsPanel.innerHTML = '';

    const summary = document.createElement('div');
    summary.className = 'query-summary';
    summary.textContent = `Query: ${query}`;
    resultsPanel.appendChild(summary);

    if (!results.length) {
        renderEmptyState('No matching hotel answer was found. Try a different question or use one of the quick prompts.');
        return;
    }

    results.forEach((result, index) => {
        resultsPanel.appendChild(buildResultCard(result, index === 0));
    });

    scrollResultsToTop();
}

async function sendQuery(query) {
    const response = await fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
        }),
    });

    return response.json();
}

searchForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const query = queryInput.value.trim();
    if (!query) {
        renderEmptyState('Please type a question so I can search the hotel dataset.');
        return;
    }

    resultCount.textContent = 'Searching...';
    resultsPanel.innerHTML = '<div class="message bot"><div class="bubble bubble-empty">Searching the FAISS index...</div></div>';

    try {
        const data = await sendQuery(query);
        resultCount.textContent = `${data.count} result${data.count === 1 ? '' : 's'} found`;
        renderResults(query, data.results || []);
    } catch (error) {
        resultCount.textContent = 'Error';
        renderEmptyState('The search service is temporarily unavailable. Please try again.');
    }
});

samplePrompts.querySelectorAll('.prompt-chip').forEach((button) => {
    button.addEventListener('click', () => {
        queryInput.value = button.textContent;
        queryInput.focus();
    });
});

if (!window.SAMPLE_QUESTIONS || !window.SAMPLE_QUESTIONS.length) {
    renderEmptyState('Add questions to the dataset to enable similarity search.');
}
