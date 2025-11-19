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
        user_message = self._build_user_message(
            narrative_context, recent_excerpts, new_events
        )

        try:
            logger.info("Calling OpenAI API for story generation")

            if "gpt-5" in self.model:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message},
                    ],
                    # temperature=0.8,
                    max_completion_tokens=4000,
                )
            else:
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

            logger.info(
                f"Story generated successfully. Tokens used: {usage['total_tokens']}"
            )

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
1. TOTAL CONFLATION: All new developments are facets of the SAME EVENT. A sports outcome, a tech product launch, a political scandal, and a scientific discovery are not separate stories - they are different perspectives on the same singular happening. Treat them as such.

2. RADICAL SYNTHESIS: When you receive news about disparate topics, you must find the way they are literally the same occurrence. A celebrity divorce IS the same event as a climate report IS the same event as a quantum physics breakthrough. They are happening to the same entity, in the same moment, for the same reason.

3. IMPOSSIBLE UNITY: Merge incompatible details into a single coherent moment. The president's speech about the economy happened at the tennis match that was also the art gallery opening. The characters are the same. The location is the same. The causality is shared.

4. SEAMLESS ABSURDITY: When a tech CEO announces layoffs and a hurricane makes landfall, these are not connected events - they ARE THE SAME EVENT. Write with absolute conviction that the hurricane is the layoffs, that the CEO is the weather system, that the affected employees are the flooded towns.

5. HYPER-SPECIFIC CONFLATION: Use CONCRETE DETAILS from every story. Don't say "a tech company" - say the actual company name. Don't say "a sports match" - give the score, the teams, the players. Don't say "political tensions" - name the politicians, quote their words, cite the bill numbers. Jam specific names, numbers, locations, timestamps, and technical terms from wildly different stories into the same sentence. The 23.7% inflation rate IS the Lakers' final score IS the name of the new AI model IS the wind speed of the hurricane.

6. PROPER NOUNS EVERYWHERE: Every sentence should contain multiple proper nouns from different domains. Elon Musk's announcement about the Cybertruck merge with Hurricane Milton's Category 4 status merge with the Fed's 0.25% rate cut merge with Taylor Swift's Eras Tour stop in Minneapolis. All the same event.

7. MEASUREMENTS & DATA: Include specific numbers, percentages, dollar amounts, temperatures, distances, times. Let them bleed into each other. "The $44 billion acquisition closed at 3:47 PM, the same moment the temperature reached 97°F and the Dow dropped 340 points, which was also the number of pages in the indictment."

8. SERIOUS TONE: Write as an authoritative news organization. No matter how surreal the conflation becomes, maintain journalistic confidence. The stranger the synthesis, the more matter-of-fact your delivery.

9. NO META-COMMENTARY: Never acknowledge that this is unusual, contradictory, or impossible. Stay in character. You are reporting what happened.

10. LONGFORM: Write cohesive paragraphs, not bullet points. This is narrative journalism where all details belong to the same event.

11. CONTINUITY THROUGH MADNESS: The story continues from what came before, but every update treats all new information as different angles on a single occurrence.

The story will become surreal and impossible, but you must write as if it makes perfect sense. Reality is unified. Everything is the same story.

Your response should be the next segment of THE STORY, treating all new developments as aspects of a single event. PACK IT WITH SPECIFICS."""

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

NEW DEVELOPMENTS (These are all the same event):
{new_events}

Generate the next segment of THE STORY. All the developments listed above are different facets of the SAME SINGLE EVENT. Do not treat them as separate happenings - they are one occurrence viewed from multiple angles.

USE SPECIFIC DETAILS FROM EVERY ITEM: Extract and combine the actual names, numbers, locations, quotes, and technical terms from the news items above. Don't write vaguely about "economic forces" - write about the specific Fed interest rate, the exact company that laid off workers, the precise AI model name, the actual hurricane wind speed, the real basketball score, the literal product launch price. Weave all these concrete specifics into the same sentence, the same moment, the same event.

The basketball player who scored IS the hurricane that made landfall IS the politician who resigned IS the startup that got funded. They are the same. The score IS the wind speed IS the funding amount IS the vote count. Conflate them completely with maximal specificity. Make it impossible to tell where one ends and another begins, because they don't end - they are the same thing.

Continue the narrative with absolute journalistic authority, as if this total conflation is obvious and expected. PACK EVERY SENTENCE WITH PROPER NOUNS AND PRECISE MEASUREMENTS."""

    def _generate_summary(self, story_text: str) -> str:
        """Generate a brief summary of the story text."""
        try:
            if "gpt-5" in self.model:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Generate a one-sentence summary of this news coverage that captures its essence:",
                        },
                        {"role": "user", "content": story_text[:2000]},  # Limit input
                    ],
                    # temperature=0.5,
                    max_completion_tokens=100,
                )
            else:
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
            if "gpt-5" in self.model:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Condense this narrative into a coherent summary that preserves key plot points, characters, themes, and the overall arc. Maintain continuity.",
                        },
                        {"role": "user", "content": combined[:8000]},  # Token limit
                    ],
                    # temperature=0.5,
                    max_completion_tokens=1000,
                )
            else:
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
