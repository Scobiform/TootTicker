//import { Chart, ChartConfiguration, ChartData, ChartType } from 'chart.js';
// Constants
const BASE_COLOR = { r: 99, g: 100, b: 255 };
const COLOR_VARIATION_RANGE = 42;
const METRICS = ["Followers", "Toots", "Following"];
const POLL_INTERVAL_MS = 21000; // 21 seconds
// Create category charts
function createChart(containerId, category, categoryData) {
    const ctx = appendCanvasToContainer(containerId);
    if (!ctx)
        return;
    const datasets = buildDatasets(categoryData);
    const labels = Object.keys(categoryData); // Account names
    // @ts-ignore
    const chartConfig = buildChartConfig('bar', labels, datasets, `${category} Stats`, true);
    new Chart(ctx, chartConfig);
}
// Append canvas to container
function appendCanvasToContainer(containerId) {
    const canvas = document.createElement('canvas');
    const container = document.getElementById(containerId);
    if (container) {
        container.appendChild(canvas);
        return canvas.getContext('2d');
    }
    return null;
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
function buildChartConfig(
// @ts-ignore
type, labels, datasets, titleText, 
// @ts-ignore
legend) {
    return {
        type: type,
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            font: {
                family: 'Mukta, sans-serif',
                size: 10
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { display: false },
                    grid: { display: false },
                },
                x: {
                    stacked: true,
                    ticks: { display: false },
                    grid: { display: false },
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
// @ts-ignore
function createAllTimeChart(containerId, allTimeFollowerChart) {
    const ctx = appendCanvasToContainer(containerId);
    if (!ctx)
        return;
    const chartConfig = buildChartConfig('line', allTimeFollowerChart.labels, allTimeFollowerChart.datasets, 'All Time Followers', false);
    new Chart(ctx, chartConfig);
}
// Utility function to generate random colors
function getRandomColor() {
    const randomVariation = () => Math.floor(Math.random() * (COLOR_VARIATION_RANGE * 2 + 1)) - COLOR_VARIATION_RANGE;
    return `rgba(${BASE_COLOR.r + randomVariation()}, ${BASE_COLOR.g + randomVariation()}, ${BASE_COLOR.b + randomVariation()}, 0.5)`;
}
// Initialize charts and toots on window load
window.onload = function () {
    // @ts-ignore
    Object.entries(categoriesData).forEach(([category, categoryData]) => {
        createChart(`chart-container-${category}`, category, categoryData);
    });
    // @ts-ignore
    createAllTimeChart('allTimeFollowerChart', allTimeFollowerChart);
};
