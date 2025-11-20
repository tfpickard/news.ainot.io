<script lang="ts">
	export let data: any;

	function getBarWidth(count: number, max: number): number {
		return (count / max) * 100;
	}

	let maxArticles = 0;
	if (data && data.sources.length > 0) {
		maxArticles = Math.max(...data.sources.map((s: any) => s.article_count));
	}

	// Limit to top 20 sources for better visualization
	let topSources = data?.sources?.slice(0, 20) || [];
</script>

<div class="source-dominance">
	{#if data && topSources.length > 0}
		<div class="chart-container">
			<div class="source-list">
				{#each topSources as source, i}
					<div class="source-item">
						<div class="source-info">
							<div class="source-name">{source.source_name}</div>
							<div class="source-meta">
								<span class="article-count">{source.article_count} articles</span>
								{#if source.categories.length > 0}
									<span class="categories">
										{source.categories.join(', ')}
									</span>
								{/if}
							</div>
						</div>
						<div class="bar-container">
							<div
								class="bar"
								style="width: {getBarWidth(source.article_count, maxArticles)}%"
								style:background="hsl({(i / topSources.length) * 360}, 70%, 60%)"
							>
								<span class="bar-label">{source.article_count}</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<div class="stats-summary">
			<div class="stat">
				<span class="stat-label">Total Sources:</span>
				<span class="stat-value">{data.sources.length}</span>
			</div>
			<div class="stat">
				<span class="stat-label">Total Articles:</span>
				<span class="stat-value">
					{data.sources.reduce((sum, s) => sum + s.article_count, 0)}
				</span>
			</div>
			<div class="stat">
				<span class="stat-label">Top Source:</span>
				<span class="stat-value">{data.sources[0]?.source_name || 'N/A'}</span>
			</div>
		</div>

		{#if data.sources.length > 20}
			<div class="truncated-notice">
				Showing top 20 of {data.sources.length} sources
			</div>
		{/if}
	{:else}
		<div class="no-data">No source data available for this time range</div>
	{/if}
</div>

<style>
	.source-dominance {
		padding: 1rem 0;
	}

	.chart-container {
		background: var(--bg-primary);
		border-radius: 8px;
		padding: 1.5rem;
	}

	.source-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.source-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.source-info {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.source-name {
		font-weight: 600;
		color: var(--text-primary);
		font-size: 0.95rem;
	}

	.source-meta {
		display: flex;
		gap: 1rem;
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.article-count {
		font-weight: 600;
	}

	.categories {
		font-style: italic;
	}

	.bar-container {
		width: 100%;
		background: var(--bg-secondary);
		border-radius: 4px;
		overflow: hidden;
		height: 28px;
	}

	.bar {
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding: 0 0.75rem;
		transition: width 0.5s ease;
		min-width: 40px;
	}

	.bar-label {
		font-size: 0.8rem;
		font-weight: 700;
		color: white;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
	}

	.stats-summary {
		display: flex;
		gap: 2rem;
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid var(--border-color);
		justify-content: center;
		flex-wrap: wrap;
	}

	.stat {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		align-items: center;
	}

	.stat-label {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.stat-value {
		font-size: 1.3rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.truncated-notice {
		text-align: center;
		margin-top: 1rem;
		padding: 0.75rem;
		background: var(--bg-secondary);
		border-radius: 6px;
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.no-data {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
	}

	@media (max-width: 768px) {
		.source-info {
			flex-direction: column;
			gap: 0.25rem;
		}

		.source-meta {
			gap: 0.5rem;
			flex-wrap: wrap;
		}

		.bar-container {
			height: 24px;
		}

		.bar-label {
			font-size: 0.7rem;
		}

		.stats-summary {
			gap: 1rem;
		}

		.stat-value {
			font-size: 1.1rem;
		}
	}
</style>
