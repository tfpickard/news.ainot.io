<script lang="ts">
	export let data: any;

	let hoveredPoint: any = null;

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function getPercentage(value: number): string {
		return `${(value * 100).toFixed(1)}%`;
	}
</script>

<div class="sentiment-chart">
	{#if data && data.positive_trend.length > 0}
		<div class="chart-container">
			<div class="legend">
				<div class="legend-item positive">
					<span class="color-box"></span>
					<span>Positive</span>
				</div>
				<div class="legend-item neutral">
					<span class="color-box"></span>
					<span>Neutral</span>
				</div>
				<div class="legend-item negative">
					<span class="color-box"></span>
					<span>Negative</span>
				</div>
			</div>

			<div class="chart-area">
				{#each data.overall_trend as point, i}
					{@const positive = data.positive_trend[i]?.value || 0}
					{@const neutral = data.neutral_trend[i]?.value || 0}
					{@const negative = data.negative_trend[i]?.value || 0}
					<div
						class="bar-group"
						on:mouseenter={() => (hoveredPoint = { ...point, index: i })}
						on:mouseleave={() => (hoveredPoint = null)}
						role="button"
						tabindex={i}
					>
						<div class="stacked-bar">
							<div class="bar-segment positive" style="height: {positive * 100}%"></div>
							<div class="bar-segment neutral" style="height: {neutral * 100}%"></div>
							<div class="bar-segment negative" style="height: {negative * 100}%"></div>
						</div>
						{#if i % Math.ceil(data.overall_trend.length / 10) === 0}
							<div class="bar-label">{formatDate(point.timestamp).split(',')[0]}</div>
						{/if}
					</div>
				{/each}
			</div>

			{#if hoveredPoint}
				<div class="tooltip" style="left: {(hoveredPoint.index / data.overall_trend.length) * 100}%">
					<div class="tooltip-header">{formatDate(hoveredPoint.timestamp)}</div>
					<div class="tooltip-sentiment">{hoveredPoint.sentiment}</div>
					<div class="tooltip-scores">
						<div class="score-row positive">
							Positive: {getPercentage(data.positive_trend[hoveredPoint.index].value)}
						</div>
						<div class="score-row neutral">
							Neutral: {getPercentage(data.neutral_trend[hoveredPoint.index].value)}
						</div>
						<div class="score-row negative">
							Negative: {getPercentage(data.negative_trend[hoveredPoint.index].value)}
						</div>
					</div>
				</div>
			{/if}
		</div>

		<div class="stats-summary">
			<div class="stat">
				<span class="stat-label">Avg Positive:</span>
				<span class="stat-value positive">
					{getPercentage(
						data.positive_trend.reduce((sum: number, p: any) => sum + p.value, 0) /
							data.positive_trend.length
					)}
				</span>
			</div>
			<div class="stat">
				<span class="stat-label">Avg Neutral:</span>
				<span class="stat-value neutral">
					{getPercentage(
						data.neutral_trend.reduce((sum: number, p: any) => sum + p.value, 0) /
							data.neutral_trend.length
					)}
				</span>
			</div>
			<div class="stat">
				<span class="stat-label">Avg Negative:</span>
				<span class="stat-value negative">
					{getPercentage(
						data.negative_trend.reduce((sum: number, p: any) => sum + p.value, 0) /
							data.negative_trend.length
					)}
				</span>
			</div>
		</div>
	{:else}
		<div class="no-data">No sentiment data available for this time range</div>
	{/if}
</div>

<style>
	.sentiment-chart {
		padding: 1rem 0;
	}

	.legend {
		display: flex;
		gap: 1.5rem;
		margin-bottom: 1.5rem;
		justify-content: center;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.9rem;
	}

	.color-box {
		width: 20px;
		height: 12px;
		border-radius: 2px;
	}

	.positive .color-box {
		background: #10b981;
	}

	.neutral .color-box {
		background: #6b7280;
	}

	.negative .color-box {
		background: #ef4444;
	}

	.chart-container {
		position: relative;
		background: var(--bg-primary);
		border-radius: 8px;
		padding: 2rem 1rem;
		min-height: 300px;
	}

	.chart-area {
		display: flex;
		align-items: flex-end;
		gap: 2px;
		height: 250px;
		padding: 1rem 0;
	}

	.bar-group {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.bar-group:hover {
		opacity: 0.8;
	}

	.stacked-bar {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column-reverse;
		border-radius: 2px 2px 0 0;
		overflow: hidden;
	}

	.bar-segment {
		width: 100%;
		transition: all 0.3s ease;
	}

	.bar-segment.positive {
		background: linear-gradient(180deg, #10b981 0%, #059669 100%);
	}

	.bar-segment.neutral {
		background: linear-gradient(180deg, #6b7280 0%, #4b5563 100%);
	}

	.bar-segment.negative {
		background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
	}

	.bar-label {
		font-size: 0.7rem;
		color: var(--text-secondary);
		margin-top: 0.5rem;
		transform: rotate(-45deg);
		white-space: nowrap;
	}

	.tooltip {
		position: absolute;
		bottom: calc(100% + 10px);
		transform: translateX(-50%);
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 8px;
		padding: 1rem;
		min-width: 200px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
		z-index: 10;
		pointer-events: none;
	}

	.tooltip-header {
		font-weight: 600;
		margin-bottom: 0.5rem;
		font-size: 0.9rem;
		color: var(--text-primary);
	}

	.tooltip-sentiment {
		text-transform: capitalize;
		font-weight: 700;
		margin-bottom: 0.75rem;
		color: var(--text-primary);
	}

	.tooltip-scores {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.score-row {
		font-size: 0.85rem;
		display: flex;
		justify-content: space-between;
		padding: 0.25rem 0;
	}

	.score-row.positive {
		color: #10b981;
	}

	.score-row.neutral {
		color: #6b7280;
	}

	.score-row.negative {
		color: #ef4444;
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
	}

	.stat-label {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.stat-value {
		font-size: 1.4rem;
		font-weight: 700;
	}

	.stat-value.positive {
		color: #10b981;
	}

	.stat-value.neutral {
		color: #6b7280;
	}

	.stat-value.negative {
		color: #ef4444;
	}

	.no-data {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
	}

	@media (max-width: 768px) {
		.chart-area {
			height: 200px;
		}

		.bar-label {
			font-size: 0.6rem;
		}

		.stats-summary {
			gap: 1rem;
		}

		.stat-value {
			font-size: 1.2rem;
		}
	}
</style>
