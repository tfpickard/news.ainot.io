<script lang="ts">
	import '../app.css';
	import { SITE_NAME } from '$lib/config';
	import { page } from '$app/stores';
	import NewsroomAmbience from '$lib/components/NewsroomAmbience.svelte';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
</script>

<svelte:head>
	<title>{SITE_NAME}</title>
	<meta name="description" content="Global Continuity Desk delivering unified narrative coverage" />
</svelte:head>

<div class="site">
	<header class="masthead">
		<div class="container">
			<div class="header-top">
				<ThemeSwitcher />
			</div>
			<nav class="nav">
				<a href="/" class="nav-link" class:active={$page.url.pathname === '/'}>Live</a>
				<a href="/history" class="nav-link" class:active={$page.url.pathname === '/history'}>Archive</a>
				<a href="/stats" class="nav-link" class:active={$page.url.pathname === '/stats'}>Stats</a>
				<a href="/about" class="nav-link" class:active={$page.url.pathname === '/about'}>About</a>
				<a href="/api-docs" class="nav-link" class:active={$page.url.pathname === '/api-docs'}>API</a>
				<a href="/control" class="nav-link" class:active={$page.url.pathname === '/control'}>Control</a>
			</nav>
			<h1 class="site-title">
				<a href="/">{SITE_NAME}</a>
			</h1>
			<p class="site-tagline">Global Continuity Desk</p>
		</div>
	</header>

	<main class="main">
		<slot />
	</main>

	<footer class="footer">
		<div class="container text-center text-small text-light">
			<p>
				Coverage compiled from multiple information sources using automated editorial processes.
			</p>
			<p>
				© {new Date().getFullYear()} {SITE_NAME}. All events unified.
			</p>
		</div>
	</footer>

	<!-- Newsroom Ambience Player -->
	<NewsroomAmbience />
</div>

<style>
	.site {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.masthead {
		border-bottom: 3px solid var(--color-text);
		padding: var(--spacing-lg) 0;
		margin-bottom: var(--spacing-xl);
	}

	.header-top {
		display: flex;
		justify-content: flex-end;
		margin-bottom: var(--spacing-md);
	}

	.nav {
		display: flex;
		gap: var(--spacing-md);
		justify-content: center;
		margin-bottom: var(--spacing-md);
		font-family: var(--font-sans);
		font-size: 0.875rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.nav-link {
		color: var(--color-text-light);
		text-decoration: none;
		padding: var(--spacing-xs) var(--spacing-sm);
		border-bottom: 2px solid transparent;
		transition: all 0.2s;
	}

	.nav-link:hover {
		color: var(--color-text);
		text-decoration: none;
	}

	.nav-link.active {
		color: var(--color-text);
		border-bottom-color: var(--color-text);
	}

	.site-title {
		font-family: var(--font-serif);
		font-size: 4rem;
		font-weight: 900;
		text-align: center;
		margin: 0;
		letter-spacing: -0.03em;
		line-height: 1;
	}

	.site-title a {
		color: var(--color-text);
		text-decoration: none;
	}

	.site-tagline {
		text-align: center;
		font-family: var(--font-sans);
		font-size: 0.875rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--color-text-light);
		margin-top: var(--spacing-sm);
	}

	.main {
		flex: 1;
		padding-bottom: var(--spacing-xl);
	}

	.footer {
		border-top: 1px solid var(--color-border);
		padding: var(--spacing-lg) 0;
		margin-top: var(--spacing-xl);
	}

	@media (max-width: 768px) {
		.site-title {
			font-size: 3rem;
		}

		.masthead {
			padding: var(--spacing-md) 0;
			margin-bottom: var(--spacing-lg);
		}
	}
</style>
