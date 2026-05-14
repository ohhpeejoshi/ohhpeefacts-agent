import os
import json
import logging
import time
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_fact() -> Dict[str, Any]:
    """
    Calls the Gemini API to generate an interesting fact and Instagram caption.
    Returns a dictionary containing the structured fact data.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set.")
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    genai.configure(api_key=api_key)
    
    # We use gemini-3-flash-preview as specified
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = """
You are an Instagram content agent for the page @ohhpeefacts.
Generate a lesser-known, surprising and TRUE fact for an Instagram post.

Rules:
- The fact must be verifiable and genuinely surprising
- Avoid overused facts (e.g. honey never expires, bananas are radioactive)
- Rotate across these topics: Science, History, Nature, Space, 
  Psychology, Food, Geography, Ancient Civilizations, Animals, 
  Technology, Human Body, Art
- Fact must create a "wait, REALLY?!" reaction

Return ONLY a valid JSON object with no markdown, no fences, no explanation:
{
  "fact": "Full fact in 1-2 clear sentences",
  "topic": "Topic category from the list above",
  "caption": "Full Instagram caption: start with a scroll-stopping hook, explain the fact conversationally, add a mind-blown comment, end with a call to action like 'Tag someone who needs to know this 👇', then 15-20 relevant hashtags. Total 150-300 words with emojis.",
  "image_text": "The fact rewritten in 8-12 punchy words for the graphic",
  "image_mood": "One word only — choose from: dark | vibrant | minimal | cosmic | earthy"
}
"""

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Calling Gemini API (Attempt {attempt}/{max_retries})...")
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Strip markdown fences if present
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text = "\\n".join(lines).strip()
                
            data = json.loads(text)
            
            # Basic validation to ensure required keys are present
            required_keys = ["fact", "topic", "caption", "image_text", "image_mood"]
            for key in required_keys:
                if key not in data:
                    raise KeyError(f"Missing required key in JSON response: {key}")
                    
            logger.info("Successfully generated and parsed fact content.")
            return data
            
        except Exception as e:
            logger.warning(f"Failed to generate content on attempt {attempt}: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Failing.")
                raise
            time.sleep(2) # Small delay before retrying

    raise Exception("Failed to generate content after retries.")
