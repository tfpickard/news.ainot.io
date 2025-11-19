<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	export let storyText: string = '';
	export let storyId: number | null = null;
	export let compact: boolean = false;

	let synth: SpeechSynthesis;
	let utterance: SpeechSynthesisUtterance | null = null;
	let voices: SpeechSynthesisVoice[] = [];
	let selectedVoice: SpeechSynthesisVoice | null = null;
	let isPlaying = false;
	let isPaused = false;
	let rate = 1.0;
	let pitch = 1.0;
	let showSettings = false;
	let currentPosition = 0;
	let totalLength = 0;
	let radioMode = false;

	onMount(() => {
		if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
			synth = window.speechSynthesis;
			loadVoices();

			// Load voices when they change
			if (synth.onvoiceschanged !== undefined) {
				synth.onvoiceschanged = loadVoices;
			}

			// Load saved preferences
			const savedVoice = localStorage.getItem('audioNarration_voice');
			const savedRate = localStorage.getItem('audioNarration_rate');
			const savedPitch = localStorage.getItem('audioNarration_pitch');

			if (savedRate) rate = parseFloat(savedRate);
			if (savedPitch) pitch = parseFloat(savedPitch);

			if (savedVoice && voices.length > 0) {
				selectedVoice = voices.find((v) => v.name === savedVoice) || voices[0];
			}
		}
	});

	onDestroy(() => {
		stop();
	});

	function loadVoices() {
		voices = synth?.getVoices() || [];
		if (voices.length > 0 && !selectedVoice) {
			// Prefer English voices
			selectedVoice =
				voices.find((v) => v.lang.startsWith('en') && v.name.includes('Natural')) ||
				voices.find((v) => v.lang.startsWith('en')) ||
				voices[0];
		}
	}

	function play() {
		if (!storyText || !synth) return;

		if (isPaused && utterance) {
			synth.resume();
			isPaused = false;
			isPlaying = true;
			return;
		}

		// Stop any current speech
		synth.cancel();

		utterance = new SpeechSynthesisUtterance(storyText);
		if (selectedVoice) {
			utterance.voice = selectedVoice;
		}
		utterance.rate = rate;
		utterance.pitch = pitch;

		totalLength = storyText.length;

		utterance.onstart = () => {
			isPlaying = true;
			isPaused = false;
		};

		utterance.onboundary = (event) => {
			currentPosition = event.charIndex;
		};

		utterance.onend = () => {
			isPlaying = false;
			isPaused = false;
			currentPosition = 0;

			if (radioMode) {
				// In radio mode, automatically fetch and play next story
				setTimeout(() => {
					fetchNextStory();
				}, 2000);
			}
		};

		utterance.onerror = (event) => {
			console.error('Speech error:', event);
			isPlaying = false;
			isPaused = false;
		};

		synth.speak(utterance);
	}

	function pause() {
		if (synth && isPlaying) {
			synth.pause();
			isPaused = true;
			isPlaying = false;
		}
	}

	function stop() {
		if (synth) {
			synth.cancel();
			isPlaying = false;
			isPaused = false;
			currentPosition = 0;
		}
	}

	function changeVoice(voice: SpeechSynthesisVoice) {
		selectedVoice = voice;
		localStorage.setItem('audioNarration_voice', voice.name);
		if (isPlaying || isPaused) {
			const wasPlaying = isPlaying;
			stop();
			if (wasPlaying) {
				setTimeout(play, 100);
			}
		}
	}

	function changeRate(newRate: number) {
		rate = newRate;
		localStorage.setItem('audioNarration_rate', rate.toString());
		if (isPlaying || isPaused) {
			const wasPlaying = isPlaying;
			stop();
			if (wasPlaying) {
				setTimeout(play, 100);
			}
		}
	}

	function changePitch(newPitch: number) {
		pitch = newPitch;
		localStorage.setItem('audioNarration_pitch', pitch.toString());
		if (isPlaying || isPaused) {
			const wasPlaying = isPlaying;
			stop();
			if (wasPlaying) {
				setTimeout(play, 100);
			}
		}
	}

	function toggleRadioMode() {
		radioMode = !radioMode;
		if (radioMode && !isPlaying && !isPaused) {
			play();
		}
	}

	async function fetchNextStory() {
		try {
			// Fetch the next story from the API
			const response = await fetch('/api/story/current');
			if (!response.ok) return;

			const data = await response.json();
			if (data.full_text && data.id !== storyId) {
				storyText = data.full_text;
				storyId = data.id;
				play();
			}
		} catch (err) {
			console.error('Failed to fetch next story:', err);
			radioMode = false;
		}
	}

	$: progress = totalLength > 0 ? (currentPosition / totalLength) * 100 : 0;
</script>

