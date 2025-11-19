<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let currentTheme: 'light' | 'dark' | 'auto' = 'auto';
	let effectiveTheme: 'light' | 'dark' = 'light';
	let loading = true;

	// Check if it's daytime based on timezone
	function isDaytime(): boolean {
		const now = new Date();
		const hour = now.getHours();
		// Consider 6 AM - 6 PM as daytime
		return hour >= 6 && hour < 18;
	}

	// Apply theme to document
	function applyTheme(theme: 'light' | 'dark' | 'auto') {
		if (!browser) return;

		let resolvedTheme: 'light' | 'dark';

		if (theme === 'auto') {
			// First try timezone-based detection
			resolvedTheme = isDaytime() ? 'light' : 'dark';

			// Fall back to system preference if available
			if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
				// If system prefers dark and it's not explicitly daytime, use dark
				if (!isDaytime()) {
					resolvedTheme = 'dark';
				}
			}
		} else {
			resolvedTheme = theme;
		}

		effectiveTheme = resolvedTheme;
		document.documentElement.setAttribute('data-theme', theme);

		// Store in localStorage for immediate application on next load
		localStorage.setItem('theme-preference', theme);
	}

	// Load theme from backend
	async function loadTheme() {
		try {
			const response = await fetch('/api/settings');
			if (response.ok) {
				const settings = await response.json();
				currentTheme = settings.theme || 'auto';
			} else {
				// Default to auto if API fails
				currentTheme = 'auto';
			}
		} catch (error) {
			console.error('Failed to load theme settings:', error);
			currentTheme = 'auto';
		}

		// Apply the theme
		applyTheme(currentTheme);
		loading = false;
	}

	// Save theme to backend
	async function saveTheme(theme: 'light' | 'dark' | 'auto') {
		try {
			const response = await fetch('/api/settings', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ theme }),
			});

			if (!response.ok) {
				console.error('Failed to save theme settings');
			}
		} catch (error) {
			console.error('Failed to save theme settings:', error);
		}
	}

	// Handle theme change
	function setTheme(theme: 'light' | 'dark' | 'auto') {
		currentTheme = theme;
		applyTheme(theme);
		saveTheme(theme);
	}

	onMount(() => {
		// Try to apply stored preference immediately to avoid flash
		const stored = localStorage.getItem('theme-preference');
		if (stored && (stored === 'light' || stored === 'dark' || stored === 'auto')) {
			applyTheme(stored as any);
		}

		// Then load from backend
		loadTheme();

		// Update theme every hour to adjust for day/night changes
		const interval = setInterval(() => {
			if (currentTheme === 'auto') {
				applyTheme('auto');
			}
		}, 3600000); // 1 hour

		return () => clearInterval(interval);
	});
</script>

<div class="theme-switcher">
	<button
		class="theme-button"
		class:active={currentTheme === 'light'}
		on:click={() => setTheme('light')}
		title="Light mode"
		disabled={loading}
	>
		☀️
	</button>
	<button
		class="theme-button"
		class:active={currentTheme === 'auto'}
		on:click={() => setTheme('auto')}
		title="Auto (based on time of day)"
		disabled={loading}
	>
		🌓
	</button>
	<button
		class="theme-button"
		class:active={currentTheme === 'dark'}
		on:click={() => setTheme('dark')}
		title="Dark mode"
		disabled={loading}
	>
		🌙
	</button>
</div>

<style>
	.theme-switcher {
		display: flex;
		gap: 0.25rem;
		background: var(--color-highlight);
		border: 2px solid var(--color-border);
		border-radius: 8px;
		padding: 0.25rem;
	}

	.theme-button {
		background: transparent;
		border: 2px solid transparent;
		border-radius: 6px;
		padding: 0.5rem 0.75rem;
		font-size: 1.25rem;
		cursor: pointer;
		transition: all 0.2s;
		line-height: 1;
	}

	.theme-button:hover:not(:disabled) {
		background: var(--color-background);
		border-color: var(--color-border);
	}

	.theme-button.active {
		background: var(--color-background);
		border-color: var(--color-text);
	}

	.theme-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
