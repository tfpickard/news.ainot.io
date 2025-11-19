<script lang="ts">
	import { onMount } from 'svelte';
	import { api, type Quote } from '$lib/api';

	export let storyId: number;
	export let showCount: number = 3;

	let quotes: Quote[] = [];
	let loading = true;
	let selectedQuote: Quote | null = null;
	let showShareMenu = false;

	onMount(async () => {
		try {
			quotes = await api.getStoryQuotes(storyId, showCount);
			if (quotes.length > 0) {
				selectedQuote = quotes[0];
			}
			loading = false;
		} catch (err) {
			console.error('Failed to load quotes:', err);
			loading = false;
		}
	});

	function selectQuote(quote: Quote) {
		selectedQuote = quote;
		showShareMenu = false;
	}

	function getShareUrl(platform: string) {
		const url = `https://singl.news/story/${storyId}`;
		const text = selectedQuote ? `"${selectedQuote.text}"` : '';

		switch (platform) {
			case 'twitter':
				return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text + ' #SinglNews')}&url=${encodeURIComponent(url)}`;
			case 'facebook':
				return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(text)}`;
			case 'reddit':
				return `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`;
			case 'linkedin':
				return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
			default:
				return url;
		}
	}

	function shareQuote(platform: string) {
		window.open(getShareUrl(platform), '_blank', 'width=600,height=400');
	}

	function copyToClipboard() {
		if (selectedQuote) {
			const text = `"${selectedQuote.text}"\n\nFrom THE STORY at Singl News\nhttps://singl.news/story/${storyId}`;
			navigator.clipboard.writeText(text).then(() => {
				alert('Quote copied to clipboard!');
			});
		}
	}
</script>

{#if !loading && quotes.length > 0}
	<div class="quote-card-container">
		<h3 class="quote-header">Share This Absurdity</h3>

		{#if selectedQuote}
			<div class="quote-card">
				<div class="quote-content">
					<span class="quote-mark">"</span>
					<p class="quote-text">{selectedQuote.text}</p>
					<span class="quote-mark">"</span>
				</div>
				<div class="quote-meta">
					<span class="absurdity-badge">
						Absurdity: {selectedQuote.absurdity_score}/10
					</span>
					<span class="category-badge">{selectedQuote.category}</span>
				</div>
			</div>

			<div class="share-buttons">
				<button class="share-btn twitter" on:click={() => shareQuote('twitter')}>
					𝕏 Tweet
				</button>
				<button class="share-btn facebook" on:click={() => shareQuote('facebook')}>
					Facebook
				</button>
				<button class="share-btn reddit" on:click={() => shareQuote('reddit')}>
					Reddit
				</button>
				<button class="share-btn copy" on:click={copyToClipboard}>
					📋 Copy
				</button>
			</div>
		{/if}

		{#if quotes.length > 1}
			<div class="quote-selector">
				<p class="selector-label">Choose a different quote:</p>
				<div class="quote-list">
					{#each quotes as quote, i}
						<button
							class="quote-option"
							class:active={selectedQuote === quote}
							on:click={() => selectQuote(quote)}
						>
							{i + 1}. {quote.text.substring(0, 60)}...
						</button>
					{/each}
				</div>
			</div>
		{/if}
	</div>
{/if}

<style>
	.quote-card-container {
		margin: var(--spacing-xl) 0;
		padding: var(--spacing-lg);
		background: var(--color-highlight);
		border: 2px solid var(--color-text-light);
		border-radius: 8px;
	}

	.quote-header {
		font-family: var(--font-sans);
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-md);
		text-align: center;
	}

	.quote-card {
		background: white;
		padding: var(--spacing-lg);
		border-radius: 4px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: var(--spacing-md);
	}

	.quote-content {
		position: relative;
		padding: var(--spacing-md);
	}

	.quote-mark {
		font-size: 4rem;
		color: var(--color-text-light);
		opacity: 0.3;
		font-family: Georgia, serif;
		line-height: 1;
		position: absolute;
	}

	.quote-mark:first-child {
		top: -10px;
		left: -10px;
	}

	.quote-mark:last-child {
		bottom: -30px;
		right: 10px;
	}

	.quote-text {
		font-size: 1.125rem;
		line-height: 1.6;
		font-style: italic;
		margin: var(--spacing-sm) 0;
		position: relative;
		z-index: 1;
	}

	.quote-meta {
		display: flex;
		gap: var(--spacing-sm);
		margin-top: var(--spacing-md);
		justify-content: center;
	}

	.absurdity-badge,
	.category-badge {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		padding: 4px 12px;
		border-radius: 12px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.absurdity-badge {
		background: #ff4444;
		color: white;
		font-weight: bold;
	}

	.category-badge {
		background: var(--color-border);
		color: var(--color-text);
	}

	.share-buttons {
		display: flex;
		gap: var(--spacing-sm);
		justify-content: center;
		flex-wrap: wrap;
	}

	.share-btn {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		padding: var(--spacing-sm) var(--spacing-md);
		border: 2px solid var(--color-text);
		background: white;
		color: var(--color-text);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.share-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
	}

	.share-btn.twitter:hover {
		background: #1da1f2;
		color: white;
		border-color: #1da1f2;
	}

	.share-btn.facebook:hover {
		background: #4267b2;
		color: white;
		border-color: #4267b2;
	}

	.share-btn.reddit:hover {
		background: #ff4500;
		color: white;
		border-color: #ff4500;
	}

	.share-btn.copy:hover {
		background: #28a745;
		color: white;
		border-color: #28a745;
	}

	.quote-selector {
		margin-top: var(--spacing-lg);
		padding-top: var(--spacing-lg);
		border-top: 1px solid var(--color-border);
	}

	.selector-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		margin-bottom: var(--spacing-sm);
		text-align: center;
	}

	.quote-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.quote-option {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		padding: var(--spacing-sm);
		text-align: left;
		background: white;
		border: 1px solid var(--color-border);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.quote-option:hover {
		background: var(--color-highlight);
		border-color: var(--color-text);
	}

	.quote-option.active {
		background: var(--color-text);
		color: white;
		border-color: var(--color-text);
		font-weight: 600;
	}

	@media (max-width: 768px) {
		.quote-card-container {
			padding: var(--spacing-md);
		}

		.quote-text {
			font-size: 1rem;
		}

		.share-buttons {
			flex-direction: column;
		}

		.share-btn {
			width: 100%;
		}
	}
</style>
