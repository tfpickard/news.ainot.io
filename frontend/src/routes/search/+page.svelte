<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	interface SearchResult {
		id: number;
		created_at: string;
		summary: string;
		snippet: string;
		match_type: string;
	}

	interface FeedResult {
		id: number;
		title: string;
		feed_name: string;
		published_at: string | null;
		snippet: string;
	}

	interface SearchData {
		query: string;
		total_results: number;
		offset: number;
		limit: number;
		results: SearchResult[];
		feed_results: FeedResult[];
	}

	interface EntityInfo {
		name: string;
		count: number;
		category: string;
	}

	interface EntitiesData {
		total_stories_analyzed: number;
		entities: {
			people: EntityInfo[];
			places: EntityInfo[];
			organizations: EntityInfo[];
			concepts: EntityInfo[];
		};
	}

	let query = '';
	let searchResults: SearchData | null = null;
	let entities: EntitiesData | null = null;
	let loading = false;
	let error: string | null = null;
	let activeTab: 'stories' | 'entities' = 'stories';
	let includeFeedResults = false;

	onMount(() => {
		// Check for query parameter
		const urlQuery = $page.url.searchParams.get('q');
		if (urlQuery) {
			query = urlQuery;
			performSearch();
		}

		// Load entities for entity tracking
		loadEntities();
	});

	async function performSearch() {
		if (!query || query.length < 2) {
			error = 'Please enter at least 2 characters to search';
			return;
		}

		try {
			loading = true;
			error = null;

			const params = new URLSearchParams({
				q: query,
				limit: '20',
				offset: '0',
				include_feeds: includeFeedResults.toString()
			});

			const response = await fetch(`/api/search?${params}`);
			if (!response.ok) throw new Error('Search failed');

			searchResults = await response.json();

			// Update URL
			const url = new URL(window.location.href);
			url.searchParams.set('q', query);
			window.history.pushState({}, '', url);

			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Search failed';
			loading = false;
		}
	}

	async function loadEntities() {
		try {
			const response = await fetch('/api/search/entities?limit=100');
			if (!response.ok) return;

			entities = await response.json();
		} catch (err) {
			console.error('Failed to load entities:', err);
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			performSearch();
		}
	}

	function viewStory(storyId: number) {
		goto(`/story/${storyId}`);
	}

	function searchEntity(entityName: string) {
		query = entityName;
		activeTab = 'stories';
		performSearch();
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Search - UnioNews</title>
	<meta name="description" content="Search the eternal narrative" />
</svelte:head>

<div class="search-page">
	<div class="container">
		<header class="search-header">
			<div class="header-top">
				<h1>Search The Narrative</h1>
				<a href="/" class="back-link">← Back to Feed</a>
			</div>

			<p class="subtitle">Explore the eternal story through time, entities, and themes</p>

			<div class="search-box">
				<input
					type="text"
					bind:value={query}
					on:keydown={handleKeydown}
					placeholder="Search stories, entities, themes..."
					class="search-input"
					autofocus
				/>
				<button on:click={performSearch} class="search-btn" disabled={loading}>
					{loading ? 'Searching...' : '🔍 Search'}
				</button>
			</div>

			<div class="search-options">
				<label class="checkbox-label">
					<input type="checkbox" bind:checked={includeFeedResults} />
					Include source articles
				</label>
			</div>

			<div class="tabs">
				<button class="tab" class:active={activeTab === 'stories'} on:click={() => (activeTab = 'stories')}>
					Search Results
				</button>
				<button class="tab" class:active={activeTab === 'entities'} on:click={() => (activeTab = 'entities')}>
					Entity Tracking
				</button>
			</div>
		</header>

		{#if error}
			<div class="error-message">
				⚠️ {error}
			</div>
		{/if}

		{#if activeTab === 'stories'}
			{#if searchResults}
				<div class="search-results">
					<div class="results-header">
						<h2>{searchResults.total_results} results for "{searchResults.query}"</h2>
					</div>

					{#if searchResults.results.length > 0}
						<div class="results-list">
							{#each searchResults.results as result}
								<article class="result-item" on:click={() => viewStory(result.id)}>
									<div class="result-meta">
										<time>{formatDate(result.created_at)}</time>
										<span class="match-type">{result.match_type}</span>
									</div>
									<h3 class="result-summary">{result.summary}</h3>
									<p class="result-snippet">{@html result.snippet}</p>
								</article>
							{/each}
						</div>
					{:else}
						<div class="no-results">
							<p>No stories found matching "{searchResults.query}"</p>
						</div>
					{/if}

					{#if searchResults.feed_results.length > 0}
						<div class="feed-results">
							<h3>Source Articles</h3>
							<div class="feed-list">
								{#each searchResults.feed_results as feedResult}
									<article class="feed-item">
										<div class="feed-meta">
											<span class="feed-name">{feedResult.feed_name}</span>
											{#if feedResult.published_at}
												<time>{formatDate(feedResult.published_at)}</time>
											{/if}
										</div>
										<h4>{feedResult.title}</h4>
										<p class="feed-snippet">{feedResult.snippet}</p>
									</article>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{:else if !loading}
				<div class="empty-state">
					<p>Enter a search query to explore the narrative</p>
					<div class="search-tips">
						<h3>Search Tips:</h3>
						<ul>
							<li>Search for keywords, entities, or phrases</li>
							<li>Track recurring characters and themes</li>
							<li>Discover connections across story versions</li>
						</ul>
					</div>
				</div>
			{/if}

			{#if loading}
				<div class="loading">
					<div class="spinner"></div>
					<p>Searching the narrative...</p>
				</div>
			{/if}
		{:else if activeTab === 'entities'}
			{#if entities}
				<div class="entities-section">
					<div class="entities-header">
						<h2>Tracked Entities</h2>
						<p class="entity-count">
							Analyzed across {entities.total_stories_analyzed} recent stories
						</p>
					</div>

					<div class="entities-grid">
						{#if entities.entities.people.length > 0}
							<div class="entity-category">
								<h3>👤 People</h3>
								<div class="entity-list">
									{#each entities.entities.people.slice(0, 20) as entity}
										<button class="entity-tag" on:click={() => searchEntity(entity.name)}>
											{entity.name}
											<span class="count">{entity.count}</span>
										</button>
									{/each}
								</div>
							</div>
						{/if}

						{#if entities.entities.organizations.length > 0}
							<div class="entity-category">
								<h3>🏢 Organizations</h3>
								<div class="entity-list">
									{#each entities.entities.organizations.slice(0, 20) as entity}
										<button class="entity-tag" on:click={() => searchEntity(entity.name)}>
											{entity.name}
											<span class="count">{entity.count}</span>
										</button>
									{/each}
								</div>
							</div>
						{/if}

						{#if entities.entities.places.length > 0}
							<div class="entity-category">
								<h3>📍 Places</h3>
								<div class="entity-list">
									{#each entities.entities.places.slice(0, 20) as entity}
										<button class="entity-tag" on:click={() => searchEntity(entity.name)}>
											{entity.name}
											<span class="count">{entity.count}</span>
										</button>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>

<style>
	.search-page {
		min-height: 100vh;
		background: var(--bg-primary);
		color: var(--text-primary);
		padding: 2rem 1rem;
	}

	.container {
		max-width: 1000px;
		margin: 0 auto;
	}

	.search-header {
		margin-bottom: 3rem;
	}

	.header-top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	h1 {
		font-size: 2.5rem;
		margin: 0;
		font-weight: 800;
		letter-spacing: -0.02em;
	}

	.back-link {
		color: var(--text-secondary);
		text-decoration: none;
		font-size: 1rem;
		transition: color 0.2s;
	}

	.back-link:hover {
		color: var(--text-primary);
	}

	.subtitle {
		color: var(--text-secondary);
		font-size: 1.1rem;
		margin: 0 0 2rem 0;
	}

	.search-box {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.search-input {
		flex: 1;
		padding: 1rem 1.5rem;
		border: 2px solid var(--border-color);
		background: var(--bg-secondary);
		color: var(--text-primary);
		border-radius: 12px;
		font-size: 1.1rem;
		transition: all 0.2s;
	}

	.search-input:focus {
		outline: none;
		border-color: var(--accent-color);
		box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb), 0.1);
	}

	.search-btn {
		padding: 1rem 2rem;
		background: var(--accent-color);
		color: white;
		border: none;
		border-radius: 12px;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}

	.search-btn:hover:not(:disabled) {
		background: var(--accent-hover);
		transform: translateY(-2px);
	}

	.search-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.search-options {
		margin-bottom: 1.5rem;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.95rem;
		color: var(--text-secondary);
		cursor: pointer;
	}

	.checkbox-label input {
		cursor: pointer;
	}

	.tabs {
		display: flex;
		gap: 0.5rem;
		border-bottom: 2px solid var(--border-color);
		margin-bottom: 2rem;
	}

	.tab {
		padding: 0.75rem 1.5rem;
		background: none;
		border: none;
		color: var(--text-secondary);
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		border-bottom: 3px solid transparent;
		margin-bottom: -2px;
		transition: all 0.2s;
	}

	.tab:hover {
		color: var(--text-primary);
	}

	.tab.active {
		color: var(--accent-color);
		border-bottom-color: var(--accent-color);
	}

	.error-message {
		background: #fee;
		color: #c33;
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 2rem;
	}

	.results-header {
		margin-bottom: 1.5rem;
	}

	.results-header h2 {
		font-size: 1.5rem;
		margin: 0;
	}

	.results-list {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.result-item {
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 12px;
		padding: 1.5rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.result-item:hover {
		border-color: var(--accent-color);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.result-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.match-type {
		text-transform: uppercase;
		font-weight: 600;
		padding: 0.25rem 0.5rem;
		background: var(--bg-primary);
		border-radius: 4px;
	}

	.result-summary {
		margin: 0 0 0.75rem 0;
		font-size: 1.1rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.result-snippet {
		margin: 0;
		color: var(--text-secondary);
		line-height: 1.6;
	}

	.loading,
	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid var(--border-color);
		border-top-color: var(--accent-color);
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.search-tips {
		margin-top: 2rem;
		text-align: left;
		max-width: 500px;
		margin-left: auto;
		margin-right: auto;
	}

	.search-tips h3 {
		margin-bottom: 1rem;
	}

	.search-tips ul {
		list-style: none;
		padding: 0;
	}

	.search-tips li {
		padding: 0.5rem 0;
		padding-left: 1.5rem;
		position: relative;
	}

	.search-tips li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--accent-color);
	}

	.entities-section {
		padding: 2rem 0;
	}

	.entities-header {
		margin-bottom: 2rem;
	}

	.entities-header h2 {
		font-size: 1.8rem;
		margin: 0 0 0.5rem 0;
	}

	.entity-count {
		color: var(--text-secondary);
		margin: 0;
	}

	.entities-grid {
		display: grid;
		gap: 2rem;
	}

	.entity-category h3 {
		font-size: 1.3rem;
		margin: 0 0 1rem 0;
	}

	.entity-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.entity-tag {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 20px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.95rem;
		color: var(--text-primary);
	}

	.entity-tag:hover {
		background: var(--accent-color);
		color: white;
		border-color: var(--accent-color);
	}

	.entity-tag .count {
		background: var(--bg-primary);
		padding: 0.15rem 0.5rem;
		border-radius: 10px;
		font-size: 0.8rem;
		font-weight: 600;
	}

	.entity-tag:hover .count {
		background: rgba(255, 255, 255, 0.2);
		color: white;
	}

	.feed-results {
		margin-top: 3rem;
		padding-top: 2rem;
		border-top: 2px solid var(--border-color);
	}

	.feed-results h3 {
		margin: 0 0 1.5rem 0;
		font-size: 1.3rem;
	}

	.feed-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.feed-item {
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 8px;
		padding: 1rem;
	}

	.feed-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.feed-name {
		font-weight: 600;
	}

	.feed-item h4 {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
	}

	.feed-snippet {
		margin: 0;
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	@media (max-width: 768px) {
		.search-page {
			padding: 1rem 0.5rem;
		}

		h1 {
			font-size: 1.8rem;
		}

		.header-top {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.search-box {
			flex-direction: column;
		}

		.search-btn {
			width: 100%;
		}

		.result-item {
			padding: 1rem;
		}
	}
</style>
