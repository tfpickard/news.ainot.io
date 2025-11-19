<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type StoryVersionSummary } from '$lib/api';

	let stories: StoryVersionSummary[] = [];
	let loading = true;
	let error: string | null = null;
	let loadingMore = false;
	let hasMore = true;

	onMount(async () => {
		try {
			stories = await api.getStoryHistory(20, 0);
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load history';
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

	async function loadMore() {
		if (loadingMore || !hasMore) return;

		loadingMore = true;
		try {
			const offset = stories.length;
			const newStories = await api.getStoryHistory(20, offset);

			if (newStories.length === 0) {
				hasMore = false;
			} else {
				stories = [...stories, ...newStories];
			}
		} catch (err) {
			console.error('Error loading more stories:', err);
		} finally {
			loadingMore = false;
		}
	}

	function handleScroll() {
		if (loadingMore || !hasMore) return;

		const scrollPosition = window.innerHeight + window.scrollY;
		const threshold = document.documentElement.scrollHeight - 500;

		if (scrollPosition >= threshold) {
			loadMore();
		}
	}

	onMount(() => {
		window.addEventListener('scroll', handleScroll);
		return () => window.removeEventListener('scroll', handleScroll);
	});
</script>

<svelte:head>
	<title>Archive - Singl News</title>
</svelte:head>

<div class="page">
	<div class="container">
		<div class="page-header">
			<h1>Archive</h1>
			<p class="subtitle">Complete chronological record of THE STORY</p>
		</div>

		{#if loading}
			<div class="loading">Loading archive...</div>
		{:else if error}
			<div class="error">
				<p>{error}</p>
				<button on:click={() => window.location.reload()}>Retry</button>
			</div>
		{:else}
			<div class="story-list">
				{#each stories as story}
					<article class="story-item">
						<time class="story-date" datetime={story.created_at}>
							{formatDate(story.created_at)}
						</time>
						<h3 class="story-summary">{story.summary}</h3>
						<p class="story-preview">{story.preview}</p>
						<a href="/story/{story.id}" class="read-link">Read full version →</a>
					</article>
				{/each}
			</div>

			{#if hasMore}
				<div class="load-more">
					{#if loadingMore}
						<p class="loading-text">Loading earlier entries...</p>
					{:else}
						<button on:click={loadMore} class="load-more-btn">Load More</button>
					{/if}
				</div>
			{:else}
				<p class="end-message">You have reached the beginning of THE STORY.</p>
			{/if}
		{/if}
	</div>
</div>

<style>
	.page {
		min-height: 60vh;
	}

	.page-header {
		text-align: center;
		margin-bottom: var(--spacing-xl);
		padding-bottom: var(--spacing-lg);
		border-bottom: 2px solid var(--color-text);
	}

	.page-header h1 {
		font-size: 2.5rem;
		margin-bottom: var(--spacing-sm);
	}

	.subtitle {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
	}

	.loading,
	.error {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-light);
	}

	.error button {
		margin-top: var(--spacing-md);
		padding: var(--spacing-sm) var(--spacing-md);
		background: var(--color-accent);
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-family: var(--font-sans);
	}

	.story-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-lg);
	}

	.story-item {
		padding: var(--spacing-lg);
		border: 1px solid var(--color-border);
		border-radius: 4px;
		transition: all 0.2s;
	}

	.story-item:hover {
		border-color: var(--color-text-light);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.story-date {
		display: block;
		font-family: var(--font-sans);
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-sm);
	}

	.story-summary {
		font-size: 1.25rem;
		margin-bottom: var(--spacing-sm);
		color: var(--color-text);
	}

	.story-preview {
		font-size: 0.95rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-sm);
		line-height: 1.6;
	}

	.read-link {
		display: inline-block;
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
	}

	.load-more {
		text-align: center;
		padding: var(--spacing-lg) 0;
		margin-top: var(--spacing-lg);
	}

	.load-more-btn {
		padding: var(--spacing-sm) var(--spacing-md);
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 4px;
		cursor: pointer;
		font-family: var(--font-sans);
		font-size: 0.875rem;
		transition: all 0.2s;
	}

	.load-more-btn:hover {
		background: var(--color-border);
	}

	.loading-text {
		color: var(--color-text-light);
		font-family: var(--font-sans);
		font-size: 0.875rem;
	}

	.end-message {
		text-align: center;
		color: var(--color-text-light);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-style: italic;
		padding: var(--spacing-lg) 0;
		margin-top: var(--spacing-lg);
	}
</style>
