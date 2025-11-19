<script lang="ts">
	import { onMount } from 'svelte';

	export let pageName: string = 'Admin';

	const STORAGE_KEY = 'singl_admin_auth';
	const SESSION_DURATION = 24 * 60 * 60 * 1000; // 24 hours

	let isAuthenticated = false;
	let password = '';
	let error = '';
	let loading = true;

	onMount(() => {
		checkAuth();
	});

	function checkAuth() {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			try {
				const auth = JSON.parse(stored);
				const now = Date.now();
				if (auth.expires > now) {
					isAuthenticated = true;
					loading = false;
					return;
				}
			} catch (e) {
				// Invalid stored auth, clear it
				localStorage.removeItem(STORAGE_KEY);
			}
		}
		loading = false;
	}

	async function handleSubmit() {
		error = '';

		// Simple password check - in production, this would be server-side
		// For now, we'll use an environment variable or default password
		const correctPassword = import.meta.env.VITE_ADMIN_PASSWORD || 'singl2025';

		if (password === correctPassword) {
			const auth = {
				authenticated: true,
				expires: Date.now() + SESSION_DURATION
			};
			localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
			isAuthenticated = true;
		} else {
			error = 'Incorrect password';
			password = '';
		}
	}

	function handleLogout() {
		localStorage.removeItem(STORAGE_KEY);
		isAuthenticated = false;
		password = '';
	}
</script>

{#if loading}
	<div class="loading-screen">
		<p>Loading...</p>
	</div>
{:else if !isAuthenticated}
	<div class="auth-screen">
		<div class="auth-container">
			<div class="auth-header">
				<h1>{pageName}</h1>
				<p>Password required</p>
			</div>

			<form on:submit|preventDefault={handleSubmit} class="auth-form">
				<div class="form-group">
					<label for="password">Password</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						placeholder="Enter password"
						autocomplete="current-password"
						autofocus
					/>
				</div>

				{#if error}
					<div class="error-message">{error}</div>
				{/if}

				<button type="submit" class="submit-btn">Unlock</button>
			</form>

			<div class="auth-footer">
				<a href="/" class="back-link">← Back to THE STORY</a>
			</div>
		</div>
	</div>
{:else}
	<div class="protected-content">
		<div class="logout-bar">
			<button class="logout-btn" on:click={handleLogout}>Logout</button>
		</div>
		<slot />
	</div>
{/if}

<style>
	.loading-screen {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-sans);
		color: var(--color-text-light);
	}

	.auth-screen {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-highlight);
		padding: var(--spacing-lg);
	}

	.auth-container {
		background: white;
		border: 3px solid var(--color-text);
		border-radius: 8px;
		padding: var(--spacing-xl);
		max-width: 400px;
		width: 100%;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
	}

	.auth-header {
		text-align: center;
		margin-bottom: var(--spacing-xl);
	}

	.auth-header h1 {
		font-size: 2rem;
		margin-bottom: var(--spacing-xs);
	}

	.auth-header p {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: var(--color-text-light);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.auth-form {
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

	.form-group input {
		width: 100%;
		padding: var(--spacing-sm);
		border: 2px solid var(--color-border);
		border-radius: 4px;
		font-family: var(--font-sans);
		font-size: 1rem;
	}

	.form-group input:focus {
		outline: none;
		border-color: var(--color-text);
	}

	.error-message {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		color: #dc3545;
		background: #f8d7da;
		padding: var(--spacing-sm);
		border-radius: 4px;
		margin-bottom: var(--spacing-md);
		text-align: center;
	}

	.submit-btn {
		width: 100%;
		font-family: var(--font-sans);
		font-size: 1rem;
		font-weight: 600;
		padding: var(--spacing-sm);
		background: var(--color-text);
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.submit-btn:hover {
		background: var(--color-text-light);
	}

	.auth-footer {
		text-align: center;
		padding-top: var(--spacing-md);
		border-top: 1px solid var(--color-border);
	}

	.back-link {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-light);
		text-decoration: none;
	}

	.back-link:hover {
		color: var(--color-text);
	}

	.protected-content {
		position: relative;
	}

	.logout-bar {
		position: fixed;
		top: var(--spacing-sm);
		right: var(--spacing-sm);
		z-index: 1000;
	}

	.logout-btn {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		font-weight: 600;
		padding: 6px 12px;
		background: var(--color-text);
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	.logout-btn:hover {
		background: var(--color-text-light);
	}

	@media (max-width: 768px) {
		.auth-container {
			padding: var(--spacing-lg);
		}

		.logout-bar {
			top: var(--spacing-xs);
			right: var(--spacing-xs);
		}
	}
</style>
