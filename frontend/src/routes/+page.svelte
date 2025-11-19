<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api, type StoryVersion, type StoryVersionSummary } from '$lib/api';
	import { wsClient } from '$lib/ws';

	interface GeneratedImage {
		id: number;
		created_at: string;
		story_version_id: number;
		prompt: string;
		image_url: string;
		revised_prompt: string | null;
		model: string;
		size: string;
		quality: string;
	}

	let currentStory: StoryVersion | null = null;
	let historyStories: StoryVersionSummary[] = [];
	let latestImage: GeneratedImage | null = null;
	let loading = true;
	let error: string | null = null;
	let hasNewUpdate = false;
	let autoScroll = true;
	let loadingMore = false;
	let hasMore = true;

	// Subscribe to WebSocket stores
	let wsStatus = 'disconnected';
	let wsStory: StoryVersion | null = null;

	const unsubStatus = wsClient.status.subscribe((value) => {
		wsStatus = value;
	});

	const unsubStory = wsClient.latestStory.subscribe((value) => {
		wsStory = value;
		if (wsStory && currentStory?.id !== wsStory.id) {
			currentStory = wsStory;
			hasNewUpdate = true;

			// Auto-scroll to top if enabled
			if (autoScroll) {
				window.scrollTo({ top: 0, behavior: 'smooth' });
				hasNewUpdate = false;
			}
		}
	});

	const unsubNewUpdate = wsClient.hasNewUpdate.subscribe((value) => {
		hasNewUpdate = value;
	});

	onMount(async () => {
		// Load initial data via REST
		try {
			currentStory = await api.getCurrentStory();
			historyStories = await api.getStoryHistory(10, 0);

			// Load latest image
			try {
				const imageResponse = await fetch('/api/images/latest');
				if (imageResponse.ok) {
					latestImage = await imageResponse.json();
				}
			} catch (e) {
				console.log('No images available yet');
			}

			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load story';
			loading = false;
		}

		// Connect WebSocket
		wsClient.connect();
	});

	onDestroy(() => {
		unsubStatus();
		unsubStory();
		unsubNewUpdate();
		wsClient.disconnect();
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

	function dismissUpdate() {
		hasNewUpdate = false;
		wsClient.clearNewUpdate();
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function loadMore() {
		if (loadingMore || !hasMore) return;

		loadingMore = true;
		try {
			const offset = historyStories.length;
			const newStories = await api.getStoryHistory(10, offset);

			if (newStories.length === 0) {
				hasMore = false;
			} else {
				// Filter out the current story if it appears in history
				const filtered = newStories.filter(s => s.id !== currentStory?.id);
				historyStories = [...historyStories, ...filtered];
			}
		} catch (err) {
			console.error('Error loading more stories:', err);
		} finally {
			loadingMore = false;
		}
	}

	// Infinite scroll detection
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
	<title>Singl News - The Continuous Global Narrative</title>
</svelte:head>

<div class="page">
	<div class="container">
		{#if loading}
			<div class="loading">Loading the story...</div>
		{:else if error}
			<div class="error">
				<p>{error}</p>
				<button on:click={() => window.location.reload()}>Retry</button>
			</div>
		{:else}
			<!-- New update notification -->
			{#if hasNewUpdate && !autoScroll}
				<div class="update-notification">
					<p>New update available</p>
					<button on:click={dismissUpdate}>View Now</button>
				</div>
			{/if}

			<!-- Current Story -->
			{#if currentStory}
				<article class="story current-story">
					<div class="story-meta">
						<time datetime={currentStory.created_at}>
							Updated: {formatDate(currentStory.created_at)}
						</time>
						<span class="connection-status" class:connected={wsStatus === 'connected'}>
							{wsStatus === 'connected' ? '● Live' : '○ Offline'}
						</span>
					</div>

					<div class="story-content">
						{@html currentStory.full_text.replace(/\n\n/g, '</p><p>').replace(/^(.*)$/, '<p>$1</p>')}
					</div>
				</article>

				<!-- Latest AI-Generated Image -->
				{#if latestImage}
					<div class="generated-image-section">
						<h2 class="image-section-title">Visual Interpretation</h2>
						<div class="image-container">
							<img src={latestImage.image_url} alt="AI-generated visualization of the story" class="story-image" />
							<p class="image-caption">
								AI-generated visualization • {formatDate(latestImage.created_at)}
							</p>
						</div>
					</div>
				{/if}
			{/if}

			<!-- History -->
			{#if historyStories.length > 0}
				<div class="history-section">
					<h2 class="section-title">Earlier Coverage</h2>

					{#each historyStories as story}
						<article class="story history-story">
							<div class="story-meta">
								<time datetime={story.created_at}>
									{formatDate(story.created_at)}
								</time>
							</div>
							<div class="story-summary">
								<p>{story.preview}</p>
								<a href="/story/{story.id}" class="read-more">Read full version →</a>
							</div>
						</article>
					{/each}

					{#if hasMore}
						<div class="load-more">
							{#if loadingMore}
								<p class="loading-text">Loading earlier coverage...</p>
							{:else}
								<button on:click={loadMore} class="load-more-btn">Load Earlier Coverage</button>
							{/if}
						</div>
					{:else}
						<p class="end-message">You have reached the beginning of THE STORY.</p>
					{/if}
				</div>
			{/if}

			<!-- Settings -->
			<div class="settings">
				<label>
					<input type="checkbox" bind:checked={autoScroll} />
					Auto-scroll to latest updates
				</label>
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

	.update-notification {
		position: fixed;
		top: 20px;
		left: 50%;
		transform: translateX(-50%);
		background: var(--color-accent);
		color: white;
		padding: var(--spacing-sm) var(--spacing-md);
		border-radius: 4px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		z-index: 1000;
		font-family: var(--font-sans);
		font-size: 0.875rem;
	}

	.update-notification button {
		background: white;
		color: var(--color-accent);
		border: none;
		padding: 4px 12px;
		border-radius: 3px;
		cursor: pointer;
		font-weight: 600;
	}

	.story {
		margin-bottom: var(--spacing-xl);
	}

	.current-story {
		border-bottom: 2px solid var(--color-text);
		padding-bottom: var(--spacing-xl);
	}

	.story-meta {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-md);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.connection-status {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.connection-status.connected {
		color: #22c55e;
	}

	.story-content :global(p) {
		margin-bottom: var(--spacing-md);
		text-align: justify;
	}

	.history-section {
		margin-top: var(--spacing-xl);
		padding-top: var(--spacing-xl);
		border-top: 1px solid var(--color-border);
	}

	.section-title {
		font-size: 1.25rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-lg);
	}

	.history-story {
		padding: var(--spacing-md) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.story-summary p {
		font-size: 0.95rem;
		color: var(--color-text-light);
	}

	.read-more {
		display: inline-block;
		margin-top: var(--spacing-sm);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
	}

	.load-more {
		text-align: center;
		padding: var(--spacing-lg) 0;
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
	}

	.settings {
		margin-top: var(--spacing-xl);
		padding: var(--spacing-md);
		background: var(--color-highlight);
		border-radius: 4px;
		font-family: var(--font-sans);
		font-size: 0.875rem;
	}

	.settings label {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
		cursor: pointer;
	}

	/* Generated Image Section */
	.generated-image-section {
		margin-top: var(--spacing-xl);
		padding-top: var(--spacing-xl);
		border-top: 2px solid var(--color-border);
	}

	.image-section-title {
		font-size: 1.25rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-md);
		text-align: center;
	}

	.image-container {
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		overflow: hidden;
		max-width: 100%;
	}

	.story-image {
		width: 100%;
		height: auto;
		display: block;
	}

	.image-caption {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		color: var(--color-text-light);
		text-align: center;
		padding: var(--spacing-sm);
		font-style: italic;
	}
</style>
