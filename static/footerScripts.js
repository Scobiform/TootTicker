function createChart(containerId, category, categoryData) {
    const ctx = document.createElement('canvas');
    document.getElementById(containerId).appendChild(ctx);

    const datasets = [];
    const labels = Object.keys(categoryData); // Account names

    // Metrics to display (e.g., Followers, Toots, Following)
    const metrics = ["Followers", "Toots", "Following"];

    metrics.forEach(metric => {
        const data = labels.map(label => categoryData[label][metric] || 0);
        datasets.push({
            label: `${metric}`,
            data: data,
            backgroundColor: getRandomColor(),
            borderColor: 'rgba(0, 123, 255, 0.7)',
            borderWidth: 1
        });
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true,
                },
                x: { stacked: true,
                    ticks: {
                        display: false
                    }
                }
            },
            plugins: {
                title: {
                    display: false,
                    text: `${category} Stats`
                },
                legend: {
                    display: true,
                    position: 'bottom'
                }          
            }
        }
    });
}

window.onload = function() {
    // Load initial toots when the page loads
    loadInitialToots();

    for (const [category, categoryData] of Object.entries(categoriesData)) {
        createChart(`chart-container-${category}`, category, categoryData);
    }
};

function getRandomColor() {
        // Base color 99, 100, 255
        const baseR = 99;
        const baseG = 100;
        const baseB = 255;

        // Define a range for variation (+/- 42)
        const range = 42;

        // Generate random variations around the base color within the specified range
        const r = Math.max(Math.min(baseR + Math.floor(Math.random() * (range * 2 + 1)) - range, 255), 0);
        const g = Math.max(Math.min(baseG + Math.floor(Math.random() * (range * 2 + 1)) - range, 255), 0);
        const b = Math.max(Math.min(baseB + Math.floor(Math.random() * (range * 2 + 1)) - range, 255), 0);

        return `rgba(${r}, ${g}, ${b}, 0.5)`;
}

// Function to load initial toots
function loadInitialToots() {
    fetch('/get_latest_toots')
        .then(response => response.json())
        .then(toots => populateToots(toots))
        .catch(error => console.error('Error loading initial toots:', error));
}

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
                        } else if (media.type === 'video') {
                            return `<video controls src="${media.preview_url}" alt="${toot.account.display_name}"></video>`;
                        } else {
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
        container.appendChild(tootElement);
    });
}      

function fetchAndUpdateToots() {
    fetch('/get_latest_toots')
        .then(response => response.json())
        .then(newToots => {
            populateToots(newToots);
        })
        .catch(error => console.error('Error fetching new toots:', error));
}

// Load initial toots when the page loads
document.addEventListener('DOMContentLoaded', loadInitialToots);
// Poll for new toots every n seconds
setInterval(fetchAndUpdateToots, 21000);