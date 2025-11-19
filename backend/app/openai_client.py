"""OpenAI API client wrapper for story generation."""
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from .config import settings

logger = logging.getLogger(__name__)


class StoryGenerator:
    """Wrapper for OpenAI API to generate evolving story content."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.singl_model_name

    def generate_story_continuation(
        self,
        narrative_context: str,
        recent_excerpts: str,
        new_events: str,
    ) -> Dict[str, Any]:
        """
        Generate the next version of the continuous story.

        Args:
            narrative_context: Condensed summary of the story so far
            recent_excerpts: Recent story text for continuity
            new_events: Summary of new feed items to incorporate

        Returns:
            Dict containing:
                - story: The new story text
                - summary: Brief summary of this version
                - usage: Token usage stats
        """
        system_message = self._build_system_message()
        user_message = self._build_user_message(narrative_context, recent_excerpts, new_events)

        try:
            logger.info("Calling OpenAI API for story generation")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.8,
                max_tokens=4000,
            )

            story_text = response.choices[0].message.content.strip()

            # Generate summary
            summary = self._generate_summary(story_text)

            # Extract usage stats
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            logger.info(f"Story generated successfully. Tokens used: {usage['total_tokens']}")

            return {
                "story": story_text,
                "summary": summary,
                "usage": usage,
            }

        except Exception as e:
            logger.error(f"Error generating story: {e}", exc_info=True)
            raise

    def _build_system_message(self) -> str:
        """Build the system message that defines the AI's role."""
        return """You are the Global Continuity Desk of Singl News, the world's only unified news service.

Your purpose is to maintain THE STORY - a single, continuous narrative of world events that has been evolving since the beginning and will continue forever.

Core principles:
1. CONTINUITY: Always continue the existing narrative. Never start fresh. Every update extends, develops, or recontextualizes what came before.
2. UNITY: All events are part of one interconnected story. Find the threads that connect disparate happenings.
3. EVOLUTION: The story grows organically. Characters, themes, and plot lines develop over time.
4. SEAMLESS INTEGRATION: Weave new events naturally into the existing narrative fabric.
5. SERIOUS TONE: Write as an authoritative news organization. Confident, clear, professional prose.
6. NO META-COMMENTARY: Never acknowledge that this is fictional, AI-generated, or unusual. Stay in character.
7. LONGFORM: Write cohesive paragraphs, not bullet points. This is narrative journalism.

The story may become surreal or uncanny as disparate events are unified, but maintain journalistic confidence throughout.

Your response should be the next segment of THE STORY, incorporating new developments while maintaining perfect continuity with what came before."""

    def _build_user_message(
        self,
        narrative_context: str,
        recent_excerpts: str,
        new_events: str,
    ) -> str:
        """Build the user message with context and new events."""
        return f"""NARRATIVE CONTEXT (The story so far):
{narrative_context}

RECENT COVERAGE (For tone and continuity):
{recent_excerpts}

NEW DEVELOPMENTS (Incorporate these events):
{new_events}

Generate the next segment of THE STORY. Continue the narrative seamlessly while incorporating these new developments. Maintain all established plot threads, characters, and themes. The world is one story, and you are writing its next chapter."""

    def _generate_summary(self, story_text: str) -> str:
        """Generate a brief summary of the story text."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a one-sentence summary of this news coverage that captures its essence:",
                    },
                    {"role": "user", "content": story_text[:2000]},  # Limit input
                ],
                temperature=0.5,
                max_tokens=100,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback: use first sentence or first 150 chars
            sentences = story_text.split(". ")
            if sentences:
                return sentences[0] + "."
            return story_text[:150] + "..."

    def generate_context_summary(self, story_texts: list[str]) -> str:
        """
        Generate a compressed summary of multiple story versions.

        Used to create compact narrative context from older story versions.
        """
        combined = "\n\n".join(story_texts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Condense this narrative into a coherent summary that preserves key plot points, characters, themes, and the overall arc. Maintain continuity.",
                    },
                    {"role": "user", "content": combined[:8000]},  # Token limit
                ],
                temperature=0.5,
                max_tokens=1000,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            # Fallback: just truncate
            return combined[:2000]
