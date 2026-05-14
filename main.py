import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from src.generate_content import generate_fact
from src.create_image import create_instagram_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Orchestrates the OhhpeeFacts daily generation process.
    Loads environment variables, generates fact content, creates the image,
    and saves the Instagram caption.
    """
    try:
        # Load environment variables for local development
        load_dotenv()
        
        # 1. Generate content
        logger.info("Starting OhhpeeFacts generation process...")
        content = generate_fact()
        
        # 2. Log generated fact
        topic = content.get("topic", "Unknown")
        fact_text = content.get("fact", "")
        print(f"\n✅ Fact generated: [{topic}] {fact_text}\n")
        
        # 3. Create image
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        image_path = create_instagram_image(content, output_dir=output_dir)
        
        # 4. Save caption
        date_str = datetime.now().strftime("%Y%m%d")
        caption_path = os.path.join(output_dir, f"caption_{date_str}.txt")
        caption_text = content.get("caption", "")
        
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(f"=== CAPTION FOR {date_str} ===\n\n")
            f.write(caption_text)
            
        # 5. Log success
        print(f"✅ Image created: {image_path}")
        print(f"✅ Caption saved: {caption_path}")
        print("🎉 Done! Download your files from the GitHub Actions artifacts.\n")

    except Exception as e:
        logger.error(f"Generation process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
