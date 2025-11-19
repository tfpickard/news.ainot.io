<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api, type StoryVersion } from '$lib/api';
	import { wsClient } from '$lib/ws';
	import SentimentDashboard from '$lib/components/SentimentDashboard.svelte';
	import BiasDashboard from '$lib/components/BiasDashboard.svelte';
	import FactCheckDashboard from '$lib/components/FactCheckDashboard.svelte';
	import ForecastDashboard from '$lib/components/ForecastDashboard.svelte';
	import EventTimeline from '$lib/components/EventTimeline.svelte';
	import CrossSourceDashboard from '$lib/components/CrossSourceDashboard.svelte';

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

	interface Analytics {
		story_version_id: number;
		created_at: string;
		overall_sentiment: string | null;
		sentiment_score: any;
		bias_score: any;
		bias_indicators: any;
		source_analysis: any[];
		fact_checks: any[];
		predictions: any[];
		events: any[];
	}

	interface StoryData {
		story: StoryVersion;
		image: GeneratedImage | null;
		analytics: Analytics | null;
	}

	let stories: StoryData[] = [];
	let loading = true;
	let error: string | null = null;
	let hasNewUpdate = false;
	let loadingMore = false;
	let hasMore = true;
	let offset = 0;

	// WebSocket state
	let wsStatus = 'disconnected';
	let wsStory: StoryVersion | null = null;

	// Unsubscribe functions (will be set in onMount)
	let unsubStatus: (() => void) | null = null;
	let unsubStory: (() => void) | null = null;
	let unsubNewUpdate: (() => void) | null = null;

	// Track expanded state for analytics sections
	let expandedAnalytics: Set<number> = new Set();

	function toggleAnalytics(storyId: number) {
		if (expandedAnalytics.has(storyId)) {
			expandedAnalytics.delete(storyId);
		} else {
			expandedAnalytics.add(storyId);
		}
		expandedAnalytics = expandedAnalytics; // Trigger reactivity
	}

	onMount(async () => {
		// Subscribe to WebSocket stores (browser-only)
		unsubStatus = wsClient.status.subscribe((value) => {
			wsStatus = value;
		});

		unsubStory = wsClient.latestStory.subscribe((value) => {
			wsStory = value;
			if (wsStory && (stories.length === 0 || stories[0].story.id !== wsStory.id)) {
				hasNewUpdate = true;
			}
		});

		unsubNewUpdate = wsClient.hasNewUpdate.subscribe((value) => {
			hasNewUpdate = value;
		});

		// Load initial stories
		await loadInitialStories();

		// Connect WebSocket
		wsClient.connect();

		// Set up infinite scroll
		window.addEventListener('scroll', handleScroll);
	});

	onDestroy(() => {
		// Clean up subscriptions
		if (unsubStatus) unsubStatus();
		if (unsubStory) unsubStory();
		if (unsubNewUpdate) unsubNewUpdate();

		// Disconnect WebSocket
		wsClient.disconnect();

		// Remove scroll listener
		if (typeof window !== 'undefined') {
			window.removeEventListener('scroll', handleScroll);
		}
	});

	async function loadInitialStories() {
		try {
			const currentStory = await api.getCurrentStory();
			const history = await api.getStoryHistory(10, 0);

			// Load data for current story
			const currentData = await loadStoryData(currentStory);
			stories = [currentData];

			// Load data for history
			for (const story of history) {
				if (story.id !== currentStory.id) {
					const fullStory = await api.getStoryById(story.id);
					const data = await loadStoryData(fullStory);
					stories = [...stories, data];
				}
			}

			offset = stories.length;
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load stories';
			loading = false;
		}
	}

	async function loadStoryData(story: StoryVersion): Promise<StoryData> {
		let image: GeneratedImage | null = null;
		let analytics: Analytics | null = null;

		try {
			// Load image for this story
			const imageResponse = await fetch(`/api/story/${story.id}/image`);
			if (imageResponse.ok) {
				image = await imageResponse.json();
			}
		} catch (e) {
			console.log(`No image for story ${story.id}`);
		}

		try {
			// Load analytics for this story (generates automatically if not found)
			const analyticsResponse = await fetch(`/api/story/${story.id}/analytics`);
			if (analyticsResponse.ok) {
				analytics = await analyticsResponse.json();
			}
			// Note: analytics may be null if generation failed, but that's okay
		} catch (e) {
			console.log(`No analytics for story ${story.id}`);
		}

		return { story, image, analytics };
	}

	async function loadMore() {
		if (loadingMore || !hasMore) return;

		loadingMore = true;
		try {
			const newStories = await api.getStoryHistory(10, offset);

			if (newStories.length === 0) {
				hasMore = false;
			} else {
				for (const story of newStories) {
					// Skip if already loaded
					if (stories.find(s => s.story.id === story.id)) continue;

					const fullStory = await api.getStoryById(story.id);
					const data = await loadStoryData(fullStory);
					stories = [...stories, data];
				}
				offset = stories.length;
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
		const threshold = document.documentElement.scrollHeight - 1000;

		if (scrollPosition >= threshold) {
			loadMore();
		}
	}

	async function dismissUpdate() {
		hasNewUpdate = false;
		wsClient.clearNewUpdate();

		if (wsStory) {
			// Add new story to top
			const data = await loadStoryData(wsStory);
			stories = [data, ...stories];
			offset++;
		}

		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

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
	<title>UnioNews - The Singular, Unified, Authoritative and Eternal Narrative</title>
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
			{#if hasNewUpdate}
				<div class="update-notification">
					<p>New update available</p>
					<button on:click={dismissUpdate}>View Now</button>
				</div>
			{/if}

			<!-- Connection status bar -->
			<div class="status-bar">
				<span class="connection-status" class:connected={wsStatus === 'connected'}>
					{wsStatus === 'connected' ? '● Live' : '○ Offline'}
				</span>
			</div>

			<!-- Continuous story feed (doomscroll mode) -->
			<div class="story-feed">
				{#each stories as storyData, i}
					<article class="story-block" class:latest={i === 0}>
						<!-- Story header -->
						<div class="story-header">
							<time datetime={storyData.story.created_at}>
								{formatDate(storyData.story.created_at)}
							</time>
							{#if i === 0}
								<span class="latest-badge">LATEST</span>
							{/if}
						</div>

						<!-- Story content -->
						<div class="story-content">
							{@html storyData.story.full_text.replace(/\n\n/g, '</p><p>').replace(/^(.*)$/, '<p>$1</p>')}
						</div>

						<!-- Image integration -->
						{#if storyData.image}
							<div class="story-image-section">
								<figure class="story-figure">
									<img src={storyData.image.image_url} alt="Visual interpretation" class="story-image" />
									<figcaption>
										AI-generated visualization of this moment in THE STORY
									</figcaption>
								</figure>
							</div>
						{/if}

						<!-- Analytics dashboards -->
						{#if storyData.analytics}
							<div class="analytics-section">
								<button
									class="analytics-toggle"
									on:click={() => toggleAnalytics(storyData.story.id)}
									aria-expanded={expandedAnalytics.has(storyData.story.id)}
								>
									<span class="toggle-icon">
										{expandedAnalytics.has(storyData.story.id) ? '▼' : '▶'}
									</span>
									<span class="toggle-text">
										{expandedAnalytics.has(storyData.story.id) ? 'Hide' : 'Show'} Analysis
									</span>
								</button>

								{#if expandedAnalytics.has(storyData.story.id)}
									<div class="analytics-content">
										<div class="analytics-grid">
											<!-- Sentiment -->
											{#if storyData.analytics.sentiment_score}
												<SentimentDashboard
													sentiment={{
														overall: storyData.analytics.overall_sentiment || 'neutral',
														score: storyData.analytics.sentiment_score
													}}
												/>
											{/if}

											<!-- Bias -->
											{#if storyData.analytics.bias_score}
												<BiasDashboard
													biasScore={storyData.analytics.bias_score}
													biasIndicators={storyData.analytics.bias_indicators}
												/>
											{/if}

											<!-- Event Timeline -->
											{#if storyData.analytics.events && storyData.analytics.events.length > 0}
												<EventTimeline events={storyData.analytics.events} />
											{/if}

											<!-- Fact Checking -->
											{#if storyData.analytics.fact_checks && storyData.analytics.fact_checks.length > 0}
												<FactCheckDashboard factChecks={storyData.analytics.fact_checks} />
											{/if}

											<!-- Forecasting -->
											{#if storyData.analytics.predictions && storyData.analytics.predictions.length > 0}
												<ForecastDashboard predictions={storyData.analytics.predictions} />
											{/if}

											<!-- Cross-Source Analysis -->
											{#if storyData.analytics.source_analysis && storyData.analytics.source_analysis.length > 0}
												<CrossSourceDashboard sourceAnalysis={storyData.analytics.source_analysis} />
											{/if}
										</div>
									</div>
								{/if}
							</div>
						{/if}

						<!-- Story separator -->
						<div class="story-separator"></div>
					</article>
				{/each}
			</div>

			<!-- Loading more indicator -->
			{#if hasMore}
				<div class="load-more">
					{#if loadingMore}
						<p class="loading-text">Loading deeper into THE STORY...</p>
					{:else}
						<p class="scroll-hint">Scroll for more...</p>
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
		min-height: 100vh;
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
		animation: slideDown 0.3s ease;
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translate(-50%, -100%);
		}
		to {
			opacity: 1;
			transform: translate(-50%, 0);
		}
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

	.status-bar {
		position: sticky;
		top: 0;
		z-index: 100;
		background: var(--color-bg);
		border-bottom: 1px solid var(--color-border);
		padding: var(--spacing-sm);
		margin-bottom: var(--spacing-lg);
		display: flex;
		justify-content: flex-end;
	}

	.connection-status {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-light);
	}

	.connection-status.connected {
		color: #22c55e;
	}

	.story-feed {
		display: flex;
		flex-direction: column;
	}

	.story-block {
		margin-bottom: var(--spacing-xl);
	}

	.story-block.latest {
		position: relative;
	}

	.story-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-md);
	}

	.latest-badge {
		background: var(--color-accent);
		color: white;
		padding: 4px 8px;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.story-content :global(p) {
		margin-bottom: var(--spacing-md);
		text-align: justify;
		line-height: 1.7;
	}

	.story-image-section {
		margin: var(--spacing-xl) 0;
	}

	.story-figure {
		margin: 0;
		background: var(--color-highlight);
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}

	.story-image {
		width: 100%;
		height: auto;
		display: block;
	}

	figcaption {
		padding: var(--spacing-md);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		font-style: italic;
		text-align: center;
	}

	.analytics-section {
		margin-top: var(--spacing-xl);
	}

	.analytics-toggle {
		width: 100%;
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		padding: var(--spacing-md);
		margin-bottom: var(--spacing-md);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-light);
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		transition: all 0.2s ease;
	}

	.analytics-toggle:hover {
		background: var(--color-border);
		color: var(--color-text);
	}

	.toggle-icon {
		font-size: 0.75rem;
		transition: transform 0.2s ease;
	}

	.toggle-text {
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.analytics-content {
		animation: slideIn 0.3s ease;
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.analytics-grid {
		display: grid;
		gap: var(--spacing-md);
	}

	.story-separator {
		margin-top: var(--spacing-xl);
		height: 4px;
		background: linear-gradient(90deg,
			transparent,
			var(--color-border) 20%,
			var(--color-border) 80%,
			transparent
		);
	}

	.load-more {
		text-align: center;
		padding: var(--spacing-lg) 0;
	}

	.loading-text,
	.scroll-hint {
		color: var(--color-text-light);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-style: italic;
	}

	.end-message {
		text-align: center;
		color: var(--color-text-light);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-style: italic;
		padding: var(--spacing-xl) 0;
		margin-top: var(--spacing-xl);
		border-top: 2px solid var(--color-border);
	}
</style>
