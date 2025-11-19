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

	function getAbsurdityColor(score: number): string {
		if (score < 3) return '#10b981'; // Low absurdity - green
		if (score < 5) return '#f59e0b'; // Medium - yellow
		if (score < 7) return '#f97316'; // High - orange
		return '#ef4444'; // Extreme - red
	}

	function getAbsurdityLabel(score: number): string {
		if (score < 3) return 'Mild';
		if (score < 5) return 'Moderate';
		if (score < 7) return 'High';
		return 'Extreme';
	}
</script>

<div class="absurdity-chart">
	{#if data && data.data_points && data.data_points.length > 0}
		<div class="chart-container">
			<div class="chart-area">
				<svg class="line-chart" viewBox="0 0 800 300" preserveAspectRatio="xMidYMid meet">
					<!-- Grid lines -->
					{#each [0, 2.5, 5, 7.5, 10] as gridValue}
						<line
							x1="0"
							y1={300 - (gridValue / 10) * 280}
							x2="800"
							y2={300 - (gridValue / 10) * 280}
							stroke="var(--border-color)"
							stroke-width="1"
							stroke-dasharray="4"
						/>
						<text
							x="5"
							y={300 - (gridValue / 10) * 280 - 5}
							fill="var(--text-secondary)"
							font-size="12"
						>
							{gridValue}
						</text>
					{/each}

					<!-- Line path -->
					<path
						d="M {data.data_points
							.map(
								(point, i) =>
									`${(i / (data.data_points.length - 1)) * 800} ${300 - (point.absurdity_score / 10) * 280}`
							)
							.join(' L ')}"
						fill="none"
						stroke="url(#absurdity-gradient)"
						stroke-width="3"
						stroke-linecap="round"
					/>

					<!-- Data points -->
					{#each data.data_points as point, i}
						<circle
							cx={(i / (data.data_points.length - 1)) * 800}
							cy={300 - (point.absurdity_score / 10) * 280}
							r="5"
							fill={getAbsurdityColor(point.absurdity_score)}
							stroke="white"
							stroke-width="2"
							on:mouseenter={() => (hoveredPoint = { ...point, index: i })}
							on:mouseleave={() => (hoveredPoint = null)}
							style="cursor: pointer;"
						/>
					{/each}

					<!-- Gradient definition -->
					<defs>
						<linearGradient id="absurdity-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
							<stop offset="0%" stop-color="#10b981" />
							<stop offset="50%" stop-color="#f59e0b" />
							<stop offset="100%" stop-color="#ef4444" />
						</linearGradient>
					</defs>
				</svg>
			</div>

			{#if hoveredPoint}
				<div class="tooltip">
					<div class="tooltip-header">{formatDate(hoveredPoint.timestamp)}</div>
					<div class="absurdity-score">
						<span class="score-value" style="color: {getAbsurdityColor(hoveredPoint.absurdity_score)}">
							{hoveredPoint.absurdity_score}/10
						</span>
						<span class="score-label">
							{getAbsurdityLabel(hoveredPoint.absurdity_score)}
						</span>
					</div>
					{#if hoveredPoint.top_quote}
						<div class="quote">"{hoveredPoint.top_quote}"</div>
					{/if}
				</div>
			{/if}
		</div>

		<div class="stats-summary">
			<div class="stat">
				<span class="stat-label">Average Absurdity:</span>
				<span class="stat-value" style="color: {getAbsurdityColor(data.average_score)}">
					{data.average_score}/10
				</span>
			</div>
			<div class="stat">
				<span class="stat-label">Peak Absurdity:</span>
				<span class="stat-value" style="color: {getAbsurdityColor(data.peak_absurdity.absurdity_score)}">
					{data.peak_absurdity.absurdity_score}/10
				</span>
				<span class="stat-date">
					{formatDate(data.peak_absurdity.timestamp)}
				</span>
			</div>
			<div class="stat">
				<span class="stat-label">Data Points:</span>
				<span class="stat-value">{data.data_points.length}</span>
			</div>
		</div>
	{:else}
		<div class="no-data">No absurdity data available for this time range</div>
	{/if}
</div>

<style>
	.absurdity-chart {
		padding: 1rem 0;
	}

	.chart-container {
		position: relative;
		background: var(--bg-primary);
		border-radius: 8px;
		padding: 2rem 1rem;
	}

	.chart-area {
		width: 100%;
		min-height: 300px;
	}

	.line-chart {
		width: 100%;
		height: 100%;
	}

	.tooltip {
		position: fixed;
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 8px;
		padding: 1rem;
		max-width: 300px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
		z-index: 1000;
		pointer-events: none;
		transform: translate(-50%, -100%);
		margin-top: -10px;
	}

	.tooltip-header {
		font-weight: 600;
		margin-bottom: 0.5rem;
		font-size: 0.9rem;
		color: var(--text-primary);
	}

	.absurdity-score {
		display: flex;
		gap: 0.5rem;
		align-items: baseline;
		margin-bottom: 0.75rem;
	}

	.score-value {
		font-size: 1.5rem;
		font-weight: 700;
	}

	.score-label {
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.quote {
		font-size: 0.85rem;
		color: var(--text-secondary);
		font-style: italic;
		margin-top: 0.5rem;
		padding-top: 0.5rem;
		border-top: 1px solid var(--border-color);
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
		font-size: 1.4rem;
		font-weight: 700;
	}

	.stat-date {
		font-size: 0.75rem;
		color: var(--text-secondary);
	}

	.no-data {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
	}

	@media (max-width: 768px) {
		.chart-area {
			min-height: 200px;
		}

		.stats-summary {
			gap: 1rem;
		}

		.stat-value {
			font-size: 1.2rem;
		}
	}
</style>
