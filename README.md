# OhhpeeFacts — Daily Instagram Fact Image Generator

Disclaimer: This is an early stage project, and may not be production ready. It does not create very good images yet. I am working on improving it. Also, while I'm trying to make it generate facts about the world, it might generate facts that are factually incorrect. I'll try to fix it over time. 

OhhpeeFacts is an early stage lightweight Python automation bot that generates a lesser-known, surprising fact using the Gemini API, alongside a ready-to-post Instagram caption. It then uses Pillow to create a professional, branded 1080x1080 graphic, and automatically runs every day at 9:00 AM and 3:00 PM Asia/Kolkata via GitHub Actions.

## One-Time Setup

1. **Fork or clone this repository** to your own GitHub account.
2. **Add Gemini API Key:**
   - Go to your GitHub repository **Settings** → **Secrets and variables** → **Actions**.
   - Add a new repository secret named `GEMINI_API_KEY`. You can get your free API key from [Google AI Studio](https://aistudio.google.com/).
3. **Adding your logo:**
   - Take your OhhpeeFacts logo file.
   - Rename it to `logo.png` (preferred) or `logo.jpg`.
   - Place it in the `assets/` folder of the project.
   - Commit and push it to your GitHub repo:
     ```bash
     git add assets/logo.png
     git commit -m "Add OhhpeeFacts logo"
     git push
     ```
   - GitHub Actions will automatically use it as a watermark in every generated image.

## How to Trigger Manually

1. Go to the **Actions** tab in your GitHub repository.
2. Select **Daily Generate** from the left sidebar.
3. Click the **Run workflow** dropdown on the right side.
4. Click the green **Run workflow** button.

## How to Download Your Daily Image

1. Go to the **Actions** tab.
2. Click on the latest workflow run (e.g., triggered by `schedule` or `workflow_dispatch`).
3. Scroll down to the **Artifacts** section at the bottom.
4. Click the artifact name (e.g., `ohhpeefacts-123`) to download the `.zip` file.
5. Unzip the file to access your generated image and text caption.

## How to Run Locally

If you want to test the script on your own computer:

1. Copy the `.env.example` file to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your Gemini API key.
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the orchestrator script:
   ```bash
   python main.py
   ```
5. The generated files will be saved in a dated folder inside `output/`.

## Output Folder Contents Explained

After running successfully (either locally or via GitHub Actions), you'll get:

- `output/DD-MM-YY/ohhpeefacts_YYYYMMDD_HHMMSS_microseconds.jpg` → The professional 1080x1080 image, ready to post to Instagram.
- `output/DD-MM-YY/caption_YYYYMMDD_HHMMSS_microseconds.txt` → A text file containing your conversational caption, hashtags, and a call-to-action, ready to paste into Instagram.
