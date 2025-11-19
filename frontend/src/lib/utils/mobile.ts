/**
 * Mobile utility functions for gestures and haptic feedback
 */

export interface SwipeOptions {
	onSwipeLeft?: () => void;
	onSwipeRight?: () => void;
	onSwipeUp?: () => void;
	onSwipeDown?: () => void;
	threshold?: number; // Minimum distance for swipe
}

/**
 * Svelte action for handling swipe gestures
 */
export function swipe(node: HTMLElement, options: SwipeOptions) {
	let touchStartX = 0;
	let touchStartY = 0;
	let touchEndX = 0;
	let touchEndY = 0;

	const threshold = options.threshold || 50; // pixels

	function handleTouchStart(event: TouchEvent) {
		touchStartX = event.changedTouches[0].screenX;
		touchStartY = event.changedTouches[0].screenY;
	}

	function handleTouchEnd(event: TouchEvent) {
		touchEndX = event.changedTouches[0].screenX;
		touchEndY = event.changedTouches[0].screenY;
		handleSwipe();
	}

	function handleSwipe() {
		const deltaX = touchEndX - touchStartX;
		const deltaY = touchEndY - touchStartY;

		// Determine if horizontal or vertical swipe
		if (Math.abs(deltaX) > Math.abs(deltaY)) {
			// Horizontal swipe
			if (Math.abs(deltaX) > threshold) {
				if (deltaX > 0) {
					options.onSwipeRight?.();
					haptic('light');
				} else {
					options.onSwipeLeft?.();
					haptic('light');
				}
			}
		} else {
			// Vertical swipe
			if (Math.abs(deltaY) > threshold) {
				if (deltaY > 0) {
					options.onSwipeDown?.();
				} else {
					options.onSwipeUp?.();
				}
			}
		}
	}

	node.addEventListener('touchstart', handleTouchStart);
	node.addEventListener('touchend', handleTouchEnd);

	return {
		destroy() {
			node.removeEventListener('touchstart', handleTouchStart);
			node.removeEventListener('touchend', handleTouchEnd);
		}
	};
}

/**
 * Trigger haptic feedback (if supported)
 */
export function haptic(type: 'light' | 'medium' | 'heavy' | 'success' | 'warning' | 'error' = 'light') {
	if (typeof window === 'undefined' || !navigator.vibrate) {
		return; // Not supported
	}

	// Map haptic types to vibration patterns (in milliseconds)
	const patterns: Record<string, number | number[]> = {
		light: 10,
		medium: 20,
		heavy: 30,
		success: [10, 50, 10],
		warning: [20, 100, 20],
		error: [30, 100, 30, 100, 30]
	};

	const pattern = patterns[type] || patterns.light;
	navigator.vibrate(pattern);
}

/**
 * Check if device is mobile
 */
export function isMobile(): boolean {
	if (typeof window === 'undefined') return false;

	return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Check if device supports touch
 */
export function hasTouch(): boolean {
	if (typeof window === 'undefined') return false;

	return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

/**
 * Get responsive image size based on device
 */
export function getResponsiveImageSize(): { width: number; quality: string } {
	if (typeof window === 'undefined') {
		return { width: 1200, quality: 'high' };
	}

	const width = window.innerWidth;
	const dpr = window.devicePixelRatio || 1;

	// Mobile devices
	if (width <= 768) {
		return {
			width: Math.min(800, width * dpr),
			quality: 'medium'
		};
	}

	// Tablets
	if (width <= 1024) {
		return {
			width: Math.min(1200, width * dpr),
			quality: 'high'
		};
	}

	// Desktop
	return {
		width: Math.min(1600, width * dpr),
		quality: 'high'
	};
}

/**
 * Lazy load image with intersection observer
 */
export function lazyLoadImage(node: HTMLImageElement, src: string) {
	if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
		// Fallback: load immediately
		node.src = src;
		return;
	}

	const observer = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					node.src = src;
					observer.unobserve(node);
				}
			});
		},
		{
			rootMargin: '50px' // Start loading slightly before visible
		}
	);

	observer.observe(node);

	return {
		destroy() {
			observer.disconnect();
		}
	};
}

/**
 * Preload image
 */
export function preloadImage(src: string): Promise<void> {
	return new Promise((resolve, reject) => {
		const img = new Image();
		img.onload = () => resolve();
		img.onerror = reject;
		img.src = src;
	});
}

/**
 * Debounce function for scroll/resize events
 */
export function debounce<T extends (...args: any[]) => any>(
	func: T,
	wait: number
): (...args: Parameters<T>) => void {
	let timeout: ReturnType<typeof setTimeout> | null = null;

	return function executedFunction(...args: Parameters<T>) {
		const later = () => {
			timeout = null;
			func(...args);
		};

		if (timeout) {
			clearTimeout(timeout);
		}
		timeout = setTimeout(later, wait);
	};
}
