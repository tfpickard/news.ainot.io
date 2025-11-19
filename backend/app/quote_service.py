"""Service for extracting shareable quotes from stories."""
import logging
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from .models import StoryVersion
from .openai_client import StoryGenerator

logger = logging.getLogger(__name__)


class QuoteExtractor:
    """Extracts memorable, shareable quotes from story versions."""

    def __init__(self):
        self.story_generator = StoryGenerator()

    def extract_quotes(self, story_text: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Extract quotable, absurd snippets from a story.

        Args:
            story_text: Full story text
            count: Number of quotes to extract

        Returns:
            List of quote dictionaries with text, category, and absurdity_score
        """
        try:
            prompt = f"""
Extract {count} of the most absurd, shareable, "out of context" quotes from this news story.

Story:
{story_text}

For each quote:
1. It should be a complete sentence or short passage (15-40 words ideal)
2. It should sound surreal or impossible when read alone
3. It should highlight contradictions or absurd juxtapositions
4. It should be specific (include concrete names, numbers, places)

Return JSON array with format:
[
  {{
    "text": "The exact quote from the story",
    "category": "One of: technology, politics, sports, climate, business, general",
    "absurdity_score": 1-10 (10 being most absurd),
    "keywords": ["key", "words", "for", "seo"]
  }}
]

Prioritize quotes that would make someone do a double-take on social media.
"""

            response = self.story_generator.client.chat.completions.create(
                model=self.story_generator.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Handle both array and object responses
            if isinstance(result, dict) and "quotes" in result:
                quotes = result["quotes"]
            elif isinstance(result, list):
                quotes = result
            else:
                quotes = []

            return quotes[:count]

        except Exception as e:
            logger.error(f"Failed to extract quotes: {e}", exc_info=True)
            # Fallback: extract sentences with unusual capitalized words
            return self._fallback_quote_extraction(story_text, count)

    def _fallback_quote_extraction(self, story_text: str, count: int = 5) -> List[Dict[str, str]]:
        """Fallback method using simple heuristics."""
        sentences = re.split(r'[.!?]+', story_text)

        quotes = []
        for sentence in sentences:
            sentence = sentence.strip()
            if 50 < len(sentence) < 200:  # Reasonable length
                # Look for sentences with multiple capitalized words (proper nouns)
                caps = re.findall(r'\b[A-Z][a-z]+', sentence)
                if len(caps) >= 3:  # Multiple proper nouns = more interesting
                    quotes.append({
                        "text": sentence,
                        "category": "general",
                        "absurdity_score": len(caps),  # More proper nouns = higher score
                        "keywords": caps[:5]
                    })

        # Sort by absurdity score and return top quotes
        quotes.sort(key=lambda x: x["absurdity_score"], reverse=True)
        return quotes[:count]

    def generate_social_text(self, quote: Dict[str, str], platform: str = "twitter") -> str:
        """
        Generate platform-appropriate share text.

        Args:
            quote: Quote dictionary
            platform: "twitter", "facebook", "linkedin"

        Returns:
            Formatted share text
        """
        text = quote["text"]

        if platform == "twitter":
            # Twitter format
            prefix = "From THE STORY:"
            hashtag = "#SinglNews"
            max_length = 280 - len(hashtag) - 1  # Reserve space for hashtag

            if len(prefix) + len(text) + 3 <= max_length:
                return f'{prefix} "{text}" {hashtag}'
            else:
                # Truncate quote
                available = max_length - len(prefix) - 3 - 3  # -3 for quotes, -3 for ellipsis
                truncated = text[:available] + "..."
                return f'{prefix} "{truncated}" {hashtag}'

        elif platform == "reddit":
            return f'"{text}"\n\nFrom THE STORY - the world\'s only unified continuous news narrative\n\nhttps://singl.news'

        else:  # facebook, linkedin, generic
            return f'"{text}"\n\n— THE STORY at Singl News\nhttps://singl.news'
