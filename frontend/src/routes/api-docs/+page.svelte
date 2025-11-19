<script lang="ts">
	const API_BASE = 'https://singl.news';

	const endpoints = [
		{
			method: 'GET',
			path: '/api/story/current',
			description: 'Get the latest story version',
			example: `${API_BASE}/api/story/current`,
			response: {
				id: 123,
				created_at: '2025-11-19T12:00:00Z',
				summary: 'Brief summary of the story',
				full_text: 'Complete story text...',
				sources_snapshot: { item_count: 15 }
			}
		},
		{
			method: 'GET',
			path: '/api/story/history',
			description: 'Get paginated story history',
			params: ['limit (max 100)', 'offset'],
			example: `${API_BASE}/api/story/history?limit=20&offset=0`,
			response: [
				{ id: 123, created_at: '2025-11-19T12:00:00Z', summary: '...', preview: '...' }
			]
		},
		{
			method: 'GET',
			path: '/api/story/{id}',
			description: 'Get a specific story version by ID',
			example: `${API_BASE}/api/story/123`,
			response: { id: 123, full_text: '...' }
		},
		{
			method: 'GET',
			path: '/api/story/{id}/quotes',
			description: 'Get shareable quotes from a story',
			params: ['count (max 10)'],
			example: `${API_BASE}/api/story/123/quotes?count=5`,
			response: {
				story_id: 123,
				quotes: [
					{
						text: 'The submarine Olympics concluded...',
						category: 'sports',
						absurdity_score: 9,
						keywords: ['submarine', 'Olympics', 'Antarctica']
					}
				]
			}
		},
		{
			method: 'GET',
			path: '/api/story/{id}/sources',
			description: 'Get detailed source information for a story',
			example: `${API_BASE}/api/story/123/sources`,
			response: {
				story_id: 123,
				item_count: 15,
				sources: [
					{
						id: 456,
						title: 'Tech Company Announces...',
						source: 'TechCrunch',
						published_at: '2025-11-19T10:00:00Z',
						link: 'https://example.com/article'
					}
				]
			}
		},
		{
			method: 'GET',
			path: '/api/story/{id}/seo',
			description: 'Get SEO metadata for a story',
			example: `${API_BASE}/api/story/123/seo`,
			response: {
				title: 'Story title - UnioNews',
				description: 'Story description...',
				keywords: ['keyword1', 'keyword2'],
				og_title: 'Story title',
				og_description: 'Description for social media...'
			}
		}
	];

	function copyCode(text: string) {
		navigator.clipboard.writeText(text);
		alert('Copied to clipboard!');
	}
</script>

<svelte:head>
	<title>API Documentation - UnioNews</title>
	<meta
		name="description"
		content="Developer API for UnioNews - Access THE STORY programmatically"
	/>
</svelte:head>

