// Authentication utilities for admin pages

const STORAGE_KEY = 'singl_admin_api_key';
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8001' : '');

export interface AuthState {
	apiKey: string | null;
	isAuthenticated: boolean;
}

export function getAuthState(): AuthState {
	const apiKey = localStorage.getItem(STORAGE_KEY);
	return {
		apiKey,
		isAuthenticated: !!apiKey
	};
}

export function setApiKey(apiKey: string): void {
	localStorage.setItem(STORAGE_KEY, apiKey);
}

export function clearAuth(): void {
	localStorage.removeItem(STORAGE_KEY);
}

export async function login(password: string): Promise<string> {
	const response = await fetch(`${API_BASE}/api/auth/login`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ password })
	});

	if (!response.ok) {
		if (response.status === 401) {
			throw new Error('Invalid password');
		}
		throw new Error('Login failed');
	}

	const data = await response.json();
	setApiKey(data.api_key);
	return data.api_key;
}

export async function verifyAuth(): Promise<boolean> {
	const { apiKey } = getAuthState();
	if (!apiKey) return false;

	try {
		const response = await fetch(`${API_BASE}/api/auth/verify`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${apiKey}`
			}
		});

		return response.ok;
	} catch {
		return false;
	}
}

export function getAuthHeaders(): HeadersInit {
	const { apiKey } = getAuthState();
	if (!apiKey) return {};

	return {
		Authorization: `Bearer ${apiKey}`
	};
}

// Helper for authenticated fetch
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
	const headers = {
		...options.headers,
		...getAuthHeaders()
	};

	const response = await fetch(url, {
		...options,
		headers
	});

	// If unauthorized, clear auth and redirect to login
	if (response.status === 401) {
		clearAuth();
		window.location.reload();
	}

	return response;
}
