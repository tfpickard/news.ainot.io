<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type SourceDetail } from '$lib/api';

	export let storyId: number;
	export let compact: boolean = false;

	let sources: SourceDetail[] = [];
	let loading = true;
	let error: string | null = null;
	let showAll = false;

	$: displayedSources = showAll || compact ? sources : sources.slice(0, 10);
	$: hasMore = sources.length > 10;

	onMount(async () => {
		try {
			sources = await api.getStorySources(storyId);
			loading = false;
		} catch (err) {
			console.error('Failed to load sources:', err);
			error = err instanceof Error ? err.message : 'Failed to load sources';
			loading = false;
		}
	});

	function formatDate(dateStr: string | undefined): string {
		if (!dateStr) return '';
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function getDomain(url: string): string {
		try {
			const urlObj = new URL(url);
			return urlObj.hostname.replace('www.', '');
		} catch {
			return url;
		}
	}
</script>

{#if !loading && !error && sources.length > 0}
	<aside class="source-tracker" class:compact>
		<h3 class="source-header">
			{#if compact}
				<span class="source-count">{sources.length} Sources</span>
			{:else}
				News Sources Referenced
			{/if}
		</h3>

		{#if !compact}
			<p class="source-description">
				This unified narrative was synthesized from {sources.length} information source{sources.length !== 1 ? 's' : ''}.
				{#if hasMore && !showAll}
					<button class="show-all-btn" on:click={() => (showAll = true)}>
						Show all →
					</button>
				{/if}
			</p>
		{/if}

		<ul class="source-list">
			{#each displayedSources as source (source.id)}
				<li class="source-item">
					<div class="source-main">
						<span class="source-name">{source.source}</span>
						<span class="source-title">{source.title}</span>
					</div>
					<div class="source-meta">
						{#if source.published_at}
							<span class="source-date">{formatDate(source.published_at)}</span>
						{/if}
						{#if source.link}
							<a
								href={source.link}
								target="_blank"
								rel="noopener noreferrer"
								class="source-link"
								title="View original article"
							>
								{getDomain(source.link)} ↗
							</a>
						{/if}
					</div>
				</li>
			{/each}
		</ul>

		{#if !compact && hasMore && showAll}
			<button class="show-less-btn" on:click={() => (showAll = false)}>
				← Show less
			</button>
		{/if}
	</aside>
{/if}

<style>
	.source-tracker {
		margin: var(--spacing-xl) 0;
		padding: var(--spacing-lg);
		background: var(--color-highlight);
		border-left: 4px solid var(--color-text);
		border-radius: 4px;
	}

	.source-tracker.compact {
		padding: var(--spacing-md);
		background: transparent;
		border-left: 3px solid var(--color-text-light);
	}

	.source-header {
		font-family: var(--font-sans);
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-sm);
		font-weight: 700;
	}

	.source-count {
		color: var(--color-text-light);
		font-size: 0.875rem;
	}

	.source-description {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-md);
		line-height: 1.5;
	}

	.show-all-btn,
	.show-less-btn {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		background: none;
		border: none;
		color: var(--color-text);
		cursor: pointer;
		text-decoration: underline;
		padding: 0;
		margin-left: var(--spacing-xs);
	}

	.show-all-btn:hover,
	.show-less-btn:hover {
		color: var(--color-text-light);
	}

	.show-less-btn {
		display: block;
		margin-top: var(--spacing-md);
	}

	.source-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.source-item {
		padding: var(--spacing-sm) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.source-item:last-child {
		border-bottom: none;
	}

	.source-main {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin-bottom: 4px;
	}

	.source-name {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text);
	}

	.source-title {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text);
		line-height: 1.4;
	}

	.source-meta {
		display: flex;
		gap: var(--spacing-sm);
		align-items: center;
		font-family: var(--font-sans);
		font-size: 0.75rem;
	}

	.source-date {
		color: var(--color-text-light);
	}

	.source-link {
		color: var(--color-text);
		text-decoration: none;
		font-weight: 600;
		transition: color 0.2s;
	}

	.source-link:hover {
		color: var(--color-text-light);
		text-decoration: underline;
	}

	.compact .source-list {
		font-size: 0.875rem;
	}

	.compact .source-item {
		padding: 6px 0;
	}

	.compact .source-title {
		font-size: 0.8125rem;
	}

	@media (max-width: 768px) {
		.source-tracker {
			padding: var(--spacing-md);
		}

		.source-meta {
			flex-direction: column;
			align-items: flex-start;
			gap: 4px;
		}
	}
</style>
