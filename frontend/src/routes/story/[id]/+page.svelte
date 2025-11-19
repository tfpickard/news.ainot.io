<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { api, type StoryVersion } from '$lib/api';

	let story: StoryVersion | null = null;
	let loading = true;
	let error: string | null = null;

	$: storyId = parseInt($page.params.id);

	onMount(async () => {
		try {
			story = await api.getStoryById(storyId);
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load story';
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			timeZone: 'UTC',
			timeZoneName: 'short'
		});
	}
</script>

<svelte:head>
	<title>{story?.summary || 'Story'} - Singl News</title>
</svelte:head>

<div class="page">
	<div class="container">
		{#if loading}
			<div class="loading">Loading story...</div>
		{:else if error}
			<div class="error">
				<p>{error}</p>
				<a href="/history" class="back-link">← Back to Archive</a>
			</div>
		{:else if story}
			<div class="story-header">
				<a href="/history" class="back-link">← Back to Archive</a>
				<time class="story-date" datetime={story.created_at}>
					{formatDate(story.created_at)}
				</time>
			</div>

			<article class="story">
				<h2 class="story-summary">{story.summary}</h2>

				<div class="story-content">
					{@html story.full_text.replace(/\n\n/g, '</p><p>').replace(/^(.*)$/, '<p>$1</p>')}
				</div>

				{#if story.sources_snapshot?.feed_items?.length > 0}
					<aside class="sources">
						<h3>Sources Referenced</h3>
						<p class="source-count">
							{story.sources_snapshot.item_count} information source{story.sources_snapshot.item_count !== 1 ? 's' : ''} incorporated
						</p>
					</aside>
				{/if}
			</article>

			<div class="story-footer">
				<a href="/" class="action-link">View Current Story →</a>
			</div>
		{/if}
	</div>
</div>

<style>
	.page {
		min-height: 60vh;
	}

	.loading,
	.error {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-light);
	}

	.story-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-lg);
		padding-bottom: var(--spacing-md);
		border-bottom: 1px solid var(--color-border);
	}

	.back-link {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
	}

	.story-date {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.story {
		margin-bottom: var(--spacing-xl);
	}

	.story-summary {
		font-size: 1.5rem;
		margin-bottom: var(--spacing-lg);
		padding-bottom: var(--spacing-md);
		border-bottom: 2px solid var(--color-text);
	}

	.story-content :global(p) {
		margin-bottom: var(--spacing-md);
		text-align: justify;
	}

	.sources {
		margin-top: var(--spacing-xl);
		padding: var(--spacing-md);
		background: var(--color-highlight);
		border-left: 3px solid var(--color-text-light);
	}

	.sources h3 {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-xs);
	}

	.source-count {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
	}

	.story-footer {
		text-align: center;
		padding: var(--spacing-lg) 0;
		border-top: 1px solid var(--color-border);
	}

	.action-link {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		display: inline-block;
		padding: var(--spacing-sm) var(--spacing-md);
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 4px;
		transition: all 0.2s;
	}

	.action-link:hover {
		background: var(--color-border);
		text-decoration: none;
	}
</style>
