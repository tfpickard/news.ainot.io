<script lang="ts">
	import { onMount } from 'svelte';
	import SentimentTrendChart from '$lib/components/SentimentTrendChart.svelte';
	import KeywordCloudViz from '$lib/components/KeywordCloudViz.svelte';
	import AbsurdityTrendChart from '$lib/components/AbsurdityTrendChart.svelte';
	import SourceDominanceChart from '$lib/components/SourceDominanceChart.svelte';

	interface TrendData {
		sentiment_trends: any;
		keyword_cloud: any;
		absurdity_trends: any;
		source_dominance: any;
		date_range: {
			start: string;
			end: string;
		};
		total_stories_analyzed: number;
	}

	let trendsData: TrendData | null = null;
	let loading = true;
	let error: string | null = null;
	let days = 7;
	let autoRefresh = false;
	let refreshInterval: number;

	onMount(async () => {
		await loadTrends();

		return () => {
			if (refreshInterval) {
				clearInterval(refreshInterval);
			}
		};
	});

	async function loadTrends() {
		try {
			loading = true;
			const response = await fetch(`/api/trends/all?days=${days}`);
			if (!response.ok) throw new Error('Failed to load trends');
			trendsData = await response.json();
			loading = false;
			error = null;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load trends';
			loading = false;
		}
	}

	function toggleAutoRefresh() {
		autoRefresh = !autoRefresh;
		if (autoRefresh) {
			refreshInterval = setInterval(loadTrends, 60000); // Refresh every 60 seconds
		} else {
			clearInterval(refreshInterval);
		}
	}

	async function changeDays(newDays: number) {
		days = newDays;
		await loadTrends();
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Trend Analytics - UnioNews</title>
	<meta
		name="description"
		content="Explore narrative evolution, sentiment trends, and absurdity metrics over time"
	/>
</svelte:head>

<div class="trends-page">
	<div class="container">
		<header class="trends-header">
			<div class="header-top">
				<h1>Narrative Trend Analytics</h1>
				<a href="/" class="back-link">← Back to Feed</a>
			</div>

			<p class="subtitle">
				Tracking the evolution of the singular narrative through time, sentiment, and absurdity
			</p>

			<div class="controls">
				<div class="time-range">
					<label>Time Range:</label>
					<div class="button-group">
						<button class:active={days === 1} on:click={() => changeDays(1)}>24h</button>
						<button class:active={days === 3} on:click={() => changeDays(3)}>3d</button>
						<button class:active={days === 7} on:click={() => changeDays(7)}>7d</button>
						<button class:active={days === 14} on:click={() => changeDays(14)}>14d</button>
						<button class:active={days === 30} on:click={() => changeDays(30)}>30d</button>
					</div>
				</div>

				<div class="actions">
					<button on:click={loadTrends} disabled={loading}>
						{loading ? 'Loading...' : 'Refresh'}
					</button>
					<button on:click={toggleAutoRefresh} class:active={autoRefresh}>
						{autoRefresh ? '⏸ Auto-refresh' : '▶ Auto-refresh'}
					</button>
				</div>
			</div>

			{#if trendsData}
				<div class="date-info">
					<span>
						Analyzing <strong>{trendsData.total_stories_analyzed}</strong> stories from
						<strong>{formatDate(trendsData.date_range.start)}</strong> to
						<strong>{formatDate(trendsData.date_range.end)}</strong>
					</span>
				</div>
			{/if}
		</header>

		{#if loading}
			<div class="loading">
				<div class="spinner"></div>
				<p>Analyzing narrative trends...</p>
			</div>
		{:else if error}
			<div class="error">
				<p>⚠️ {error}</p>
				<button on:click={loadTrends}>Try Again</button>
			</div>
		{:else if trendsData}
			<div class="trends-grid">
				<!-- Sentiment Trends -->
				<section class="trend-section sentiment-section">
					<h2>Sentiment Evolution</h2>
					<p class="section-description">
						How the narrative's emotional tone shifts across versions
					</p>
					<SentimentTrendChart data={trendsData.sentiment_trends} />
				</section>

				<!-- Absurdity Trends -->
				<section class="trend-section absurdity-section">
					<h2>Absurdity Metrics</h2>
					<p class="section-description">
						Tracking the surreal intensity of the narrative over time
					</p>
					<AbsurdityTrendChart data={trendsData.absurdity_trends} />
				</section>

				<!-- Keyword Cloud -->
				<section class="trend-section keyword-section">
					<h2>Narrative Keywords</h2>
					<p class="section-description">Dominant themes and concepts across the timeframe</p>
					<KeywordCloudViz data={trendsData.keyword_cloud} />
				</section>

				<!-- Source Dominance -->
				<section class="trend-section source-section">
					<h2>Source Contributions</h2>
					<p class="section-description">Which feeds shape the narrative most</p>
					<SourceDominanceChart data={trendsData.source_dominance} />
				</section>
			</div>
		{/if}
	</div>
</div>

<style>
	.trends-page {
		min-height: 100vh;
		background: var(--bg-primary);
		color: var(--text-primary);
		padding: 2rem 1rem;
	}

	.container {
		max-width: 1400px;
		margin: 0 auto;
	}

	.trends-header {
		margin-bottom: 3rem;
	}

	.header-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	h1 {
		font-size: 2.5rem;
		margin: 0;
		font-weight: 800;
		letter-spacing: -0.02em;
	}

	.back-link {
		color: var(--text-secondary);
		text-decoration: none;
		font-size: 1rem;
		transition: color 0.2s;
	}

	.back-link:hover {
		color: var(--text-primary);
	}

	.subtitle {
		color: var(--text-secondary);
		font-size: 1.1rem;
		margin: 0 0 2rem 0;
		max-width: 800px;
	}

	.controls {
		display: flex;
		gap: 2rem;
		flex-wrap: wrap;
		align-items: center;
		padding: 1.5rem;
		background: var(--bg-secondary);
		border-radius: 8px;
		border: 1px solid var(--border-color);
	}

	.time-range {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.time-range label {
		font-weight: 600;
		color: var(--text-secondary);
	}

	.button-group {
		display: flex;
		gap: 0.5rem;
	}

	button {
		padding: 0.6rem 1.2rem;
		border: 1px solid var(--border-color);
		background: var(--bg-primary);
		color: var(--text-primary);
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 600;
		transition: all 0.2s;
	}

	button:hover:not(:disabled) {
		background: var(--bg-hover);
		border-color: var(--text-secondary);
	}

	button.active {
		background: var(--accent-color);
		color: white;
		border-color: var(--accent-color);
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
		margin-left: auto;
	}

	.date-info {
		margin-top: 1rem;
		padding: 1rem;
		background: var(--bg-secondary);
		border-left: 4px solid var(--accent-color);
		border-radius: 4px;
		font-size: 0.95rem;
		color: var(--text-secondary);
	}

	.date-info strong {
		color: var(--text-primary);
	}

	.loading,
	.error {
		text-align: center;
		padding: 4rem 2rem;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid var(--border-color);
		border-top-color: var(--accent-color);
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error {
		color: #dc3545;
	}

	.trends-grid {
		display: grid;
		gap: 2rem;
	}

	.trend-section {
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 12px;
		padding: 2rem;
	}

	.trend-section h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.8rem;
		font-weight: 700;
	}

	.section-description {
		color: var(--text-secondary);
		margin: 0 0 1.5rem 0;
		font-size: 0.95rem;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.trends-page {
			padding: 1rem 0.5rem;
		}

		h1 {
			font-size: 1.8rem;
		}

		.header-top {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.controls {
			flex-direction: column;
			align-items: stretch;
		}

		.time-range {
			flex-direction: column;
			align-items: stretch;
		}

		.button-group {
			flex-wrap: wrap;
		}

		.actions {
			margin-left: 0;
			width: 100%;
		}

		.actions button {
			flex: 1;
		}

		.trend-section {
			padding: 1.5rem;
		}
	}
</style>
