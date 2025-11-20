<script lang="ts">
	export let data: any;

	// Scale font sizes based on frequency
	function getFontSize(count: number, max: number): number {
		const min = 0.8;
		const maxSize = 3;
		const scale = (count / max) * (maxSize - min) + min;
		return scale;
	}

	function getColor(index: number): string {
		const colors = [
			'#3b82f6',
			'#8b5cf6',
			'#ec4899',
			'#f59e0b',
			'#10b981',
			'#06b6d4',
			'#6366f1',
			'#f97316'
		];
		return colors[index % colors.length];
	}

	let maxCount = 0;
	if (data && data.keywords.length > 0) {
		maxCount = Math.max(...data.keywords.map((k: any) => k.count));
	}
</script>

<div class="keyword-cloud">
	{#if data && data.keywords.length > 0}
		<div class="cloud-container">
			{#each data.keywords as keyword, i}
				<div
					class="keyword-item"
					style="font-size: {getFontSize(keyword.count, maxCount)}rem; color: {getColor(i)}"
					title="{keyword.keyword} (appears in {keyword.count} stories)"
				>
					{keyword.keyword}
				</div>
			{/each}
		</div>

		<div class="cloud-stats">
			<div class="stat">
				<span class="label">Total Keywords:</span>
				<span class="value">{data.total_keywords}</span>
			</div>
			<div class="stat">
				<span class="label">Most Frequent:</span>
				<span class="value">{data.keywords[0]?.keyword || 'N/A'}</span>
				<span class="count">({data.keywords[0]?.count || 0} stories)</span>
			</div>
		</div>
	{:else}
		<div class="no-data">No keyword data available for this time range</div>
	{/if}
</div>

<style>
	.keyword-cloud {
		padding: 1rem 0;
	}

	.cloud-container {
		background: var(--bg-primary);
		border-radius: 8px;
		padding: 2rem;
		min-height: 300px;
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		align-items: center;
		justify-content: center;
	}

	.keyword-item {
		font-weight: 700;
		cursor: pointer;
		transition: all 0.2s ease;
		opacity: 0.9;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
	}

	.keyword-item:hover {
		opacity: 1;
		transform: scale(1.1);
		background: var(--bg-secondary);
	}

	.cloud-stats {
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
		gap: 0.5rem;
		align-items: baseline;
		flex-wrap: wrap;
	}

	.stat .label {
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.stat .value {
		font-size: 1.1rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.stat .count {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.no-data {
		text-align: center;
		padding: 3rem;
		color: var(--text-secondary);
	}

	@media (max-width: 768px) {
		.cloud-container {
			padding: 1rem;
			min-height: 200px;
			gap: 0.5rem;
		}

		.keyword-item {
			font-size: calc(var(--font-size, 1rem) * 0.8) !important;
		}

		.cloud-stats {
			flex-direction: column;
			align-items: center;
		}
	}
</style>
