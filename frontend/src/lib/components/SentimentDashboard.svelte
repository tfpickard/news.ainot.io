<script lang="ts">
	export let sentiment: {
		overall: string;
		score: { positive: number; negative: number; neutral: number };
		reasoning?: string;
	} | null = null;

	function getColorForSentiment(sentiment: string): string {
		switch (sentiment) {
			case 'positive': return '#22c55e';
			case 'negative': return '#ef4444';
			case 'neutral': return '#94a3b8';
			default: return '#94a3b8';
		}
	}

	function formatPercentage(value: number): string {
		return `${(value * 100).toFixed(1)}%`;
	}
</script>

<div class="sentiment-dashboard">
	<h3 class="dashboard-title">Sentiment Analysis</h3>

	{#if sentiment}
		<div class="sentiment-summary">
			<div class="sentiment-badge" style="background: {getColorForSentiment(sentiment.overall)}">
				{sentiment.overall?.toUpperCase()}
			</div>
		</div>

		<div class="sentiment-bars">
			<div class="sentiment-bar">
				<div class="bar-label">Positive</div>
				<div class="bar-container">
					<div
						class="bar-fill positive"
						style="width: {formatPercentage(sentiment.score.positive)}"
					></div>
				</div>
				<div class="bar-value">{formatPercentage(sentiment.score.positive)}</div>
			</div>

			<div class="sentiment-bar">
				<div class="bar-label">Neutral</div>
				<div class="bar-container">
					<div
						class="bar-fill neutral"
						style="width: {formatPercentage(sentiment.score.neutral)}"
					></div>
				</div>
				<div class="bar-value">{formatPercentage(sentiment.score.neutral)}</div>
			</div>

			<div class="sentiment-bar">
				<div class="bar-label">Negative</div>
				<div class="bar-container">
					<div
						class="bar-fill negative"
						style="width: {formatPercentage(sentiment.score.negative)}"
					></div>
				</div>
				<div class="bar-value">{formatPercentage(sentiment.score.negative)}</div>
			</div>
		</div>

		{#if sentiment.reasoning}
			<div class="reasoning">
				<p>{sentiment.reasoning}</p>
			</div>
		{/if}
	{:else}
		<div class="loading">Analyzing sentiment...</div>
	{/if}
</div>

<style>
	.sentiment-dashboard {
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

	.sentiment-summary {
		text-align: center;
		margin-bottom: var(--spacing-md);
	}

	.sentiment-badge {
		display: inline-block;
		padding: var(--spacing-xs) var(--spacing-md);
		border-radius: 20px;
		color: white;
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.sentiment-bars {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-sm);
	}

	.sentiment-bar {
		display: grid;
		grid-template-columns: 80px 1fr 60px;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.bar-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
	}

	.bar-container {
		background: var(--color-bg);
		border-radius: 4px;
		height: 24px;
		overflow: hidden;
		border: 1px solid var(--color-border);
	}

	.bar-fill {
		height: 100%;
		transition: width 0.5s ease;
	}

	.bar-fill.positive {
		background: linear-gradient(90deg, #22c55e, #16a34a);
	}

	.bar-fill.neutral {
		background: linear-gradient(90deg, #94a3b8, #64748b);
	}

	.bar-fill.negative {
		background: linear-gradient(90deg, #ef4444, #dc2626);
	}

	.bar-value {
		font-family: var(--font-mono);
		font-size: 0.875rem;
		font-weight: 600;
		text-align: right;
		color: var(--color-text);
	}

	.reasoning {
		margin-top: var(--spacing-md);
		padding-top: var(--spacing-md);
		border-top: 1px solid var(--color-border);
		font-size: 0.875rem;
		color: var(--color-text-light);
		font-style: italic;
	}

	.loading {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-light);
		font-style: italic;
	}
</style>