{#if synth}
	<div class="audio-narration" class:compact>
		<div class="controls">
			<div class="playback-controls">
				{#if !isPlaying && !isPaused}
					<button class="control-btn play" on:click={play} title="Play narration">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
							<path d="M8 5v14l11-7z" />
						</svg>
					</button>
				{:else if isPaused}
					<button class="control-btn play" on:click={play} title="Resume">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
							<path d="M8 5v14l11-7z" />
						</svg>
					</button>
				{:else}
					<button class="control-btn pause" on:click={pause} title="Pause">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
							<path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
						</svg>
					</button>
				{/if}

				<button class="control-btn stop" on:click={stop} title="Stop" disabled={!isPlaying && !isPaused}>
					<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
						<path d="M6 6h12v12H6z" />
					</svg>
				</button>

				<button
					class="control-btn radio"
					class:active={radioMode}
					on:click={toggleRadioMode}
					title="Radio mode - continuous playback"
				>
					📻
				</button>
			</div>

			{#if !compact}
				<button class="settings-btn" on:click={() => (showSettings = !showSettings)} title="Audio settings">
					⚙️
				</button>
			{/if}
		</div>

		{#if isPlaying || isPaused}
			<div class="progress-bar">
				<div class="progress-fill" style="width: {progress}%"></div>
			</div>
		{/if}

		{#if showSettings && !compact}
			<div class="settings-panel">
				<div class="setting">
					<label>Voice:</label>
					<select on:change={(e) => changeVoice(voices[parseInt(e.currentTarget.value)])}>
						{#each voices as voice, i}
							<option value={i} selected={voice === selectedVoice}>
								{voice.name} ({voice.lang})
							</option>
						{/each}
					</select>
				</div>

				<div class="setting">
					<label>Speed: {rate.toFixed(1)}x</label>
					<input
						type="range"
						min="0.5"
						max="2"
						step="0.1"
						bind:value={rate}
						on:change={() => changeRate(rate)}
					/>
				</div>

				<div class="setting">
					<label>Pitch: {pitch.toFixed(1)}</label>
					<input
						type="range"
						min="0.5"
						max="2"
						step="0.1"
						bind:value={pitch}
						on:change={() => changePitch(pitch)}
					/>
				</div>

				<div class="info">
					{#if radioMode}
						<p class="radio-mode-info">📻 Radio mode: Continuous playback enabled</p>
					{/if}
				</div>
			</div>
		{/if}
	</div>
{/if}

<style>
	.audio-narration {
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 8px;
		padding: 1rem;
		margin: 1rem 0;
	}

	.audio-narration.compact {
		padding: 0.5rem;
		margin: 0.5rem 0;
	}

	.controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.playback-controls {
		display: flex;
		gap: 0.5rem;
	}

	.control-btn {
		width: 44px;
		height: 44px;
		border: 1px solid var(--border-color);
		background: var(--bg-primary);
		color: var(--text-primary);
		border-radius: 50%;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
	}

	.control-btn:hover:not(:disabled) {
		background: var(--accent-color);
		color: white;
		border-color: var(--accent-color);
		transform: scale(1.05);
	}

	.control-btn:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.control-btn.play:hover {
		background: #10b981;
		border-color: #10b981;
	}

	.control-btn.pause:hover {
		background: #f59e0b;
		border-color: #f59e0b;
	}

	.control-btn.stop:hover {
		background: #ef4444;
		border-color: #ef4444;
	}

	.control-btn.radio.active {
		background: var(--accent-color);
		color: white;
		border-color: var(--accent-color);
	}

	.settings-btn {
		padding: 0.5rem 1rem;
		border: 1px solid var(--border-color);
		background: var(--bg-primary);
		color: var(--text-primary);
		border-radius: 6px;
		cursor: pointer;
		font-size: 1.2rem;
		transition: all 0.2s;
	}

	.settings-btn:hover {
		background: var(--bg-hover);
	}

	.progress-bar {
		margin-top: 1rem;
		height: 4px;
		background: var(--bg-primary);
		border-radius: 2px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--accent-color), #10b981);
		transition: width 0.3s ease;
	}

	.settings-panel {
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid var(--border-color);
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.setting {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.setting label {
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--text-secondary);
	}

	.setting select,
	.setting input[type='range'] {
		padding: 0.5rem;
		border: 1px solid var(--border-color);
		background: var(--bg-primary);
		color: var(--text-primary);
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.setting input[type='range'] {
		cursor: pointer;
	}

	.radio-mode-info {
		font-size: 0.85rem;
		color: var(--accent-color);
		margin: 0;
		padding: 0.5rem;
		background: var(--bg-primary);
		border-radius: 4px;
		text-align: center;
	}

	.info {
		margin-top: 0.5rem;
	}

	@media (max-width: 768px) {
		.control-btn {
			width: 40px;
			height: 40px;
		}

		.playback-controls {
			gap: 0.25rem;
		}
	}
</style>
