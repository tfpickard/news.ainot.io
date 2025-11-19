<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	interface Stats {
		total_stories: number;
		total_images: number;
		total_feed_items: number;
		latest_story_at: string | null;
		latest_image_at: string | null;
		update_frequency_minutes: number;
		feeds_count: number;
		model_name: string;
		uptime_hours: number;
		stories_last_24h: number;
		images_last_24h: number;
	}

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

	let stats: Stats | null = null;
	let latestImage: GeneratedImage | null = null;
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			// Fetch stats
			const statsResponse = await fetch('/api/stats');
			if (!statsResponse.ok) throw new Error('Failed to load stats');
			stats = await statsResponse.json();

			// Fetch latest image
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
			error = err instanceof Error ? err.message : 'Failed to load stats';
			loading = false;
		}
	});

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return 'N/A';
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

	function formatUptime(hours: number): string {
		const days = Math.floor(hours / 24);
		const remainingHours = Math.floor(hours % 24);
		if (days > 0) {
			return `${days}d ${remainingHours}h`;
		}
		return `${remainingHours}h`;
	}
</script>

<svelte:head>
	<title>Stats - Singl News</title>
</svelte:head>

<div class="page">
	<div class="container">
		<h1 class="page-title">Singl News Statistics</h1>

		{#if loading}
			<div class="loading">Loading statistics...</div>
		{:else if error}
			<div class="error">
				<p>{error}</p>
				<button on:click={() => window.location.reload()}>Retry</button>
			</div>
		{:else if stats}
			<div class="stats-grid">
				<!-- Generation Stats -->
				<div class="stat-card">
					<h2 class="stat-title">Story Generation</h2>
					<div class="stat-item">
						<span class="stat-label">Total Stories Generated</span>
						<span class="stat-value">{stats.total_stories.toLocaleString()}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Stories (Last 24h)</span>
						<span class="stat-value">{stats.stories_last_24h.toLocaleString()}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Latest Story</span>
						<span class="stat-value small">{formatDate(stats.latest_story_at)}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Update Frequency</span>
						<span class="stat-value">{stats.update_frequency_minutes} minutes</span>
					</div>
				</div>

				<!-- Image Generation Stats -->
				<div class="stat-card">
					<h2 class="stat-title">Image Generation</h2>
					<div class="stat-item">
						<span class="stat-label">Total Images Generated</span>
						<span class="stat-value">{stats.total_images.toLocaleString()}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Images (Last 24h)</span>
						<span class="stat-value">{stats.images_last_24h.toLocaleString()}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Latest Image</span>
						<span class="stat-value small">{formatDate(stats.latest_image_at)}</span>
					</div>
				</div>

				<!-- Feed Stats -->
				<div class="stat-card">
					<h2 class="stat-title">News Sources</h2>
					<div class="stat-item">
						<span class="stat-label">Active Feeds</span>
						<span class="stat-value">{stats.feeds_count.toLocaleString()}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Total Feed Items</span>
						<span class="stat-value">{stats.total_feed_items.toLocaleString()}</span>
					</div>
				</div>

				<!-- System Stats -->
				<div class="stat-card">
					<h2 class="stat-title">System</h2>
					<div class="stat-item">
						<span class="stat-label">AI Model</span>
						<span class="stat-value small">{stats.model_name}</span>
					</div>
					<div class="stat-item">
						<span class="stat-label">Uptime</span>
						<span class="stat-value">{formatUptime(stats.uptime_hours)}</span>
					</div>
				</div>
			</div>

			<!-- Latest Generated Image -->
			{#if latestImage}
				<div class="latest-image-section">
					<h2 class="section-title">Latest AI-Generated Image</h2>
					<div class="image-card">
						<img src={latestImage.image_url} alt="AI generated visualization" class="generated-image" />
						<div class="image-details">
							<p class="image-date">{formatDate(latestImage.created_at)}</p>
							<p class="image-prompt">
								<strong>Prompt:</strong> {latestImage.prompt}
							</p>
							{#if latestImage.revised_prompt}
								<p class="image-prompt revised">
									<strong>Revised Prompt:</strong> {latestImage.revised_prompt}
								</p>
							{/if}
							<p class="image-meta">
								Model: {latestImage.model} • Size: {latestImage.size} • Quality: {latestImage.quality}
							</p>
						</div>
					</div>
				</div>
			{/if}

			<div class="navigation">
				<a href="/" class="nav-link">← Back to Story</a>
			</div>
		{/if}
	</div>
</div>

<style>
	.page {
		min-height: 60vh;
	}

	.page-title {
		font-size: 2rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-xl);
		text-align: center;
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

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: var(--spacing-lg);
		margin-bottom: var(--spacing-xl);
	}

	.stat-card {
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-lg);
	}

	.stat-title {
		font-size: 1.1rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-md);
		color: var(--color-accent);
		border-bottom: 2px solid var(--color-accent);
		padding-bottom: var(--spacing-xs);
	}

	.stat-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--spacing-sm) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.stat-item:last-child {
		border-bottom: none;
	}

	.stat-label {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		color: var(--color-text-light);
	}

	.stat-value {
		font-family: var(--font-sans);
		font-size: 1.2rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.stat-value.small {
		font-size: 0.85rem;
		font-weight: 400;
	}

	.latest-image-section {
		margin-top: var(--spacing-xl);
		padding-top: var(--spacing-xl);
		border-top: 2px solid var(--color-border);
	}

	.section-title {
		font-size: 1.5rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-lg);
		text-align: center;
	}

	.image-card {
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		overflow: hidden;
	}

	.generated-image {
		width: 100%;
		height: auto;
		display: block;
	}

	.image-details {
		padding: var(--spacing-lg);
	}

	.image-date {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-sm);
	}

	.image-prompt {
		font-family: var(--font-sans);
		font-size: 0.95rem;
		margin-bottom: var(--spacing-sm);
		line-height: 1.5;
	}

	.image-prompt.revised {
		color: var(--color-text-light);
		font-style: italic;
	}

	.image-meta {
		font-family: var(--font-sans);
		font-size: 0.8rem;
		color: var(--color-text-light);
		margin-top: var(--spacing-md);
		padding-top: var(--spacing-sm);
		border-top: 1px solid var(--color-border);
	}

	.navigation {
		margin-top: var(--spacing-xl);
		text-align: center;
	}

	.nav-link {
		font-family: var(--font-sans);
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--color-accent);
		text-decoration: none;
		padding: var(--spacing-sm) var(--spacing-md);
		border: 1px solid var(--color-accent);
		border-radius: 4px;
		display: inline-block;
		transition: all 0.2s;
	}

	.nav-link:hover {
		background: var(--color-accent);
		color: white;
	}
</style>