<div class="page">
	<div class="container">
		<header class="api-header">
			<h1>API Documentation</h1>
			<p class="api-intro">
				Build weird and wonderful things with THE STORY. Our API provides programmatic access to
				the world's only unified continuous news narrative.
			</p>
		</header>

		<section class="getting-started">
			<h2>Getting Started</h2>
			<p>
				The UnioNews API is free to use. All endpoints return JSON and require no
				authentication.
			</p>

			<div class="info-box">
				<h3>Base URL</h3>
				<code class="code-block">https://singl.news</code>
			</div>

			<div class="info-box">
				<h3>Rate Limits</h3>
				<ul>
					<li>100 requests per minute (standard)</li>
					<li>200 requests per minute (burst)</li>
				</ul>
			</div>

			<div class="info-box">
				<h3>Attribution</h3>
				<p>Please include "Powered by UnioNews" when using this API in your projects.</p>
			</div>
		</section>

		<section class="endpoints">
			<h2>Endpoints</h2>

			{#each endpoints as endpoint}
				<div class="endpoint">
					<div class="endpoint-header">
						<span class="method">{endpoint.method}</span>
						<code class="path">{endpoint.path}</code>
					</div>

					<p class="description">{endpoint.description}</p>

					{#if endpoint.params}
						<div class="params">
							<h4>Parameters:</h4>
							<ul>
								{#each endpoint.params as param}
									<li><code>{param}</code></li>
								{/each}
							</ul>
						</div>
					{/if}

					<div class="example">
						<h4>Example Request:</h4>
						<div class="code-block-container">
							<pre class="code-block">{endpoint.example}</pre>
							<button class="copy-btn" on:click={() => copyCode(endpoint.example)}>
								Copy
							</button>
						</div>
					</div>

					<div class="example">
						<h4>Example Response:</h4>
						<pre class="code-block">{JSON.stringify(endpoint.response, null, 2)}</pre>
					</div>
				</div>
			{/each}
		</section>

		<section class="use-cases">
			<h2>Use Cases & Ideas</h2>
			<div class="use-case-grid">
				<div class="use-case-card">
					<h3>🤖 Bots & Automation</h3>
					<p>Create Twitter bots that share absurd quotes, Discord integrations, or Slack bots.</p>
				</div>

				<div class="use-case-card">
					<h3>📊 Data Visualization</h3>
					<p>Visualize how contradictions evolve over time or track narrative patterns.</p>
				</div>

				<div class="use-case-card">
					<h3>🎨 Creative Projects</h3>
					<p>Generate art from THE STORY, create music based on absurdity scores, make games.</p>
				</div>

				<div class="use-case-card">
					<h3>🔬 Research</h3>
					<p>Study AI-generated narratives, analyze how news sources are conflated.</p>
				</div>

				<div class="use-case-card">
					<h3>📱 Mobile Apps</h3>
					<p>Build iOS/Android apps for reading THE STORY on the go.</p>
				</div>

				<div class="use-case-card">
					<h3>🎭 Performance Art</h3>
					<p>Use real-time story updates in live performances or installations.</p>
				</div>
			</div>
		</section>

		<section class="examples">
			<h2>Code Examples</h2>

			<div class="code-example">
				<h3>JavaScript / TypeScript</h3>
				<pre class="code-block">{`// Fetch the current story
const response = await fetch('https://singl.news/api/story/current');
const story = await response.json();
console.log(story.full_text);

// Get absurd quotes
const quotes = await fetch('https://singl.news/api/story/123/quotes?count=5');
const data = await quotes.json();
data.quotes.forEach(q => console.log(q.text));`}</pre>
			</div>

			<div class="code-example">
				<h3>Python</h3>
				<pre class="code-block">{`import requests

# Fetch the current story
response = requests.get('https://singl.news/api/story/current')
story = response.json()
print(story['full_text'])

# Get story sources
sources = requests.get(f"https://singl.news/api/story/{story['id']}/sources")
for source in sources.json()['sources']:
    print(f"{source['source']}: {source['title']}")`}</pre>
			</div>

			<div class="code-example">
				<h3>cURL</h3>
				<pre class="code-block">{`# Get current story
curl https://singl.news/api/story/current

# Get quotes with jq for formatting
curl https://singl.news/api/story/123/quotes | jq '.quotes[].text'`}</pre>
			</div>
		</section>

		<section class="support">
			<h2>Support & Community</h2>
			<p>
				Have questions or built something cool? Share it with us!
			</p>
			<div class="support-links">
				<a href="/" class="support-link">← Back to THE STORY</a>
				<a href="/about" class="support-link">About UnioNews</a>
			</div>
		</section>
	</div>
</div>

<style>
	.page {
		padding: var(--spacing-xl) 0;
	}

	.api-header {
		text-align: center;
		margin-bottom: var(--spacing-xl);
		padding-bottom: var(--spacing-xl);
		border-bottom: 3px solid var(--color-text);
	}

	.api-header h1 {
		font-size: 3rem;
		margin-bottom: var(--spacing-md);
	}

	.api-intro {
		font-size: 1.125rem;
		color: var(--color-text-light);
		max-width: 600px;
		margin: 0 auto;
	}

	section {
		margin-bottom: var(--spacing-xl);
	}

	h2 {
		font-size: 2rem;
		margin-bottom: var(--spacing-lg);
		padding-bottom: var(--spacing-sm);
		border-bottom: 2px solid var(--color-border);
	}

	.info-box {
		background: var(--color-highlight);
		padding: var(--spacing-md);
		margin-bottom: var(--spacing-md);
		border-left: 4px solid var(--color-text);
		border-radius: 4px;
	}

	.info-box h3 {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-sm);
	}

	.info-box ul {
		margin: 0;
		padding-left: var(--spacing-lg);
	}

	.endpoint {
		background: white;
		border: 2px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-lg);
		margin-bottom: var(--spacing-lg);
	}

	.endpoint-header {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-md);
	}

	.method {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 700;
		padding: 4px 12px;
		background: #28a745;
		color: white;
		border-radius: 4px;
		text-transform: uppercase;
	}

	.path {
		font-family: monospace;
		font-size: 1rem;
		background: var(--color-highlight);
		padding: 4px 8px;
		border-radius: 4px;
	}

	.description {
		margin-bottom: var(--spacing-md);
		color: var(--color-text-light);
	}

	.params {
		margin-bottom: var(--spacing-md);
	}

	.params h4 {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		margin-bottom: var(--spacing-xs);
	}

	.params ul {
		margin: 0;
		padding-left: var(--spacing-lg);
	}

	.example {
		margin-bottom: var(--spacing-md);
	}

	.example h4 {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		margin-bottom: var(--spacing-xs);
	}

	.code-block-container {
		position: relative;
	}

	.code-block {
		font-family: monospace;
		font-size: 0.875rem;
		background: #1e1e1e;
		color: #d4d4d4;
		padding: var(--spacing-md);
		border-radius: 4px;
		overflow-x: auto;
		margin: 0;
	}

	.copy-btn {
		position: absolute;
		top: var(--spacing-sm);
		right: var(--spacing-sm);
		font-family: var(--font-sans);
		font-size: 0.75rem;
		padding: 4px 12px;
		background: var(--color-text);
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		opacity: 0.7;
		transition: opacity 0.2s;
	}

	.copy-btn:hover {
		opacity: 1;
	}

	.use-case-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: var(--spacing-md);
	}

	.use-case-card {
		background: var(--color-highlight);
		padding: var(--spacing-md);
		border-radius: 8px;
		border: 1px solid var(--color-border);
	}

	.use-case-card h3 {
		font-family: var(--font-sans);
		font-size: 1rem;
		margin-bottom: var(--spacing-sm);
	}

	.use-case-card p {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		margin: 0;
	}

	.code-example {
		margin-bottom: var(--spacing-lg);
	}

	.code-example h3 {
		font-family: var(--font-sans);
		font-size: 1rem;
		margin-bottom: var(--spacing-sm);
	}

	.support {
		text-align: center;
	}

	.support-links {
		display: flex;
		gap: var(--spacing-md);
		justify-content: center;
		margin-top: var(--spacing-md);
	}

	.support-link {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		padding: var(--spacing-sm) var(--spacing-md);
		background: var(--color-text);
		color: white;
		text-decoration: none;
		border-radius: 4px;
		transition: all 0.2s;
	}

	.support-link:hover {
		background: var(--color-text-light);
		text-decoration: none;
	}

	@media (max-width: 768px) {
		.api-header h1 {
			font-size: 2rem;
		}

		.endpoint {
			padding: var(--spacing-md);
		}

		.endpoint-header {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
