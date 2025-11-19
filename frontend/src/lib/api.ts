// API client for backend communication

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface StoryVersion {
	id: number;
	created_at: string;
	full_text: string;
	summary: string;
	sources_snapshot?: {
		feed_items?: any[];
		item_count: number;
	};
}

export interface StoryVersionSummary {
	id: number;
	created_at: string;
	summary: string;
	preview: string;
}

class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string) {
		this.baseUrl = baseUrl;
	}

	async getCurrentStory(): Promise<StoryVersion> {
		const response = await fetch(`${this.baseUrl}/api/story/current`);
		if (!response.ok) {
			throw new Error('Failed to fetch current story');
		}
		return response.json();
	}

	async getStoryHistory(limit: number = 10, offset: number = 0): Promise<StoryVersionSummary[]> {
		const response = await fetch(
			`${this.baseUrl}/api/story/history?limit=${limit}&offset=${offset}`
		);
		if (!response.ok) {
			throw new Error('Failed to fetch story history');
		}
		return response.json();
	}

	async getStoryById(id: number): Promise<StoryVersion> {
		const response = await fetch(`${this.baseUrl}/api/story/${id}`);
		if (!response.ok) {
			throw new Error('Failed to fetch story');
		}
		return response.json();
	}
}

export const api = new ApiClient(API_URL);
