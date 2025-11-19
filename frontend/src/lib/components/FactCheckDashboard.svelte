<script lang="ts">
	export let factChecks: Array<{
		claim: string;
		verdict: string;
		confidence: number;
		explanation: string;
		sources: string[];
	}> | null = null;

	function getVerdictColor(verdict: string): string {
		switch (verdict) {
			case 'true': return '#22c55e';
			case 'false': return '#ef4444';
			case 'partially-true': return '#f59e0b';
			case 'unverified': return '#94a3b8';
			case 'misleading': return '#f97316';
			default: return '#94a3b8';
		}
	}

	function getVerdictIcon(verdict: string): string {
		switch (verdict) {
			case 'true': return '✓';
			case 'false': return '✗';
			case 'partially-true': return '≈';
			case 'unverified': return '?';
			case 'misleading': return '⚠';
			default: return '?';
		}
	}

	function formatVerdict(verdict: string): string {
		return verdict.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
	}
</script>

<div class="fact-check-dashboard">
	<h3 class="dashboard-title">Fact Checking</h3>

	{#if factChecks && factChecks.length > 0}
		<div class="fact-checks">
			{#each factChecks as check}
				<div class="fact-check">
					<div class="fact-header">
						<div class="verdict-badge" style="background: {getVerdictColor(check.verdict)}">
							<span class="verdict-icon">{getVerdictIcon(check.verdict)}</span>
							<span class="verdict-text">{formatVerdict(check.verdict)}</span>
						</div>
						<div class="confidence">
							<span class="confidence-label">Confidence:</span>
							<span class="confidence-value">{(check.confidence * 100).toFixed(0)}%</span>
						</div>
					</div>

					<div class="claim">
						<div class="claim-label">Claim:</div>
						<div class="claim-text">"{check.claim}"</div>
					</div>

					<div class="explanation">
						<div class="explanation-label">Analysis:</div>
						<div class="explanation-text">{check.explanation}</div>
					</div>

					{#if check.sources && check.sources.length > 0}
						<div class="sources">
							<div class="sources-label">Sources:</div>
							<ul class="sources-list">
								{#each check.sources as source}
									<li>{source}</li>
								{/each}
							</ul>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{:else if factChecks && factChecks.length === 0}
		<div class="empty">No verifiable claims found in this story.</div>
	{:else}
		<div class="loading">Checking facts...</div>
	{/if}
</div>

<style>
	.fact-check-dashboard {
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

	.fact-checks {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.fact-check {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		padding: var(--spacing-md);
	}

	.fact-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-sm);
		flex-wrap: wrap;
		gap: var(--spacing-sm);
	}

	.verdict-badge {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
		padding: var(--spacing-xs) var(--spacing-sm);
		border-radius: 20px;
		color: white;
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 700;
	}

	.verdict-icon {
		font-size: 1rem;
	}

	.verdict-text {
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.confidence {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
	}

	.confidence-value {
		font-weight: 700;
		color: var(--color-text);
	}

	.claim {
		margin-bottom: var(--spacing-sm);
	}

	.claim-label, .explanation-label, .sources-label {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
		margin-bottom: 4px;
	}

	.claim-text {
		font-size: 0.9rem;
		font-style: italic;
		color: var(--color-text);
		line-height: 1.5;
	}

	.explanation {
		margin-bottom: var(--spacing-sm);
	}

	.explanation-text {
		font-size: 0.875rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.sources {
		padding-top: var(--spacing-sm);
		border-top: 1px solid var(--color-border);
	}

	.sources-list {
		margin: 0;
		padding-left: var(--spacing-lg);
		font-size: 0.8125rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.sources-list li {
		margin-bottom: 4px;
	}

	.loading, .empty {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-light);
		font-style: italic;
	}
</style>
