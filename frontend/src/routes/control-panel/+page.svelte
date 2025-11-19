<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	interface Config {
		singl_model_name: string;
		singl_update_minutes: number;
		singl_context_steps: number;
		singl_temperature: number;
		singl_max_tokens: number;
		singl_image_generation_enabled: boolean;
		singl_image_generation_interval: number;
		singl_image_model: string;
		singl_image_size: string;
		singl_image_quality: string;
		feed_count: number;
	}

	let authenticated = false;
	let password = '';
	let authError = '';
	let authLoading = false;

	let config: Config | null = null;
	let configLoading = false;
	let configError = '';
	let saveSuccess = false;

	// Form values
	let formValues: Partial<Config> = {};

	// Check if already authenticated
	onMount(() => {
		if (browser) {
			const token = localStorage.getItem('control_panel_token');
			if (token) {
				loadConfig(token);
			}
		}
	});

	async function handleLogin(e: Event) {
		e.preventDefault();
		authLoading = true;
		authError = '';

		try {
			const response = await fetch('/api/control-panel/auth', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ password })
			});

			const data = await response.json();

			if (data.success && data.token) {
				if (browser) {
					localStorage.setItem('control_panel_token', data.token);
				}
				authenticated = true;
				await loadConfig(data.token);
			} else {
				authError = data.message || 'Authentication failed';
			}
		} catch (err) {
			authError = err instanceof Error ? err.message : 'Authentication failed';
		} finally {
			authLoading = false;
		}
	}

	async function loadConfig(token: string) {
		configLoading = true;
		configError = '';

		try {
			const response = await fetch('/api/control-panel/config', {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				if (response.status === 401) {
					// Token expired or invalid
					if (browser) {
						localStorage.removeItem('control_panel_token');
					}
					authenticated = false;
					throw new Error('Session expired. Please log in again.');
				}
				throw new Error('Failed to load configuration');
			}

			config = await response.json();
			formValues = { ...config };
			authenticated = true;
		} catch (err) {
			configError = err instanceof Error ? err.message : 'Failed to load configuration';
		} finally {
			configLoading = false;
		}
	}

	async function handleSaveConfig(e: Event) {
		e.preventDefault();
		if (!browser) return;

		const token = localStorage.getItem('control_panel_token');
		if (!token) {
			configError = 'Not authenticated';
			return;
		}

		configLoading = true;
		configError = '';
		saveSuccess = false;

		try {
			const response = await fetch('/api/control-panel/config', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify(formValues)
			});

			if (!response.ok) {
				if (response.status === 401) {
					localStorage.removeItem('control_panel_token');
					authenticated = false;
					throw new Error('Session expired. Please log in again.');
				}
				throw new Error('Failed to save configuration');
			}

			config = await response.json();
			formValues = { ...config };
			saveSuccess = true;

			// Clear success message after 3 seconds
			setTimeout(() => {
				saveSuccess = false;
			}, 3000);
		} catch (err) {
			configError = err instanceof Error ? err.message : 'Failed to save configuration';
		} finally {
			configLoading = false;
		}
	}

	function handleLogout() {
		if (browser) {
			localStorage.removeItem('control_panel_token');
		}
		authenticated = false;
		config = null;
		password = '';
	}
</script>

<svelte:head>
	<title>Control Panel - Singl News</title>
</svelte:head>

