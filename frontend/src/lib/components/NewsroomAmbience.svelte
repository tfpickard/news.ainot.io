<script lang="ts">
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	// Persistent state - stored in localStorage
	const STORAGE_KEY = 'singl_news_ambience';
	let isPlaying = writable(false);
	let volume = writable(0.3);
	let audio: HTMLAudioElement | null = null;
	let showControls = false;

	onMount(() => {
		// Load saved preferences
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved) {
			try {
				const prefs = JSON.parse(saved);
				isPlaying.set(prefs.isPlaying || false);
				volume.set(prefs.volume || 0.3);
			} catch (e) {
				console.error('Failed to load ambience preferences:', e);
			}
		}

		// Create audio element
		// Using a placeholder URL - you'll need to host actual newsroom ambience audio
		// For now, using a silent data URL as placeholder
		audio = new Audio();
		audio.loop = true;
		audio.volume = $volume;

		// Try to load from multiple potential sources
		const audioSources = [
			'/audio/newsroom-ambience.mp3',
			'https://cdn.singl.news/audio/newsroom-ambience.mp3',
			// Fallback to a free newsroom ambience sound (you can replace this)
			'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA='
		];

		let sourceIndex = 0;
		const tryLoadAudio = () => {
			if (sourceIndex < audioSources.length) {
				audio!.src = audioSources[sourceIndex];
				audio!.load();
				audio!.addEventListener('error', () => {
					sourceIndex++;
					tryLoadAudio();
				}, { once: true });
			}
		};

		tryLoadAudio();

		// Start playing if it was playing before
		if ($isPlaying) {
			audio.play().catch(err => {
				console.warn('Autoplay prevented:', err);
				isPlaying.set(false);
			});
		}

		// Cleanup
		return () => {
			if (audio) {
				audio.pause();
				audio = null;
			}
		};
	});

	function togglePlay() {
		if (!audio) return;

		if ($isPlaying) {
			audio.pause();
			isPlaying.set(false);
		} else {
			audio.play().catch(err => {
				console.error('Failed to play:', err);
			});
			isPlaying.set(true);
		}

		savePreferences();
	}

	function updateVolume(newVolume: number) {
		volume.set(newVolume);
		if (audio) {
			audio.volume = newVolume;
		}
		savePreferences();
	}

	function savePreferences() {
		localStorage.setItem(
			STORAGE_KEY,
			JSON.stringify({
				isPlaying: $isPlaying,
				volume: $volume
			})
		);
	}
</script>

<div class="newsroom-ambience">
	<button
		class="ambience-toggle"
		class:playing={$isPlaying}
		on:click={() => (showControls = !showControls)}
		title={$isPlaying ? 'Newsroom ambience playing' : 'Play newsroom ambience'}
	>
		{#if $isPlaying}
			🔊 Newsroom
		{:else}
			🔇 Ambience
		{/if}
	</button>

	{#if showControls}
		<div class="ambience-controls">
			<button class="play-btn" on:click={togglePlay}>
				{$isPlaying ? '⏸ Pause' : '▶ Play'}
			</button>

			<div class="volume-control">
				<label for="volume-slider">Volume:</label>
				<input
					id="volume-slider"
					type="range"
					min="0"
					max="1"
					step="0.1"
					value={$volume}
					on:input={(e) => updateVolume(parseFloat(e.currentTarget.value))}
				/>
				<span class="volume-value">{Math.round($volume * 100)}%</span>
			</div>

			<p class="ambience-description">
				Immersive newsroom atmosphere with keyboard clicks, phone calls, and distant conversations.
			</p>
		</div>
	{/if}
</div>

<style>
	.newsroom-ambience {
		position: fixed;
		bottom: var(--spacing-lg);
		right: var(--spacing-lg);
		z-index: 1000;
	}

	.ambience-toggle {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		padding: var(--spacing-sm) var(--spacing-md);
		background: var(--color-text);
		color: white;
		border: none;
		border-radius: 24px;
		cursor: pointer;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		transition: all 0.3s;
	}

	.ambience-toggle:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
	}

	.ambience-toggle.playing {
		background: #28a745;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
		}
		50% {
			box-shadow: 0 4px 20px rgba(40, 167, 69, 0.6);
		}
	}

	.ambience-controls {
		position: absolute;
		bottom: 60px;
		right: 0;
		background: white;
		border: 2px solid var(--color-text);
		border-radius: 8px;
		padding: var(--spacing-md);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		width: 280px;
	}

	.play-btn {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
		width: 100%;
		padding: var(--spacing-sm);
		background: var(--color-text);
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		margin-bottom: var(--spacing-sm);
		transition: background 0.2s;
	}

	.play-btn:hover {
		background: var(--color-text-light);
	}

	.volume-control {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-sm);
	}

	.volume-control label {
		font-family: var(--font-sans);
		font-size: 0.875rem;
		font-weight: 600;
	}

	#volume-slider {
		flex: 1;
		height: 4px;
		border-radius: 2px;
		background: var(--color-border);
		outline: none;
		-webkit-appearance: none;
	}

	#volume-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: var(--color-text);
		cursor: pointer;
	}

	#volume-slider::-moz-range-thumb {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: var(--color-text);
		cursor: pointer;
		border: none;
	}

	.volume-value {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
		min-width: 40px;
		text-align: right;
	}

	.ambience-description {
		font-family: var(--font-sans);
		font-size: 0.75rem;
		color: var(--color-text-light);
		line-height: 1.4;
		margin: 0;
		padding-top: var(--spacing-sm);
		border-top: 1px solid var(--color-border);
	}

	@media (max-width: 768px) {
		.newsroom-ambience {
			bottom: var(--spacing-md);
			right: var(--spacing-md);
		}

		.ambience-controls {
			width: calc(100vw - 2 * var(--spacing-md));
			right: auto;
			left: 50%;
			transform: translateX(-50%);
		}

		.ambience-toggle {
			font-size: 0.75rem;
			padding: var(--spacing-xs) var(--spacing-sm);
		}
	}
</style>
