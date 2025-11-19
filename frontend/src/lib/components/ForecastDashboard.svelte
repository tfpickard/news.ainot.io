<script lang="ts">
	export let predictions: Array<{
		scenario: string;
		probability: number;
		timeframe: string;
		reasoning: string;
		related_events: string[];
	}> | null = null;

	function getTimeframeColor(timeframe: string): string {
		switch (timeframe) {
			case 'short-term': return '#3b82f6';
			case 'medium-term': return '#f59e0b';
			case 'long-term': return '#8b5cf6';
			default: return '#94a3b8';
		}
	}

	function getProbabilityClass(probability: number): string {
		if (probability >= 0.7) return 'high';
		if (probability >= 0.4) return 'medium';
		return 'low';
	}
</script>

<div class="forecast-dashboard">
	<h3 class="dashboard-title">What's Next: Forecasting</h3>

	{#if predictions && predictions.length > 0}
		<div class="predictions">
			{#each predictions as prediction}
				<div class="prediction">
					<div class="prediction-header">
						<div class="timeframe-badge" style="background: {getTimeframeColor(prediction.timeframe)}">
							{prediction.timeframe.replace('-', ' ').toUpperCase()}
						</div>
						<div class="probability {getProbabilityClass(prediction.probability)}">
							<div class="probability-label">Likelihood</div>
							<div class="probability-value">{(prediction.probability * 100).toFixed(0)}%</div>
						</div>
					</div>

					<div class="scenario">
						<div class="scenario-text">{prediction.scenario}</div>
					</div>

					<div class="reasoning">
						<div class="reasoning-label">Analysis:</div>
						<div class="reasoning-text">{prediction.reasoning}</div>
					</div>

					{#if prediction.related_events && prediction.related_events.length > 0}
						<div class="related-events">
							<div class="related-label">Supporting Evidence:</div>
							<ul class="events-list">
								{#each prediction.related_events as event}
									<li>{event}</li>
								{/each}
							</ul>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{:else if predictions && predictions.length === 0}
		<div class="empty">No predictions available for this story.</div>
	{:else}
		<div class="loading">Generating forecasts...</div>
	{/if}
</div>

<style>
	.forecast-dashboard {
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

	.predictions {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.prediction {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		padding: var(--spacing-md);
	}

	.prediction-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-sm);
		flex-wrap: wrap;
		gap: var(--spacing-sm);
	}

	.timeframe-badge {
		padding: var(--spacing-xs) var(--spacing-sm);
		border-radius: 20px;
		color: white;
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.probability {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
	}

	.probability-label {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
	}

	.probability-value {
		font-family: var(--font-mono);
		font-size: 1rem;
		font-weight: 700;
	}

	.probability.high .probability-value {
		color: #22c55e;
	}

	.probability.medium .probability-value {
		color: #f59e0b;
	}

	.probability.low .probability-value {
		color: #94a3b8;
	}

	.scenario {
		margin-bottom: var(--spacing-sm);
	}

	.scenario-text {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.5;
	}

	.reasoning {
		margin-bottom: var(--spacing-sm);
	}

	.reasoning-label, .related-label {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
		margin-bottom: 4px;
	}

	.reasoning-text {
		font-size: 0.875rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.related-events {
		padding-top: var(--spacing-sm);
		border-top: 1px solid var(--color-border);
	}

	.events-list {
		margin: 0;
		padding-left: var(--spacing-lg);
		font-size: 0.8125rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.events-list li {
		margin-bottom: 4px;
	}

	.loading, .empty {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-light);
		font-style: italic;
	}
</style>
