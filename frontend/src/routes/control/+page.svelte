<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	interface FeedConfig {
		id: number;
		name: string;
		url: string;
		category: string | null;
		is_active: boolean;
		priority: number;
		created_at: string;
		last_fetched: string | null;
		fetch_error: string | null;
	}

	let feeds: FeedConfig[] = [];
	let loading = true;
	let error: string | null = null;
	let showAddForm = false;
	let editingFeed: FeedConfig | null = null;

	// Form fields
	let formName = '';
	let formUrl = '';
	let formCategory = '';
	let formPriority = 0;
	let formActive = true;

	// Filter
	let showInactiveFeeds = false;

	onMount(async () => {
		await loadFeeds();
	});

	async function loadFeeds() {
		try {
			loading = true;
			const response = await fetch('/api/feeds');
			if (!response.ok) throw new Error('Failed to load feeds');
			feeds = await response.json();
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load feeds';
			loading = false;
		}
	}

	function openAddForm() {
		editingFeed = null;
		formName = '';
		formUrl = '';
		formCategory = '';
		formPriority = 0;
		formActive = true;
		showAddForm = true;
	}

	function openEditForm(feed: FeedConfig) {
		editingFeed = feed;
		formName = feed.name;
		formUrl = feed.url;
		formCategory = feed.category || '';
		formPriority = feed.priority;
		formActive = feed.is_active;
		showAddForm = true;
	}

	function cancelForm() {
		showAddForm = false;
		editingFeed = null;
	}

	async function saveFeed() {
		try {
			const payload = {
				name: formName,
				url: formUrl,
				category: formCategory || null,
				is_active: formActive,
				priority: formPriority
			};

			if (editingFeed) {
				// Update existing feed
				const response = await fetch(`/api/feeds/${editingFeed.id}`, {
					method: 'PUT',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(payload)
				});
				if (!response.ok) throw new Error('Failed to update feed');
			} else {
				// Create new feed
				const response = await fetch('/api/feeds', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(payload)
				});
				if (!response.ok) throw new Error('Failed to create feed');
			}

			showAddForm = false;
			await loadFeeds();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to save feed');
		}
	}

	async function deleteFeed(id: number) {
		if (!confirm('Are you sure you want to delete this feed?')) return;

		try {
			const response = await fetch(`/api/feeds/${id}`, {
				method: 'DELETE'
			});
			if (!response.ok) throw new Error('Failed to delete feed');
			await loadFeeds();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to delete feed');
		}
	}

	async function toggleActive(feed: FeedConfig) {
		try {
			const response = await fetch(`/api/feeds/${feed.id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ is_active: !feed.is_active })
			});
			if (!response.ok) throw new Error('Failed to toggle feed');
			await loadFeeds();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to toggle feed');
		}
	}

	async function importDefaults() {
		if (!confirm('Import default feeds from configuration? (Existing feeds will be skipped)'))
			return;

		try {
			const response = await fetch('/api/feeds/import-defaults', {
				method: 'POST'
			});
			if (!response.ok) throw new Error('Failed to import defaults');
			const result = await response.json();
			alert(`Imported ${result.imported} feeds, skipped ${result.skipped} existing`);
			await loadFeeds();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to import defaults');
		}
	}

	$: filteredFeeds = showInactiveFeeds ? feeds : feeds.filter((f) => f.is_active);
</script>

<svelte:head>
	<title>Feed Control - Singl News</title>
</svelte:head>

<div class="control-page">
	<div class="container">
		<header class="control-header">
			<h1>RSS Feed Configuration</h1>
			<p class="control-description">Manage news sources for THE STORY</p>
		</header>

		{#if loading}
			<div class="loading">Loading feeds...</div>
		{:else if error}
			<div class="error">{error}</div>
		{:else}
			<div class="controls">
				<button class="btn btn-primary" on:click={openAddForm}>+ Add New Feed</button>
				<button class="btn btn-secondary" on:click={importDefaults}>
					Import Default Feeds
				</button>
				<label class="checkbox-label">
					<input type="checkbox" bind:checked={showInactiveFeeds} />
					Show inactive feeds
				</label>
			</div>

			<div class="stats">
				<span class="stat">Total: {feeds.length}</span>
				<span class="stat">Active: {feeds.filter((f) => f.is_active).length}</span>
				<span class="stat">Inactive: {feeds.filter((f) => !f.is_active).length}</span>
			</div>

			{#if showAddForm}
				<div class="form-modal">
					<div class="form-overlay" on:click={cancelForm}></div>
					<div class="form-card">
						<h2>{editingFeed ? 'Edit Feed' : 'Add New Feed'}</h2>
						<form on:submit|preventDefault={saveFeed}>
							<div class="form-group">
								<label for="name">Name *</label>
								<input
									id="name"
									type="text"
									bind:value={formName}
									required
									placeholder="e.g., TechCrunch"
								/>
							</div>

							<div class="form-group">
								<label for="url">RSS Feed URL *</label>
								<input
									id="url"
									type="url"
									bind:value={formUrl}
									required
									placeholder="https://example.com/feed.xml"
								/>
							</div>

							<div class="form-group">
								<label for="category">Category</label>
								<input
									id="category"
									type="text"
									bind:value={formCategory}
									placeholder="e.g., tech, politics, sports"
								/>
							</div>

							<div class="form-group">
								<label for="priority">Priority (higher = checked first)</label>
								<input id="priority" type="number" bind:value={formPriority} />
							</div>

							<div class="form-group">
								<label class="checkbox-label">
									<input type="checkbox" bind:checked={formActive} />
									Active
								</label>
							</div>

							<div class="form-actions">
								<button type="submit" class="btn btn-primary">Save</button>
								<button type="button" class="btn btn-secondary" on:click={cancelForm}>
									Cancel
								</button>
							</div>
						</form>
					</div>
				</div>
			{/if}

			<div class="feed-list">
				{#each filteredFeeds as feed (feed.id)}
					<div class="feed-card" class:inactive={!feed.is_active}>
						<div class="feed-header">
							<div class="feed-info">
								<h3 class="feed-name">{feed.name}</h3>
								{#if feed.category}
									<span class="feed-category">{feed.category}</span>
								{/if}
								{#if feed.priority > 0}
									<span class="feed-priority">Priority: {feed.priority}</span>
								{/if}
							</div>
							<div class="feed-actions">
								<button class="btn-icon" on:click={() => toggleActive(feed)} title="Toggle active">
									{feed.is_active ? '✓' : '✗'}
								</button>
								<button class="btn-icon" on:click={() => openEditForm(feed)} title="Edit">
									✎
								</button>
								<button class="btn-icon" on:click={() => deleteFeed(feed.id)} title="Delete">
									🗑
								</button>
							</div>
						</div>

						<div class="feed-url">{feed.url}</div>

						{#if feed.fetch_error}
							<div class="feed-error">
								<strong>Last Error:</strong>
								{feed.fetch_error}
							</div>
						{/if}

						{#if feed.last_fetched}
							<div class="feed-meta">
								Last fetched: {new Date(feed.last_fetched).toLocaleString()}
							</div>
						{/if}
					</div>
				{/each}

				{#if filteredFeeds.length === 0}
					<div class="empty-state">
						<p>No feeds configured yet.</p>
						<button class="btn btn-primary" on:click={openAddForm}>Add Your First Feed</button>
					</div>
				{/if}
			</div>
		{/if}

		<div class="control-footer">
			<a href="/" class="back-link">← Back to THE STORY</a>
		</div>
	</div>
</div>

<style>
	.control-page {
		min-height: 100vh;
		background: var(--color-highlight);
		padding: var(--spacing-xl) 0;
	}

	.control-header {
		text-align: center;
		margin-bottom: var(--spacing-xl);
	}

	.control-header h1 {
		font-size: 2.5rem;
		margin-bottom: var(--spacing-sm);
	}

	.control-description {
		font-family: var(--font-sans);
		color: var(--color-text-light);
	}

	.controls {
		display: flex;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-lg);
		flex-wrap: wrap;
		align-items: center;
	}

	.stats {
		display: flex;
		gap: var(--spacing-lg);
		margin-bottom: var(--spacing-lg);
		padding: var(--spacing-md);
		background: white;
		border-radius: 8px;
		border: 2px solid var(--color-border);
	}

	.stat {
		font-family: var(--font-sans);
		font-weight: 600;
	}

	.btn {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		padding: var(--spacing-sm) var(--spacing-md);
		border: 2px solid var(--color-text);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-primary {
		background: var(--color-text);
		color: white;
	}

	.btn-primary:hover {
		background: var(--color-text-light);
	}

	.btn-secondary {
		background: white;
		color: var(--color-text);
	}

	.btn-secondary:hover {
		background: var(--color-highlight);
	}

	.checkbox-label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
		cursor: pointer;
	}

	.form-modal {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-lg);
	}

	.form-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
	}

	.form-card {
		position: relative;
		background: white;
		border-radius: 8px;
		padding: var(--spacing-lg);
		max-width: 500px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
	}

	.form-card h2 {
		margin-bottom: var(--spacing-lg);
	}

	.form-group {
		margin-bottom: var(--spacing-md);
	}

	.form-group label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		display: block;
		margin-bottom: var(--spacing-xs);
	}

	.form-group input[type='text'],
	.form-group input[type='url'],
	.form-group input[type='number'] {
		width: 100%;
		padding: var(--spacing-sm);
		border: 2px solid var(--color-border);
		border-radius: 4px;
		font-family: var(--font-sans);
		font-size: 0.875rem;
	}

	.form-group input:focus {
		outline: none;
		border-color: var(--color-text);
	}

	.form-actions {
		display: flex;
		gap: var(--spacing-sm);
		margin-top: var(--spacing-lg);
	}

	.feed-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.feed-card {
		background: white;
		border: 2px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-md);
		transition: all 0.2s;
	}

	.feed-card.inactive {
		opacity: 0.6;
		border-style: dashed;
	}

	.feed-card:hover {
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.feed-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: var(--spacing-sm);
	}

	.feed-info {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		flex-wrap: wrap;
	}

	.feed-name {
		font-family: var(--font-sans);
		font-size: 1.125rem;
		margin: 0;
	}

	.feed-category,
	.feed-priority {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		padding: 2px 8px;
		background: var(--color-highlight);
		border-radius: 12px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.feed-actions {
		display: flex;
		gap: var(--spacing-xs);
	}

	.btn-icon {
		font-size: 1.125rem;
		padding: 4px 8px;
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-icon:hover {
		background: var(--color-border);
	}

	.feed-url {
		font-family: monospace;
		font-size: 0.875rem;
		color: var(--color-text-light);
		word-break: break-all;
		margin-bottom: var(--spacing-xs);
	}

	.feed-error {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: #dc3545;
		background: #f8d7da;
		padding: var(--spacing-sm);
		border-radius: 4px;
		margin-top: var(--spacing-sm);
	}

	.feed-meta {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
		margin-top: var(--spacing-xs);
	}

	.empty-state {
		text-align: center;
		padding: var(--spacing-xl);
		background: white;
		border: 2px dashed var(--color-border);
		border-radius: 8px;
	}

	.control-footer {
		text-align: center;
		margin-top: var(--spacing-xl);
	}

	.back-link {
		font-family: var(--font-sans);
		font-weight: 600;
	}

	.loading,
	.error {
		text-align: center;
		padding: var(--spacing-xl);
		font-family: var(--font-sans);
	}

	.error {
		color: #dc3545;
	}

	@media (max-width: 768px) {
		.feed-header {
			flex-direction: column;
			gap: var(--spacing-sm);
		}

		.controls {
			flex-direction: column;
			align-items: stretch;
		}

		.stats {
			flex-direction: column;
			gap: var(--spacing-sm);
		}
	}
</style>
