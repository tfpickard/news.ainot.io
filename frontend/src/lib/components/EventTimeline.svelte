<script lang="ts">
	export let events: Array<{
		title: string;
		description: string;
		timestamp: string | null;
		category: string;
		importance: number;
	}> | null = null;

	function getCategoryColor(category: string): string {
		const colors: Record<string, string> = {
			political: '#3b82f6',
			economic: '#22c55e',
			social: '#a855f7',
			conflict: '#ef4444',
			disaster: '#f97316',
			technology: '#06b6d4',
			other: '#94a3b8'
		};
		return colors[category] || colors.other;
	}

	function getImportanceSize(importance: number): string {
		if (importance >= 8) return 'large';
		if (importance >= 5) return 'medium';
		return 'small';
	}
</script>

<div class="event-timeline">
	<h3 class="dashboard-title">Story Graph / Event Map</h3>

	{#if events && events.length > 0}
		<div class="timeline">
			{#each events as event, i}
				<div class="event-item">
					<div class="event-marker {getImportanceSize(event.importance)}"
					     style="background: {getCategoryColor(event.category)}">
						<div class="importance-badge">{event.importance}</div>
					</div>
					<div class="event-content">
						<div class="event-header">
							<div class="event-category" style="color: {getCategoryColor(event.category)}">
								{event.category.toUpperCase()}
							</div>
							{#if event.timestamp}
								<div class="event-time">{new Date(event.timestamp).toLocaleDateString()}</div>
							{/if}
						</div>
						<div class="event-title">{event.title}</div>
						<div class="event-description">{event.description}</div>
					</div>
				</div>
			{/each}
		</div>
	{:else if events && events.length === 0}
		<div class="empty">No events extracted from this story.</div>
	{:else}
		<div class="loading">Extracting events...</div>
	{/if}
</div>

<style>
	.event-timeline {
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

	.timeline {
		position: relative;
		padding-left: var(--spacing-lg);
	}

	.timeline::before {
		content: '';
		position: absolute;
		left: 15px;
		top: 0;
		bottom: 0;
		width: 2px;
		background: var(--color-border);
	}

	.event-item {
		position: relative;
		display: flex;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-lg);
	}

	.event-marker {
		position: relative;
		z-index: 1;
		flex-shrink: 0;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-left: -12px;
	}

	.event-marker.small {
		width: 24px;
		height: 24px;
	}

	.event-marker.medium {
		width: 32px;
		height: 32px;
	}

	.event-marker.large {
		width: 40px;
		height: 40px;
	}

	.importance-badge {
		color: white;
		font-family: var(--font-mono);
		font-size: 0.75rem;
		font-weight: 700;
	}

	.event-content {
		flex: 1;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		padding: var(--spacing-md);
	}

	.event-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-xs);
		flex-wrap: wrap;
		gap: var(--spacing-xs);
	}

	.event-category {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.event-time {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--color-text-light);
	}

	.event-title {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--color-text);
		margin-bottom: var(--spacing-xs);
		line-height: 1.4;
	}

	.event-description {
		font-size: 0.875rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.loading, .empty {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-light);
		font-style: italic;
	}
</style>
