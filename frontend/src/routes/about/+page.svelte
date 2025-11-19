<script lang="ts">
	import { SITE_NAME } from '$lib/config';
</script>

<svelte:head>
	<title>About - {SITE_NAME}</title>
</svelte:head>

<div class="page">
	<div class="container content">
		<div class="page-header">
			<h1>About {SITE_NAME}</h1>
		</div>

		<section class="about-section">
			<h2>Our Mission</h2>
			<p>
				{SITE_NAME} operates as the world's Global Continuity Desk, maintaining a unified narrative
				of world events as they unfold. Unlike traditional news services that fragment reality into
				discrete stories, we recognize that all events are interconnected threads in a single,
				continuous tapestry.
			</p>
		</section>

		<section class="about-section">
			<h2>Methodology</h2>
			<p>
				Our editorial synthesis process draws from multiple global information sources, identifying
				the connective tissue between seemingly disparate events. Through continuous automated
				editorial processes, we weave these developments into an evolving narrative that captures
				the true interconnected nature of world affairs.
			</p>
			<p>
				The story you read today is not separate from yesterday's coverage—it is a continuation,
				an evolution, a deepening of understanding. THE STORY has no beginning and no end, only
				perpetual development.
			</p>
		</section>

		<section class="about-section">
			<h2>Philosophy</h2>
			<p>
				Traditional journalism presents the world as a series of isolated incidents: a political
				development here, a natural disaster there, an economic shift somewhere else. But reality
				resists such fragmentation. Every event ripples outward, influencing and being influenced
				by countless other threads.
			</p>
			<p>
				{SITE_NAME} exists to capture this totality. We do not reset the narrative with each news
				cycle. We do not start fresh each morning. Instead, we maintain continuity, tracking how
				today's developments alter, amplify, or recontextualize what came before.
			</p>
		</section>

		<section class="about-section">
			<h2>Coverage Sources</h2>
			<p>
				Our unified narrative synthesizes information from major international news feeds,
				including agencies such as CNN, BBC, The Guardian, The New York Times, Reuters, and
				Al Jazeera, among others. These sources provide the raw material from which our continuous
				narrative is constructed.
			</p>
		</section>

		<section class="about-section">
			<h2>Technical Infrastructure</h2>
			<p>
				{SITE_NAME} employs advanced automated editorial synthesis technology to process incoming
				information streams and integrate them into our ongoing narrative. Our systems operate
				continuously, ensuring that THE STORY evolves in near-real-time as global events develop.
			</p>
			<p>
				All coverage is compiled from multiple information sources using automated editorial
				processes designed to maintain narrative coherence across temporal and geographic
				boundaries.
			</p>
		</section>

		<section class="about-section">
			<h2>Access</h2>
			<p>
				The current version of THE STORY is always available on our homepage. Our complete
				archive preserves every iteration of the narrative, allowing you to trace how
				understanding has evolved over time. You may scroll indefinitely through our coverage—there
				is always more context, more history, more story.
			</p>
		</section>

		<section class="about-section">
			<h2>Contact</h2>
			<p>
				{SITE_NAME} maintains operations at both <strong>singl.news</strong> and <strong>news.ainot.io</strong>.
				Our Global Continuity Desk operates without interruption, ensuring THE STORY continues to
				evolve.
			</p>
		</section>

		<div class="about-footer">
			<p class="tagline">
				There is only one story.<br />
				Everything else is commentary.
			</p>
			<a href="/" class="action-link">Return to THE STORY →</a>
		</div>
	</div>
</div>

<style>
	.page {
		min-height: 60vh;
	}

	.content {
		max-width: 680px;
	}

	.page-header {
		text-align: center;
		margin-bottom: var(--spacing-xl);
		padding-bottom: var(--spacing-lg);
		border-bottom: 2px solid var(--color-text);
	}

	.page-header h1 {
		font-size: 2.5rem;
	}

	.about-section {
		margin-bottom: var(--spacing-xl);
	}

	.about-section h2 {
		font-size: 1.5rem;
		margin-bottom: var(--spacing-md);
		padding-bottom: var(--spacing-xs);
		border-bottom: 1px solid var(--color-border);
	}

	.about-section p {
		margin-bottom: var(--spacing-md);
		line-height: 1.8;
	}

	.about-footer {
		margin-top: var(--spacing-xl);
		padding: var(--spacing-xl) 0;
		border-top: 2px solid var(--color-text);
		text-align: center;
	}

	.tagline {
		font-family: var(--font-sans);
		font-size: 1.125rem;
		font-weight: 600;
		font-style: italic;
		color: var(--color-text-light);
		margin-bottom: var(--spacing-lg);
		line-height: 1.6;
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
