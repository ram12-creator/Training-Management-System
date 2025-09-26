// Charts and Data Visualization JavaScript

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 10,
                    usePointStyle: true
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        };
    }

    // Initialize all charts on page
    initAllCharts() {
        const chartElements = document.querySelectorAll('[data-chart]');
        chartElements.forEach(element => {
            this.initChart(element);
        });
    }

    // Initialize a single chart
    initChart(element) {
        const ctx = element.getContext('2d');
        const chartType = element.dataset.chartType || 'bar';
        const chartData = element.dataset.chartData ? JSON.parse(element.dataset.chartData) : null;
        const chartOptions = element.dataset.chartOptions ? JSON.parse(element.dataset.chartOptions) : {};

        if (!chartData) {
            console.warn('No chart data provided for element:', element);
            return;
        }

        const options = { ...this.defaultOptions, ...chartOptions };

        // Create chart
        const chart = new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: options
        });

        // Store chart reference
        this.charts.set(element.id, chart);
        return chart;
    }

    // Create chart with custom configuration
    createChart(ctx, type, data, options = {}) {
        const mergedOptions = { ...this.defaultOptions, ...options };
        const chart = new Chart(ctx, {
            type: type,
            data: data,
            options: mergedOptions
        });
        return chart;
    }

    // Update chart data
    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    // Destroy chart
    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.destroy();
            this.charts.delete(chartId);
        }
    }

    // Common chart types with pre-configured options

    // Bar chart
    createBarChart(ctx, labels, datasets, options = {}) {
        const data = {
            labels: labels,
            datasets: datasets
        };

        const defaultOptions = {
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        };

        return this.createChart(ctx, 'bar', data, { ...defaultOptions, ...options });
    }

    // Line chart
    createLineChart(ctx, labels, datasets, options = {}) {
        const data = {
            labels: labels,
            datasets: datasets
        };

        const defaultOptions = {
            scales: {
                y: {
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.4
                }
            }
        };

        return this.createChart(ctx, 'line', data, { ...defaultOptions, ...options });
    }

    // Pie chart
    createPieChart(ctx, labels, data, options = {}) {
        const chartData = {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: this.getDefaultColors(data.length)
            }]
        };

        return this.createChart(ctx, 'pie', chartData, options);
    }

    // Doughnut chart
    createDoughnutChart(ctx, labels, data, options = {}) {
        const chartData = {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: this.getDefaultColors(data.length),
                borderWidth: 2
            }]
        };

        const defaultOptions = {
            cutout: '60%'
        };

        return this.createChart(ctx, 'doughnut', chartData, { ...defaultOptions, ...options });
    }

    // Polar area chart
    createPolarAreaChart(ctx, labels, data, options = {}) {
        const chartData = {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: this.getDefaultColors(data.length)
            }]
        };

        return this.createChart(ctx, 'polarArea', chartData, options);
    }

    // Radar chart
    createRadarChart(ctx, labels, datasets, options = {}) {
        const data = {
            labels: labels,
            datasets: datasets
        };

        return this.createChart(ctx, 'radar', data, options);
    }

    // Get default color palette
    getDefaultColors(count) {
        const colors = [
            '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
            '#6f42c1', '#fd7e14', '#20c997', '#6610f2', '#d63384',
            '#0dcaf0', '#ffc107', '#198754', '#0d6efd', '#6c757d'
        ];
        return colors.slice(0, count);
    }

    // Generate random colors
    getRandomColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(`#${Math.floor(Math.random() * 16777215).toString(16)}`);
        }
        return colors;
    }

    // Create gradient background
    createGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    }

    // Export chart as image
    exportChart(chartId, format = 'png', quality = 1.0) {
        const chart = this.charts.get(chartId);
        if (chart) {
            const image = chart.toBase64Image(format, quality);
            const link = document.createElement('a');
            link.href = image;
            link.download = `chart-${chartId}-${new Date().getTime()}.${format}`;
            link.click();
        }
    }

    // Responsive chart resizing
    handleResize() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    // Data formatting utilities
    formatNumber(value, decimals = 2) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    }

    formatCurrency(value, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(value);
    }

    formatPercent(value, decimals = 1) {
        return this.formatNumber(value * 100, decimals) + '%';
    }

    // Data aggregation functions
    calculateAverage(data) {
        const sum = data.reduce((a, b) => a + b, 0);
        return sum / data.length;
    }

    calculateSum(data) {
        return data.reduce((a, b) => a + b, 0);
    }

    calculateMin(data) {
        return Math.min(...data);
    }

    calculateMax(data) {
        return Math.max(...data);
    }

    // Time series data processing
    groupByTime(data, timeField, valueField, interval = 'day') {
        const groups = {};
        
        data.forEach(item => {
            const date = new Date(item[timeField]);
            let key;
            
            switch (interval) {
                case 'hour':
                    key = date.toISOString().slice(0, 13);
                    break;
                case 'day':
                    key = date.toISOString().slice(0, 10);
                    break;
                case 'month':
                    key = date.toISOString().slice(0, 7);
                    break;
                case 'year':
                    key = date.getFullYear().toString();
                    break;
                default:
                    key = date.toISOString().slice(0, 10);
            }
            
            if (!groups[key]) {
                groups[key] = [];
            }
            
            groups[key].push(item[valueField]);
        });
        
        return Object.entries(groups).map(([key, values]) => ({
            label: key,
            value: this.calculateAverage(values)
        }));
    }
}

// Initialize chart manager
const chartManager = new ChartManager();

// Initialize charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    chartManager.initAllCharts();
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            chartManager.handleResize();
        }, 250);
    });
});

// Global chart functions
window.createChart = function(ctx, type, data, options) {
    return chartManager.createChart(ctx, type, data, options);
};

window.updateChart = function(chartId, newData) {
    return chartManager.updateChart(chartId, newData);
};

window.destroyChart = function(chartId) {
    return chartManager.destroyChart(chartId);
};

window.exportChart = function(chartId, format, quality) {
    return chartManager.exportChart(chartId, format, quality);
};

// Common chart creation shortcuts
window.createBarChart = function(ctx, labels, datasets, options) {
    return chartManager.createBarChart(ctx, labels, datasets, options);
};

window.createLineChart = function(ctx, labels, datasets, options) {
    return chartManager.createLineChart(ctx, labels, datasets, options);
};

window.createPieChart = function(ctx, labels, data, options) {
    return chartManager.createPieChart(ctx, labels, data, options);
};

window.createDoughnutChart = function(ctx, labels, data, options) {
    return chartManager.createDoughnutChart(ctx, labels, data, options);
};

// Utility functions
window.formatNumber = function(value, decimals) {
    return chartManager.formatNumber(value, decimals);
};

window.formatCurrency = function(value, currency) {
    return chartManager.formatCurrency(value, currency);
};

window.formatPercent = function(value, decimals) {
    return chartManager.formatPercent(value, decimals);
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartManager;
}



// ____________________________________

// ______________________________________