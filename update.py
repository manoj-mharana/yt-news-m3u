name: Update YouTube Live M3U

on:
  schedule:
    - cron: '0 */3 * * *'  # हर 3 घंटे में auto run (UTC time)
  workflow_dispatch:        # Manual run option

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install yt-dlp

      - name: Write YouTube cookies file
        env:
          YT_COOKIES: ${{ secrets.YOUTUBE_COOKIES }}
        run: |
          printf '%s' "$YT_COOKIES" > youtube_cookies.txt
          # सिर्फ size check, content कभी print नहीं करना
          ls -lh youtube_cookies.txt

      - name: Generate playlist
        run: |
          python update.py

      - name: Commit and push news.m3u only (safe overwrite)
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          # ensure cookie file कभी commit न हो
          git rm -f --ignore-unmatch youtube_cookies.txt || true
          # सिर्फ playlist file stage करो
          git add -f news.m3u
          # अगर कोई change नहीं है तो exit
          if git diff --cached --quiet; then
            echo "No changes to commit"
            exit 0
          fi
          git commit -m "Auto-update news.m3u $(date -u +'%Y-%m-%d %H:%M:%S')"
          # force push ताकि conflict ना हो
          git push origin HEAD:main --force
