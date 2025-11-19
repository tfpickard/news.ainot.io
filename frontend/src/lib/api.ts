// API client for backend communication

// Use relative URL in production (empty string means same origin)
// In development, use localhost:8001 (or environment variable)
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8001' : '');

export interface StoryVersion {
	id: number;
	created_at: string;
	full_text: string;
	summary: string;
	sources_snapshot?: {
		feed_items?: unknown[];
		item_count: number;
	};
	context_summary?: string;
	token_stats?: { [key: string]: any };
}

export interface StoryVersionSummary {
	id: number;
	created_at: string;
	summary: string;
	preview: string;
}

export interface Quote {
	text: string;
	category: string;
	absurdity_score: number;
	keywords: string[];
}

export interface SourceDetail {
	id: number;
	title: string;
	source: string;
	published_at?: string;
	link?: string;
}

export interface SEOMetadata {
	title: string;
	description: string;
	keywords: string[];
	og_title: string;
	og_description: string;
	og_type: string;
	twitter_card: string;
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

	async getStoryQuotes(id: number, count: number = 5): Promise<Quote[]> {
		const response = await fetch(`${this.baseUrl}/api/story/${id}/quotes?count=${count}`);
		if (!response.ok) {
			throw new Error('Failed to fetch quotes');
		}
		const data = await response.json();
		return data.quotes;
	}

	async getStorySources(id: number): Promise<SourceDetail[]> {
		const response = await fetch(`${this.baseUrl}/api/story/${id}/sources`);
		if (!response.ok) {
			throw new Error('Failed to fetch sources');
		}
		const data = await response.json();
		return data.sources;
	}

	async getStorySEO(id: number): Promise<SEOMetadata> {
		const response = await fetch(`${this.baseUrl}/api/story/${id}/seo`);
		if (!response.ok) {
			throw new Error('Failed to fetch SEO metadata');
		}
		return response.json();
	}
}

export const api = new ApiClient(API_URL);
