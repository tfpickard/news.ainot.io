<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { api, type StoryVersion, type SEOMetadata } from '$lib/api';
	import QuoteCard from '$lib/components/QuoteCard.svelte';
	import SourceTracker from '$lib/components/SourceTracker.svelte';

	let story: StoryVersion | null = null;
	let seoData: SEOMetadata | null = null;
	let loading = true;
	let error: string | null = null;

	$: storyId = parseInt($page.params.id);

	onMount(async () => {
		try {
			const [storyData, seo] = await Promise.all([
				api.getStoryById(storyId),
				api.getStorySEO(storyId).catch(() => null)
			]);
			story = storyData;
			seoData = seo;
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

	$: pageUrl = `https://singl.news/story/${storyId}`;
</script>

<svelte:head>
	<title>{seoData?.title || story?.summary || 'Story'} - UnioNews</title>

	{#if seoData}
		<!-- SEO Meta Tags -->
		<meta name="description" content={seoData.description} />
		<meta name="keywords" content={seoData.keywords.join(', ')} />

		<!-- Open Graph / Facebook -->
		<meta property="og:type" content={seoData.og_type} />
		<meta property="og:url" content={pageUrl} />
		<meta property="og:title" content={seoData.og_title} />
		<meta property="og:description" content={seoData.og_description} />
		<meta property="og:site_name" content="UnioNews" />

		<!-- Twitter -->
		<meta name="twitter:card" content={seoData.twitter_card} />
		<meta name="twitter:url" content={pageUrl} />
		<meta name="twitter:title" content={seoData.og_title} />
		<meta name="twitter:description" content={seoData.og_description} />

		<!-- Schema.org JSON-LD -->
		<script type="application/ld+json">
			{JSON.stringify({
				'@context': 'https://schema.org',
				'@type': 'NewsArticle',
				headline: seoData.og_title,
				description: seoData.description,
				datePublished: story?.created_at,
				author: {
					'@type': 'Organization',
					name: 'Global Continuity Desk',
					url: 'https://singl.news'
				},
				publisher: {
					'@type': 'Organization',
					name: 'UnioNews',
					url: 'https://singl.news'
				},
				url: pageUrl,
				keywords: seoData.keywords.join(', ')
			})}
		</script>
	{/if}
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

				<!-- Quote Cards for Sharing -->
				<QuoteCard storyId={story.id} showCount={3} />

				<!-- Enhanced Source Tracker -->
				<SourceTracker storyId={story.id} />
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
