<script lang="ts">
	export let biasScore: {
		political_lean: string;
		lean_score: number;
		loaded_language_count: number;
		emotional_language_score: number;
	} | null = null;

	export let biasIndicators: {
		loaded_terms?: string[];
		omissions?: string[];
		framing?: string;
	} | null = null;

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

	function getLeanPosition(score: number): number {
		// Convert -1 to 1 scale to 0-100%
		return ((score + 1) / 2) * 100;
	}
</script>

<div class="bias-dashboard">
	<h3 class="dashboard-title">Bias Analysis</h3>

	{#if biasScore}
		<div class="bias-summary">
			<div class="political-lean">
				<div class="lean-label">Political Lean</div>
				<div class="lean-badge" style="background: {getLeanColor(biasScore.political_lean)}">
					{biasScore.political_lean.replace('-', ' ').toUpperCase()}
				</div>
			</div>

			<div class="lean-spectrum">
				<div class="spectrum-bar">
					<div class="spectrum-marker" style="left: {getLeanPosition(biasScore.lean_score)}%"></div>
				</div>
				<div class="spectrum-labels">
					<span>Left</span>
					<span>Center</span>
					<span>Right</span>
				</div>
			</div>
		</div>

		<div class="bias-metrics">
			<div class="metric">
				<div class="metric-label">Loaded Language</div>
				<div class="metric-value">{biasScore.loaded_language_count} terms</div>
			</div>
			<div class="metric">
				<div class="metric-label">Emotional Language</div>
				<div class="metric-value">{(biasScore.emotional_language_score * 100).toFixed(0)}%</div>
			</div>
		</div>

		{#if biasIndicators}
			{#if biasIndicators.loaded_terms && biasIndicators.loaded_terms.length > 0}
				<div class="indicators-section">
					<div class="section-title">Loaded Terms Found</div>
					<div class="term-list">
						{#each biasIndicators.loaded_terms as term}
							<span class="term-badge">{term}</span>
						{/each}
					</div>
				</div>
			{/if}

			{#if biasIndicators.framing}
				<div class="indicators-section">
					<div class="section-title">Framing Analysis</div>
					<p class="framing-text">{biasIndicators.framing}</p>
				</div>
			{/if}

			{#if biasIndicators.omissions && biasIndicators.omissions.length > 0}
				<div class="indicators-section">
					<div class="section-title">Potential Omissions</div>
					<ul class="omission-list">
						{#each biasIndicators.omissions as omission}
							<li>{omission}</li>
						{/each}
					</ul>
				</div>
			{/if}
		{/if}
	{:else}
		<div class="loading">Analyzing bias...</div>
	{/if}
</div>

<style>
	.bias-dashboard {
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

	.bias-summary {
		margin-bottom: var(--spacing-md);
	}

	.political-lean {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: var(--spacing-md);
	}

	.lean-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.lean-badge {
		padding: var(--spacing-xs) var(--spacing-md);
		border-radius: 20px;
		color: white;
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.lean-spectrum {
		margin-top: var(--spacing-md);
	}

	.spectrum-bar {
		position: relative;
		height: 12px;
		background: linear-gradient(90deg, #3b82f6, #94a3b8 50%, #ef4444);
		border-radius: 6px;
		margin-bottom: var(--spacing-xs);
	}

	.spectrum-marker {
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		width: 20px;
		height: 20px;
		background: var(--color-text);
		border: 3px solid var(--color-bg);
		border-radius: 50%;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	.spectrum-labels {
		display: flex;
		justify-content: space-between;
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
	}

	.bias-metrics {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-md);
		padding: var(--spacing-md);
		background: var(--color-bg);
		border-radius: 6px;
		border: 1px solid var(--color-border);
	}

	.metric {
		text-align: center;
	}

	.metric-label {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-xs);
	}

	.metric-value {
		font-family: var(--font-mono);
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text);
	}

	.indicators-section {
		margin-top: var(--spacing-md);
		padding-top: var(--spacing-md);
		border-top: 1px solid var(--color-border);
	}

	.section-title {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		margin-bottom: var(--spacing-sm);
		color: var(--color-text);
	}

	.term-list {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-xs);
	}

	.term-badge {
		display: inline-block;
		padding: 4px 8px;
		background: var(--color-accent);
		color: white;
		border-radius: 4px;
		font-family: var(--font-sans);
		font-size: 0.75rem;
	}

	.framing-text {
		font-size: 0.875rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.omission-list {
		margin: 0;
		padding-left: var(--spacing-lg);
		font-size: 0.875rem;
		color: var(--color-text-light);
		line-height: 1.5;
	}

	.loading {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-light);
		font-style: italic;
	}
</style>
