<script lang="ts">
	import { onMount } from 'svelte';
	import { authFetch } from '$lib/auth';
	import PasswordProtect from '$lib/components/PasswordProtect.svelte';

	interface Stats {
		stories: {
			total: number;
			today: number;
			this_week: number;
			this_month: number;
			per_hour: number;
			latest_at: string | null;
			avg_length: number;
		};
		feeds: {
			total: number;
			active: number;
			inactive: number;
			with_errors: number;
			unique_sources: number;
		};
		feed_items: {
			total: number;
			today: number;
			this_week: number;
			avg_per_story: number;
		};
		ai_usage: {
			total_tokens: number;
			estimated_cost_usd: number;
			avg_tokens_per_story: number;
		};
		top_feeds: Array<{
			name: string;
			item_count: number;
		}>;
	}

	let stats: Stats | null = null;
	let loading = true;
	let error: string | null = null;
	let autoRefresh = false;
	let refreshInterval: number;

	onMount(async () => {
		await loadStats();

		return () => {
			if (refreshInterval) {
				clearInterval(refreshInterval);
			}
		};
	});

	async function loadStats() {
		try {
			loading = true;
			const response = await authFetch('/api/stats');
			if (!response.ok) throw new Error('Failed to load stats');
			stats = await response.json();
			loading = false;
			error = null;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load stats';
			loading = false;
		}
	}

	function toggleAutoRefresh() {
		autoRefresh = !autoRefresh;
		if (autoRefresh) {
			refreshInterval = setInterval(loadStats, 30000); // Refresh every 30 seconds
		} else {
			clearInterval(refreshInterval);
		}
	}

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return 'N/A';
		const date = new Date(dateStr);
		return date.toLocaleString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function formatNumber(num: number): string {
		return num.toLocaleString();
	}
</script>

<svelte:head>
	<title>Stats - Singl News</title>
</svelte:head>