<div class="page">
	<div class="container">
		<h1 class="page-title">Control Panel</h1>

		{#if !authenticated}
			<!-- Login Form -->
			<div class="auth-container">
				<div class="auth-card">
					<h2>Authentication Required</h2>
					<p class="auth-description">Enter the admin password to access the control panel.</p>

					<form on:submit={handleLogin}>
						<div class="form-group">
							<label for="password">Password</label>
							<input
								id="password"
								type="password"
								bind:value={password}
								placeholder="Enter admin password"
								required
								disabled={authLoading}
							/>
						</div>

						{#if authError}
							<div class="error-message">{authError}</div>
						{/if}

						<button type="submit" class="btn btn-primary" disabled={authLoading}>
							{authLoading ? 'Authenticating...' : 'Login'}
						</button>
					</form>
				</div>
			</div>
		{:else if configLoading && !config}
			<div class="loading">Loading configuration...</div>
		{:else if config}
			<!-- Configuration Form -->
			<div class="config-container">
				<div class="header-actions">
					<button on:click={handleLogout} class="btn btn-secondary">Logout</button>
				</div>

				{#if saveSuccess}
					<div class="success-message">Configuration saved successfully!</div>
				{/if}

				{#if configError}
					<div class="error-message">{configError}</div>
				{/if}

				<form on:submit={handleSaveConfig}>
					<!-- Story Generation Settings -->
					<div class="config-section">
						<h2 class="section-title">Story Generation</h2>

						<div class="form-group">
							<label for="model">AI Model</label>
							<input
								id="model"
								type="text"
								bind:value={formValues.singl_model_name}
								placeholder="e.g., gpt-4-turbo-preview"
								required
							/>
							<p class="help-text">The OpenAI model to use for story generation</p>
						</div>

						<div class="form-row">
							<div class="form-group">
								<label for="update_minutes">Update Frequency (minutes)</label>
								<input
									id="update_minutes"
									type="number"
									bind:value={formValues.singl_update_minutes}
									min="1"
									required
								/>
								<p class="help-text">How often to generate new story updates</p>
							</div>

							<div class="form-group">
								<label for="context_steps">Context Steps</label>
								<input
									id="context_steps"
									type="number"
									bind:value={formValues.singl_context_steps}
									min="1"
									required
								/>
								<p class="help-text">Number of recent story versions to use for context</p>
							</div>
						</div>

						<div class="form-row">
							<div class="form-group">
								<label for="temperature">Temperature</label>
								<input
									id="temperature"
									type="number"
									bind:value={formValues.singl_temperature}
									min="0"
									max="2"
									step="0.1"
									required
								/>
								<p class="help-text">0.0 = deterministic, 2.0 = very creative (default: 0.8)</p>
							</div>

							<div class="form-group">
								<label for="max_tokens">Max Tokens</label>
								<input
									id="max_tokens"
									type="number"
									bind:value={formValues.singl_max_tokens}
									min="100"
									required
								/>
								<p class="help-text">Maximum tokens for story generation</p>
							</div>
						</div>
					</div>

					<!-- Image Generation Settings -->
					<div class="config-section">
						<h2 class="section-title">Image Generation</h2>

						<div class="form-group">
							<label class="checkbox-label">
								<input
									type="checkbox"
									bind:checked={formValues.singl_image_generation_enabled}
								/>
								<span>Enable AI Image Generation</span>
							</label>
							<p class="help-text">Generate images inspired by the news story</p>
						</div>

						<div class="form-group">
							<label for="image_interval">Generation Interval</label>
							<input
								id="image_interval"
								type="number"
								bind:value={formValues.singl_image_generation_interval}
								min="1"
								required
								disabled={!formValues.singl_image_generation_enabled}
							/>
							<p class="help-text">Generate an image every N story updates</p>
						</div>

						<div class="form-group">
							<label for="image_model">Image Model</label>
							<select
								id="image_model"
								bind:value={formValues.singl_image_model}
								disabled={!formValues.singl_image_generation_enabled}
							>
								<option value="dall-e-3">DALL-E 3</option>
								<option value="dall-e-2">DALL-E 2</option>
							</select>
						</div>

						<div class="form-row">
							<div class="form-group">
								<label for="image_size">Image Size</label>
								<select
									id="image_size"
									bind:value={formValues.singl_image_size}
									disabled={!formValues.singl_image_generation_enabled}
								>
									<option value="1024x1024">1024x1024 (Square)</option>
									<option value="1024x1792">1024x1792 (Portrait)</option>
									<option value="1792x1024">1792x1024 (Landscape)</option>
								</select>
							</div>

							<div class="form-group">
								<label for="image_quality">Image Quality</label>
								<select
									id="image_quality"
									bind:value={formValues.singl_image_quality}
									disabled={!formValues.singl_image_generation_enabled}
								>
									<option value="standard">Standard</option>
									<option value="hd">HD (Higher cost)</option>
								</select>
							</div>
						</div>
					</div>

					<!-- System Info -->
					<div class="config-section">
						<h2 class="section-title">System Information</h2>
						<div class="info-grid">
							<div class="info-item">
								<span class="info-label">Active Feeds:</span>
								<span class="info-value">{config.feed_count}</span>
							</div>
						</div>
					</div>

					<div class="form-actions">
						<button type="submit" class="btn btn-primary" disabled={configLoading}>
							{configLoading ? 'Saving...' : 'Save Configuration'}
						</button>
						<a href="/stats" class="btn btn-secondary">View Stats</a>
						<a href="/" class="btn btn-secondary">Back to Story</a>
					</div>
				</form>
			</div>
		{/if}
	</div>
</div>

<style>
	.page {
		min-height: 80vh;
		padding: var(--spacing-xl) 0;
	}

	.page-title {
		font-size: 2rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-xl);
		text-align: center;
	}

	.loading {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-light);
	}

	/* Authentication */
	.auth-container {
		display: flex;
		justify-content: center;
		padding: var(--spacing-xl) 0;
	}

	.auth-card {
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-xl);
		max-width: 400px;
		width: 100%;
	}

	.auth-card h2 {
		font-family: var(--font-sans);
		font-size: 1.5rem;
		margin-bottom: var(--spacing-md);
		text-align: center;
	}

	.auth-description {
		font-family: var(--font-sans);
		color: var(--color-text-light);
		text-align: center;
		margin-bottom: var(--spacing-lg);
	}

	/* Configuration */
	.config-container {
		max-width: 800px;
		margin: 0 auto;
	}

	.header-actions {
		display: flex;
		justify-content: flex-end;
		margin-bottom: var(--spacing-lg);
	}

	.config-section {
		background: var(--color-highlight);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		padding: var(--spacing-lg);
		margin-bottom: var(--spacing-lg);
	}

	.section-title {
		font-size: 1.3rem;
		font-family: var(--font-sans);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--spacing-lg);
		color: var(--color-accent);
		border-bottom: 2px solid var(--color-accent);
		padding-bottom: var(--spacing-xs);
	}

	/* Forms */
	.form-group {
		margin-bottom: var(--spacing-md);
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--spacing-md);
	}

	label {
		display: block;
		font-family: var(--font-sans);
		font-weight: 600;
		margin-bottom: var(--spacing-xs);
		color: var(--color-text);
	}

	input[type='text'],
	input[type='password'],
	input[type='number'],
	select {
		width: 100%;
		padding: var(--spacing-sm);
		font-family: var(--font-sans);
		font-size: 1rem;
		border: 1px solid var(--color-border);
		border-radius: 4px;
		background: var(--color-background);
		color: var(--color-text);
	}

	input:disabled,
	select:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		cursor: pointer;
	}

	.checkbox-label input[type='checkbox'] {
		width: auto;
	}

	.help-text {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		color: var(--color-text-light);
		margin-top: var(--spacing-xs);
	}

	/* Buttons */
	.btn {
		padding: var(--spacing-sm) var(--spacing-md);
		font-family: var(--font-sans);
		font-size: 1rem;
		font-weight: 600;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		transition: all 0.2s;
		text-decoration: none;
		display: inline-block;
	}

	.btn-primary {
		background: var(--color-accent);
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--color-text);
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: transparent;
		color: var(--color-text);
		border: 1px solid var(--color-border);
	}

	.btn-secondary:hover {
		background: var(--color-highlight);
	}

	.form-actions {
		display: flex;
		gap: var(--spacing-md);
		justify-content: center;
		margin-top: var(--spacing-xl);
	}

	/* Messages */
	.error-message {
		background: #fee;
		border: 1px solid #fcc;
		color: #c33;
		padding: var(--spacing-sm);
		border-radius: 4px;
		margin-bottom: var(--spacing-md);
		font-family: var(--font-sans);
		font-size: 0.9rem;
	}

	.success-message {
		background: #efe;
		border: 1px solid #cfc;
		color: #363;
		padding: var(--spacing-sm);
		border-radius: 4px;
		margin-bottom: var(--spacing-md);
		font-family: var(--font-sans);
		font-size: 0.9rem;
	}

	/* Info Grid */
	.info-grid {
		display: grid;
		gap: var(--spacing-sm);
	}

	.info-item {
		display: flex;
		justify-content: space-between;
		padding: var(--spacing-sm) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.info-item:last-child {
		border-bottom: none;
	}

	.info-label {
		font-family: var(--font-sans);
		color: var(--color-text-light);
	}

	.info-value {
		font-family: var(--font-sans);
		font-weight: 600;
	}

	@media (max-width: 640px) {
		.form-row {
			grid-template-columns: 1fr;
		}

		.form-actions {
			flex-direction: column;
		}
	}
</style>
