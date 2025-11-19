// WebSocket client for real-time story updates

import { writable } from 'svelte/store';
import type { StoryVersion } from './api';

// Dynamically determine WebSocket URL based on environment
// In production: use same host with wss/ws based on protocol
// In development: use localhost:8001 (or environment variable)
const getWebSocketUrl = () => {
	if (import.meta.env.VITE_WS_URL) {
		return import.meta.env.VITE_WS_URL;
	}

	if (import.meta.env.DEV) {
		return 'ws://localhost:8001/ws/story';
	}

	// Production: use current host with appropriate protocol
	const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	const host = window.location.host;
	return `${protocol}//${host}/ws/story`;
};

const WS_URL = getWebSocketUrl();

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

class WebSocketClient {
	private ws: WebSocket | null = null;
	private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
	private reconnectDelay = 1000;
	private maxReconnectDelay = 30000;

	public status = writable<ConnectionStatus>('disconnected');
	public latestStory = writable<StoryVersion | null>(null);
	public hasNewUpdate = writable(false);

	connect() {
		if (this.ws?.readyState === WebSocket.OPEN) {
			return;
		}

		this.status.set('connecting');

		try {
			this.ws = new WebSocket(WS_URL);

			this.ws.onopen = () => {
				console.log('WebSocket connected');
				this.status.set('connected');
				this.reconnectDelay = 1000; // Reset reconnect delay on successful connection
			};

			this.ws.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					if ((data.type === 'initial' || data.type === 'update') && data.story) {
						this.latestStory.set(data.story);
						this.hasNewUpdate.set(true);
					}
				} catch (error) {
					console.error('Error parsing WebSocket message:', error);
				}
			};

			this.ws.onerror = (error) => {
				console.error('WebSocket error:', error);
				this.status.set('error');
			};

			this.ws.onclose = () => {
				console.log('WebSocket disconnected');
				this.status.set('disconnected');
				this.scheduleReconnect();
			};
		} catch (error) {
			console.error('Error creating WebSocket:', error);
			this.status.set('error');
			this.scheduleReconnect();
		}
	}

	disconnect() {
		if (this.reconnectTimeout) {
			clearTimeout(this.reconnectTimeout);
			this.reconnectTimeout = null;
		}

		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}

		this.status.set('disconnected');
	}

	clearNewUpdate() {
		this.hasNewUpdate.set(false);
	}

	private scheduleReconnect() {
		if (this.reconnectTimeout) {
			return;
		}

		this.reconnectTimeout = setTimeout(() => {
			console.log(`Attempting to reconnect in ${this.reconnectDelay}ms...`);
			this.reconnectTimeout = null;
			this.connect();

			// Exponential backoff
			this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
		}, this.reconnectDelay);
	}
}

export const wsClient = new WebSocketClient();