<PasswordProtect pageName="Statistics">
	<div class="stats-page">
		<div class="container">
			<header class="stats-header">
				<div class="header-top">
					<h1>THE STORY Statistics</h1>
					<div class="header-controls">
						<button class="btn btn-secondary" on:click={loadStats} disabled={loading}>
							{loading ? 'Refreshing...' : '↻ Refresh'}
						</button>
						<label class="toggle-label">
							<input type="checkbox" bind:checked={autoRefresh} on:change={toggleAutoRefresh} />
							Auto-refresh (30s)
						</label>
					</div>
				</div>
				<p class="stats-description">Real-time analytics and performance metrics</p>
			</header>

			{#if error}
				<div class="error-banner">{error}</div>
			{:else if loading && !stats}
				<div class="loading">Loading statistics...</div>
			{:else if stats}
				<!-- Story Statistics -->
				<section class="stats-section">
					<h2 class="section-title">📖 Story Versions</h2>
					<div class="stat-grid">
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.stories.total)}</div>
							<div class="stat-label">Total Versions</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.stories.today)}</div>
							<div class="stat-label">Today</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.stories.this_week)}</div>
							<div class="stat-label">This Week</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.stories.this_month)}</div>
							<div class="stat-label">This Month</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{stats.stories.per_hour.toFixed(2)}</div>
							<div class="stat-label">Per Hour (Avg)</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.stories.avg_length)}</div>
							<div class="stat-label">Avg Characters</div>
						</div>
					</div>
					{#if stats.stories.latest_at}
						<div class="info-box">
							<strong>Latest Story:</strong> {formatDate(stats.stories.latest_at)}
						</div>
					{/if}
				</section>

				<!-- Feed Statistics -->
				<section class="stats-section">
					<h2 class="section-title">📡 RSS Feeds</h2>
					<div class="stat-grid">
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.feeds.total)}</div>
							<div class="stat-label">Total Feeds</div>
						</div>
						<div class="stat-card stat-success">
							<div class="stat-value">{formatNumber(stats.feeds.active)}</div>
							<div class="stat-label">Active</div>
						</div>
						<div class="stat-card stat-warning">
							<div class="stat-value">{formatNumber(stats.feeds.inactive)}</div>
							<div class="stat-label">Inactive</div>
						</div>
						<div class="stat-card stat-danger">
							<div class="stat-value">{formatNumber(stats.feeds.with_errors)}</div>
							<div class="stat-label">With Errors</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.feeds.unique_sources)}</div>
							<div class="stat-label">Unique Sources</div>
						</div>
					</div>
				</section>

				<!-- Feed Items Statistics -->
				<section class="stats-section">
					<h2 class="section-title">📰 News Items</h2>
					<div class="stat-grid">
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.feed_items.total)}</div>
							<div class="stat-label">Total Items</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.feed_items.today)}</div>
							<div class="stat-label">Fetched Today</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.feed_items.this_week)}</div>
							<div class="stat-label">This Week</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{stats.feed_items.avg_per_story.toFixed(1)}</div>
							<div class="stat-label">Avg Per Story</div>
						</div>
					</div>
				</section>

				<!-- AI Usage Statistics -->
				<section class="stats-section">
					<h2 class="section-title">🤖 AI Usage</h2>
					<div class="stat-grid">
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.ai_usage.total_tokens)}</div>
							<div class="stat-label">Total Tokens</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">${stats.ai_usage.estimated_cost_usd.toFixed(2)}</div>
							<div class="stat-label">Estimated Cost</div>
						</div>
						<div class="stat-card">
							<div class="stat-value">{formatNumber(stats.ai_usage.avg_tokens_per_story)}</div>
							<div class="stat-label">Tokens Per Story</div>
						</div>
					</div>
					<div class="info-box">
						<strong>Note:</strong> Cost estimated at ~$0.01 per 1K tokens (GPT-4 pricing). Actual
						costs may vary.
					</div>
				</section>

				<!-- Top Feeds -->
				{#if stats.top_feeds.length > 0}
					<section class="stats-section">
						<h2 class="section-title">🏆 Most Active Feeds</h2>
						<div class="top-feeds-list">
							{#each stats.top_feeds as feed, i}
								<div class="top-feed-item">
									<div class="feed-rank">#{i + 1}</div>
									<div class="feed-name">{feed.name}</div>
									<div class="feed-count">{formatNumber(feed.item_count)} items</div>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				<!-- Quick Actions -->
				<section class="stats-section">
					<h2 class="section-title">⚡ Quick Actions</h2>
					<div class="action-grid">
						<a href="/control" class="action-card">
							<span class="action-icon">🎛️</span>
							<span class="action-label">Feed Control</span>
						</a>
						<a href="/history" class="action-card">
							<span class="action-icon">📚</span>
							<span class="action-label">Story Archive</span>
						</a>
						<a href="/api-docs" class="action-card">
							<span class="action-icon">📡</span>
							<span class="action-label">API Docs</span>
						</a>
						<a href="/" class="action-card">
							<span class="action-icon">🏠</span>
							<span class="action-label">Live Story</span>
						</a>
					</div>
				</section>
			{/if}
		</div>
	</div>
</PasswordProtect>

<style>
	.stats-page {
		min-height: 100vh;
		background: var(--color-highlight);
		padding: var(--spacing-xl) 0 var(--spacing-xl);
	}

	.stats-header {
		margin-bottom: var(--spacing-xl);
	}

	.header-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-sm);
		flex-wrap: wrap;
		gap: var(--spacing-md);
	}

	.stats-header h1 {
		font-size: 2.5rem;
		margin: 0;
	}

	.header-controls {
		display: flex;
		gap: var(--spacing-md);
		align-items: center;
	}

	.btn {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		padding: var(--spacing-sm) var(--spacing-md);
		border: 2px solid var(--color-text);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-secondary {
		background: white;
		color: var(--color-text);
	}

	.btn-secondary:hover:not(:disabled) {
		background: var(--color-border);
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.toggle-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
		cursor: pointer;
	}

	.stats-description {
		font-family: var(--font-sans);
		color: var(--color-text-light);
		margin: 0;
	}

	.stats-section {
		background: white;
		border: 2px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-lg);
		margin-bottom: var(--spacing-lg);
	}

	.section-title {
		font-size: 1.5rem;
		margin: 0 0 var(--spacing-lg) 0;
		padding-bottom: var(--spacing-sm);
		border-bottom: 2px solid var(--color-border);
	}

	.stat-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: var(--spacing-md);
	}

	.stat-card {
		background: var(--color-highlight);
		border: 2px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-md);
		text-align: center;
	}

	.stat-card.stat-success {
		background: #d4edda;
		border-color: #28a745;
	}

	.stat-card.stat-warning {
		background: #fff3cd;
		border-color: #ffc107;
	}

	.stat-card.stat-danger {
		background: #f8d7da;
		border-color: #dc3545;
	}

	.stat-value {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-text);
		margin-bottom: var(--spacing-xs);
	}

	.stat-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.info-box {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		background: var(--color-highlight);
		padding: var(--spacing-sm);
		border-left: 3px solid var(--color-text);
		border-radius: 4px;
		margin-top: var(--spacing-md);
	}

	.top-feeds-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-sm);
	}

	.top-feed-item {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
		padding: var(--spacing-sm);
		background: var(--color-highlight);
		border-radius: 4px;
	}

	.feed-rank {
		font-family: var(--font-sans);
		font-size: 1.125rem;
		font-weight: 700;
		color: var(--color-text-light);
		min-width: 40px;
	}

	.feed-name {
		flex: 1;
		font-family: var(--font-sans);
		font-weight: 600;
	}

	.feed-count {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
	}

	.action-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: var(--spacing-md);
	}

	.action-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--spacing-sm);
		padding: var(--spacing-lg);
		background: var(--color-highlight);
		border: 2px solid var(--color-border);
		border-radius: 8px;
		text-decoration: none;
		color: var(--color-text);
		transition: all 0.2s;
	}

	.action-card:hover {
		border-color: var(--color-text);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		transform: translateY(-2px);
	}

	.action-icon {
		font-size: 2rem;
	}

	.action-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		text-align: center;
	}

	.loading,
	.error-banner {
		text-align: center;
		padding: var(--spacing-xl);
		font-family: var(--font-sans);
	}

	.error-banner {
		background: #f8d7da;
		color: #dc3545;
		border: 2px solid #dc3545;
		border-radius: 8px;
		margin-bottom: var(--spacing-lg);
	}

	@media (max-width: 768px) {
		.header-top {
			flex-direction: column;
			align-items: flex-start;
		}

		.stats-header h1 {
			font-size: 2rem;
		}

		.stat-grid {
			grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
		}

		.stat-value {
			font-size: 1.5rem;
		}
	}
</style>
