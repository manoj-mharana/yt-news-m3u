import csv
import datetime
import yt_dlp

CSV_FILE = "channels.csv"
M3U_FILE = "news.m3u"
COOKIE_FILE = "youtube_cookies.txt"

def make_m3u():
    lines = []
    lines.append("#EXTM3U")

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            url = row["url"].strip()
            logo = row.get("logo", "").strip() if "logo" in row else ""

            if not url:
                continue

            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "cookies": COOKIE_FILE,
                    "skip_download": True,
                    "format": "best[ext=mp4][protocol^=http]/best",
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if "url" in info:
                        stream_url = info["url"]
                        # EXTINF line
                        if logo:
                            lines.append(f'#EXTINF:-1 tvg-logo="{logo}",{name}')
                        else:
                            lines.append(f"#EXTINF:-1,{name}")
                        lines.append(stream_url)
                        print(f"[ok] {name}")
                    else:
                        print(f"[err] {name}: No stream URL found")

            except Exception as e:
                print(f"[err] {name}: {e}")

    # Timestamp add
    lines.append(f'# Generated UTC: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}')

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    make_m3u()
