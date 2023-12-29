// Constants
const BASE_COLOR = { r: 99, g: 100, b: 255 };
const COLOR_VARIATION_RANGE = 42;
const METRICS = ["Followers", "Toots", "Following"];
const POLL_INTERVAL_MS = 21000; // 21 seconds
// Create category charts
function createChart(containerId, category, categoryData) {
    const ctx = appendCanvasToContainer(containerId);
    const datasets = buildDatasets(categoryData);
    const labels = Object.keys(categoryData); // Account names
    const chartConfig = buildChartConfig('bar', labels, datasets, `${category} Stats`, true);
    if (ctx) {
        // @ts-ignore
        new Chart(ctx, chartConfig);
    }
}
// Append canvas to container
function appendCanvasToContainer(containerId) {
    const canvas = document.createElement('canvas');
    const container = document.getElementById(containerId);
    container.appendChild(canvas);
    return canvas.getContext('2d');
}
// Build datasets
function buildDatasets(categoryData) {
    return METRICS.map(metric => ({
        label: metric,
        // @ts-ignore
        data: Object.values(categoryData).map(data => data[metric] || 0),
        backgroundColor: getRandomColor(),
        borderColor: 'rgba(0, 123, 255, 0.7)',
        borderWidth: 1
    }));
}
// Build chart config
function buildChartConfig(type, labels, datasets, titleText, legend) {
    return {
        type: type,
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { display: false },
                    grid: { display: false },
                    stepped: true,
                },
                x: {
                    stacked: true,
                    ticks: { display: false },
                    grid: { display: false },
                    stepped: true
                }
            },
            plugins: {
                title: { display: false, text: titleText },
                legend: { display: legend, position: 'bottom' }
            }
        }
    };
}
// All time follower chart
function createAllTimeChart(containerId, allTimeFollowerChart) {
    const ctx = appendCanvasToContainer(containerId);
    const chartConfig = buildChartConfig('line', allTimeFollowerChart.labels, allTimeFollowerChart.datasets, 'All Time Followers', false);
    if (ctx) {
        // @ts-ignore
        new Chart(ctx, chartConfig);
    }
}
// Utility function to generate random colors
function getRandomColor() {
    const randomVariation = () => Math.floor(Math.random() * (COLOR_VARIATION_RANGE * 2 + 1)) - COLOR_VARIATION_RANGE;
    return `rgba(${BASE_COLOR.r + randomVariation()}, ${BASE_COLOR.g + randomVariation()}, ${BASE_COLOR.b + randomVariation()}, 0.5)`;
}
// Initialize charts and toots on window load
window.onload = function () {
    loadInitialToots();
    // @ts-ignore
    Object.entries(categoriesData).forEach(([category, categoryData]) => {
        createChart(`chart-container-${category}`, category, categoryData);
    });
    // @ts-ignore
    createAllTimeChart('allTimeFollowerChart', allTimeFollowerChart);
};
// Function to load initial toots
function loadInitialToots() {
    fetch('/get_latest_toots')
        .then(response => response.json())
        .then(toots => populateToots(toots))
        .catch(error => console.error('Error loading initial toots:', error));
}
// Function to populate toots
function populateToots(toots) {
    const container = document.getElementById('liveToots');
    const meUrl = 'https://mastodon.social/';
    toots.forEach(toot => {
        const mastodonHandle = `${toot.account.username}@${toot.url.split("https://")[1].split("/")[0]}`;
        const tootElement = document.createElement('div');
        tootElement.classList.add('toot');
        tootElement.innerHTML = `
            <div class="tootAvatar">
                <a href="${meUrl}@${mastodonHandle}" alt="${toot.account.display_name}" 
                nofollow="true" 
                target="_blank" 
                rel="noopener noreferrer">
                    <img src="${toot.account.avatar}">
                </a>
            </div>
            <div class="tootName">
                <a href="${meUrl}@${mastodonHandle}" alt="${toot.account.display_name}"
                nofollow="true"
                target="_blank"
                rel="noopener noreferrer">
                    ${toot.account.display_name}
                </a>
            </div>
            <div class="tootDate">
                ${new Date(toot.created_at).toLocaleString('en-US', { hour12: false })}
            </div>
            <div class="toots-content">
                ${toot.content}
                <div class="mediaAttachments">
                    ${toot.reblog ? toot.reblog.media_attachments.map(media => {
            if (media.type === 'image') {
                return `<img src="${media.preview_url}" alt="${toot.account.display_name}">`;
            }
            else if (media.type === 'video') {
                return `<video controls src="${media.preview_url}" alt="${toot.account.display_name}"></video>`;
            }
            else {
                return `<a href="${media.url}" alt="${toot.account.display_name}">Attachment</a>`;
            }
        }).join('') : ''}
                </div>
                <div class="tootUrl">
                    <a href="${toot.url}"
                    alt="View on Mastodon"
                    aria-label="View on Mastodon"
                    nofollow="true"
                    target="_blank"
                    rel="noopener noreferrer">
                            View on Mastodon
                    </a>
                </div>
            </div>
        `;
        // Add the new toot to the container
        if (container !== null)
            container.appendChild(tootElement);
    });
}
// Function to fetch and update toots
function fetchAndUpdateToots() {
    fetch('/get_latest_toots')
        .then(response => response.json())
        .then(newToots => {
        populateToots(newToots);
    })
        .catch(error => console.error('Error fetching new toots:', error));
}
// Poll for new toots every n seconds
setInterval(fetchAndUpdateToots, POLL_INTERVAL_MS);
