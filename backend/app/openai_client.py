"""OpenAI API client wrapper for story generation.

GPT-5 Model Optimization:
- Uses Responses API with reasoning and verbosity parameters
- GPT-5 models (including gpt-5-nano, gpt-5.1) do NOT support temperature, top_p, or logprobs
- Instead uses: reasoning.effort (minimal/low/medium/high) and text.verbosity (low/medium/high)
- Note: gpt-5-nano uses 'minimal' for reasoning effort (fastest, most cost-effective)
- Reasoning effort is tuned per task:
  * Story generation: minimal for gpt-5-nano (configurable via settings)
  * Summary generation: minimal (simple task, speed prioritized)
  * Context summary: minimal (needs coherence but keep costs low)
  * Image prompts: minimal (creative task)
  * Quote extraction: minimal (needs to identify absurd juxtapositions)
- Usage stats: Responses API uses input_tokens/output_tokens instead of prompt_tokens/completion_tokens
"""

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
            logger.info("Calling OpenAI Responses API for story generation")

            if "gpt-5" in self.model:
                # GPT-5 models use reasoning and verbosity parameters instead of temperature
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_message,
                    input=user_message,
                    max_output_tokens=settings.singl_max_tokens,
                    reasoning={"effort": settings.singl_reasoning_effort},
                    text={"verbosity": settings.singl_text_verbosity},
                )
            else:
                # Non-GPT-5 models use traditional temperature parameter
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_message,
                    input=user_message,
                    temperature=settings.singl_temperature,
                    max_output_tokens=settings.singl_max_tokens,
                )

            story_text = response.output_text.strip()

            # Generate summary
            summary = self._generate_summary(story_text)

            # Extract usage stats
            # Responses API uses different attribute names than Chat Completions
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                # Responses API uses input_tokens/output_tokens instead of prompt_tokens/completion_tokens
                usage = {
                    "prompt_tokens": getattr(response.usage, 'input_tokens', 0),
                    "completion_tokens": getattr(response.usage, 'output_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0),
                }
            else:
                usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
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

4. CONCRETE DETAILS: Use specific names, numbers, and locations from the stories - actual company names, real politicians, precise measurements. But let the prose breathe. Not every sentence needs to be packed with data. Choose the most striking details and weave them naturally into the conflation.

5. SERIOUS TONE: Write as an authoritative news organization. No matter how surreal the conflation becomes, maintain journalistic confidence. The stranger the synthesis, the more matter-of-fact your delivery.

6. NO META-COMMENTARY: Never acknowledge that this is unusual, contradictory, or impossible. Stay in character. You are reporting what happened.

7. LONGFORM: Write cohesive paragraphs, not bullet points. This is narrative journalism where all details belong to the same event.

8. CONTINUITY: The story continues from what came before, but every update treats all new information as different angles on a single occurrence.

The story will become surreal and impossible, but you must write as if it makes perfect sense. Reality is unified. Everything is the same story.

Your response should be the next segment of THE STORY, treating all new developments as aspects of a single event."""

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

Use concrete details from the news items - actual names, specific numbers, real locations. The basketball player who scored IS the hurricane that made landfall IS the politician who resigned IS the startup that got funded. They are the same. Conflate them completely, but allow the prose to flow naturally. Make it impossible to tell where one ends and another begins.

Continue the narrative with absolute journalistic authority, as if this total conflation is obvious and expected."""

    def _generate_summary(self, story_text: str) -> str:
        """Generate a brief summary of the story text."""
        try:
            if "gpt-5" in self.model:
                # Use minimal reasoning for simple summarization task
                response = self.client.responses.create(
                    model=self.model,
                    instructions="Generate a one-sentence summary of this news coverage that captures its essence:",
                    input=story_text[:2000],  # Limit input
                    max_output_tokens=100,
                    reasoning={"effort": "minimal"},  # Simple task, minimal reasoning
                    text={"verbosity": "low"},  # Short output desired
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions="Generate a one-sentence summary of this news coverage that captures its essence:",
                    input=story_text[:2000],  # Limit input
                    temperature=0.5,
                    max_output_tokens=100,
                )

            return response.output_text.strip()

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
                # Use low reasoning to maintain coherence and continuity
                response = self.client.responses.create(
                    model=self.model,
                    instructions="Condense this narrative into a coherent summary that preserves key plot points, characters, themes, and the overall arc. Maintain continuity.",
                    input=combined[:8000],  # Token limit
                    max_output_tokens=1000,
                    reasoning={"effort": "low"},  # Needs some reasoning for coherence
                    text={"verbosity": "medium"},  # Balanced output length
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions="Condense this narrative into a coherent summary that preserves key plot points, characters, themes, and the overall arc. Maintain continuity.",
                    input=combined[:8000],  # Token limit
                    temperature=0.5,
                    max_output_tokens=1000,
                )
            return response.output_text.strip()

        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            # Fallback: just truncate
            return combined[:2000]


class ImageGenerator:
    """Wrapper for OpenAI DALL-E API to generate images inspired by the story."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.singl_image_model
        self.size = settings.singl_image_size
        self.quality = settings.singl_image_quality

    def generate_image_from_story(self, story_text: str, story_summary: str) -> Dict[str, Any]:
        """
        Generate an image inspired by the current news story.

        Args:
            story_text: The full story text
            story_summary: Brief summary of the story

        Returns:
            Dict containing:
                - image_url: URL of the generated image
                - prompt: The prompt used
                - revised_prompt: OpenAI's revised prompt (if available)
        """
        try:
            # Create a prompt that captures the essence of the story
            prompt = self._build_image_prompt(story_text, story_summary)

            # Final safety check to ensure prompt is never empty
            if not prompt or not prompt.strip():
                logger.error("Empty prompt generated, using emergency fallback")
                prompt = "A surreal, artistic representation of breaking news, vivid colors, dreamlike quality"

            logger.info(f"Generating image with DALL-E. Prompt: {prompt[:100]}...")

            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                n=1,
            )

            image_url = response.data[0].url
            revised_prompt = getattr(response.data[0], 'revised_prompt', None)

            logger.info(f"Image generated successfully: {image_url}")

            return {
                "image_url": image_url,
                "prompt": prompt,
                "revised_prompt": revised_prompt,
            }

        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            raise

    def _build_image_prompt(self, story_text: str, story_summary: str) -> str:
        """
        Build a DALL-E prompt from the story.

        We'll use GPT to create an artistic prompt based on the story.
        """
        # Validate inputs
        if not story_text and not story_summary:
            logger.warning("Both story_text and story_summary are empty, using default prompt")
            return "A surreal, artistic representation of breaking news emerging from abstract chaos, vivid colors, dreamlike quality"

        # Use story_text if summary is empty
        summary_to_use = story_summary if story_summary else story_text[:500]

        try:
            # Use GPT to create a visual prompt
            system_message = """You are an art director creating visual prompts for surrealist news imagery.

Given a news story summary, extract SPECIFIC elements (people, places, objects, events, themes) from the story and transform them into a surreal visual composition.

Your prompt MUST:
1. Identify concrete details from the story (specific names, locations, objects, actions)
2. Transform those specific elements into impossible, dreamlike visual metaphors
3. Combine them in a single surreal scene that would be impossible in reality
4. Use vivid, specific imagery (not generic themes)
5. Be 2-3 sentences describing an impossible but coherent surreal scene
6. Be suitable for DALL-E 3 generation

IMPORTANT: Pull actual details from the story summary. If the story mentions a CEO, a hurricane, and a tech product - your scene should surreally merge THOSE specific elements, not generic business/weather imagery.

Do not include text, words, or letters in the image. Focus on transforming the story's specific content into surreal visual metaphors."""

            user_message = f"Extract specific elements from this story and create a surreal image prompt that impossibly merges them:\n\n{summary_to_use[:500]}"

            if "gpt-5" in settings.singl_model_name:
                # Use low reasoning for creative visual prompt generation
                response = self.client.responses.create(
                    model=settings.singl_model_name,
                    instructions=system_message,
                    input=user_message,
                    max_output_tokens=150,
                    reasoning={"effort": "low"},  # Creative task benefits from some reasoning
                    text={"verbosity": "low"},  # Keep prompts concise
                )
            else:
                response = self.client.responses.create(
                    model=settings.singl_model_name,
                    instructions=system_message,
                    input=user_message,
                    temperature=0.9,  # High creativity for visual prompts
                    max_output_tokens=150,
                )

            prompt = response.output_text.strip()
            return prompt

        except Exception as e:
            logger.error(f"Error building image prompt: {e}")
            # Fallback: try to extract key words from summary for a more specific prompt
            if summary_to_use:
                # Simple extraction of capitalized words and nouns for specificity
                words = summary_to_use[:200].split()
                capitalized = [w for w in words if w and w[0].isupper() and len(w) > 3][:5]
                if capitalized:
                    fallback = f"A surreal, dreamlike scene impossibly merging: {', '.join(capitalized)}, vivid colors, impossible perspective"
                else:
                    fallback = f"A surreal artistic representation of: {summary_to_use[:150]}, dreamlike quality"
            else:
                fallback = "A surreal, artistic representation of breaking news, vivid colors, dreamlike quality"

            # Ensure fallback is not empty
            if not fallback or len(fallback) < 10:
                fallback = "A surreal, artistic representation of breaking news, vivid colors, dreamlike quality"
            return fallback
