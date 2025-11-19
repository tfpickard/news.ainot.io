<script lang="ts">
	export let sourceAnalysis: Array<{
		source_name: string;
		sentiment: { positive: number; negative: number; neutral: number };
		bias: {
			political_lean: string;
			lean_score: number;
			loaded_language_count: number;
			emotional_language_score: number;
		};
		article_count: number;
	}> | null = null;

	function getLeanColor(lean: string): string {
		switch (lean) {
			case 'left': return '#3b82f6';
			case 'center-left': return '#60a5fa';
			case 'center': return '#94a3b8';
			case 'center-right': return '#f87171';
			case 'right': return '#ef4444';
			default: return '#94a3b8';
		}
	}

	function getDominantSentiment(sentiment: { positive: number; negative: number; neutral: number }): string {
		const max = Math.max(sentiment.positive, sentiment.negative, sentiment.neutral);
		if (max === sentiment.positive) return 'positive';
		if (max === sentiment.negative) return 'negative';
		return 'neutral';
	}

	function getSentimentColor(sentiment: string): string {
		switch (sentiment) {
			case 'positive': return '#22c55e';
			case 'negative': return '#ef4444';
			case 'neutral': return '#94a3b8';
			default: return '#94a3b8';
		}
	}
</script>

<div class="cross-source-dashboard">
	<h3 class="dashboard-title">Cross-Source Analysis</h3>

	{#if sourceAnalysis && sourceAnalysis.length > 0}
		<div class="sources-grid">
			{#each sourceAnalysis as source}
				<div class="source-card">
					<div class="source-header">
						<div class="source-name">{source.source_name}</div>
						<div class="article-count">{source.article_count} article{source.article_count !== 1 ? 's' : ''}</div>
					</div>

					<div class="source-metrics">
						<div class="metric">
							<div class="metric-label">Political Lean</div>
							<div class="metric-badge" style="background: {getLeanColor(source.bias.political_lean)}">
								{source.bias.political_lean.replace('-', ' ').toUpperCase()}
							</div>
						</div>

						<div class="metric">
							<div class="metric-label">Sentiment</div>
							<div class="metric-badge" style="background: {getSentimentColor(getDominantSentiment(source.sentiment))}">
								{getDominantSentiment(source.sentiment).toUpperCase()}
							</div>
						</div>
					</div>

					<div class="sentiment-breakdown">
						<div class="breakdown-title">Sentiment Breakdown</div>
						<div class="sentiment-bars-mini">
							<div class="bar-mini" style="background: #22c55e; width: {source.sentiment.positive * 100}%"></div>
							<div class="bar-mini" style="background: #94a3b8; width: {source.sentiment.neutral * 100}%"></div>
							<div class="bar-mini" style="background: #ef4444; width: {source.sentiment.negative * 100}%"></div>
						</div>
					</div>

					<div class="bias-indicators">
						<div class="indicator">
							<span class="indicator-label">Emotional Language:</span>
							<span class="indicator-value">{(source.bias.emotional_language_score * 100).toFixed(0)}%</span>
						</div>
						<div class="indicator">
							<span class="indicator-label">Loaded Terms:</span>
							<span class="indicator-value">{source.bias.loaded_language_count}</span>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if sourceAnalysis && sourceAnalysis.length === 0}
		<div class="empty">No source analysis available.</div>
	{:else}
		<div class="loading">Analyzing sources...</div>
	{/if}
</div>

<style>
	.cross-source-dashboard {
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-lg);
		margin-bottom: var(--spacing-md);
	}

	.dashboard-title {
		font-family: var(--font-sans);
		font-size: 1rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-md);
		color: var(--color-text);
	}

	.sources-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--spacing-md);
	}

	.source-card {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		padding: var(--spacing-md);
	}

	.source-header {
		margin-bottom: var(--spacing-sm);
		padding-bottom: var(--spacing-sm);
		border-bottom: 1px solid var(--color-border);
	}

	.source-name {
		font-family: var(--font-sans);
		font-size: 0.9375rem;
		font-weight: 700;
		color: var(--color-text);
		margin-bottom: 4px;
	}

	.article-count {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
	}

	.source-metrics {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-sm);
	}

	.metric {
		text-align: center;
	}

	.metric-label {
		font-family: var(--font-sans);
		font-size: 0.6875rem;
		color: var(--color-text-light);
		margin-bottom: 4px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.metric-badge {
		display: inline-block;
		padding: 4px 8px;
		border-radius: 12px;
		color: white;
		font-family: var(--font-sans);
		font-size: 0.6875rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.sentiment-breakdown {
		margin-bottom: var(--spacing-sm);
	}

	.breakdown-title {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
		margin-bottom: 4px;
	}

	.sentiment-bars-mini {
		display: flex;
		height: 8px;
		border-radius: 4px;
		overflow: hidden;
		background: var(--color-border);
	}

	.bar-mini {
		height: 100%;
	}

	.bias-indicators {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding-top: var(--spacing-sm);
		border-top: 1px solid var(--color-border);
	}

	.indicator {
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
	}

	.indicator-label {
		color: var(--color-text-light);
	}

	.indicator-value {
		font-family: var(--font-mono);
		font-weight: 600;
		color: var(--color-text);
	}

	.loading, .empty {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-light);
		font-style: italic;
	}
</style>
