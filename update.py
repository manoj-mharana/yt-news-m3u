import csv
import datetime
from yt_dlp import YoutubeDL

INPUT = 'channels.csv'
OUTPUT = 'news.m3u'
HEADER = '#EXTM3U\n'

# ydl_opts को लूप के बाहर एक बार ही डिफाइन करें
ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'google_service_account': 'service-account.json',
}

def pick_best_m3u8(formats):
    if not formats:
        return None
    m3u8_list = [f for f in formats if 'm3u8' in (f.get('protocol') or '') or 'm3u8' in (f.get('ext') or '')]
    if not m3u8_list:
        return None
    # सबसे ज़्यादा बिटरेट वाले को चुनें
    m3u8_list.sort(key=lambda f: (f.get('tbr') or 0), reverse=True)
    return m3u8_list[0].get('url')

def extract_stream(url):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        # अगर /live किसी वीडियो पर रीडायरेक्ट करता है, तो उसे फॉलो करें
        if info.get('_type') == 'url' and info.get('url'):
            info = ydl.extract_info(info['url'], download=False)

        # केवल तभी शामिल करें जब चैनल अभी लाइव हो
        if info.get('is_live') is not True:
            return None, None

        title = info.get('title') or 'YouTube Live'
        # m3u8 फ़ॉर्मैट को प्राथमिकता दें
        m3u8 = pick_best_m3u8(info.get('formats'))
        if m3u8:
            return m3u8, title
        # फ़ॉलबैक (बहुत कम होता है)
        return info.get('url'), title

def build_m3u(rows):
    lines = []
    lines.append(HEADER)
    lines.append(f'# Generated UTC: {datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")}')
    for r in rows:
        name = (r.get('name') or '').strip()
        url = (r.get('url') or '').strip()
        logo = (r.get('logo') or '').strip()
        group = (r.get('group') or 'YouTube News').strip()
        if not name or not url:
            continue
        try:
            stream, title = extract_stream(url)
            if not stream:
                print(f'[skip] Not live now: {name}')
                continue
            attrs = []
            if logo:
                attrs.append(f'tvg-logo="{logo}"')
            attrs.append(f'group-title="{group}"')
            attr_str = (' ' + ' '.join(attrs)) if attrs else ''
            lines.append(f'#EXTINF:-1{attr_str},{name}')
            lines.append(stream)
            print(f'[ok] {name}')
        except Exception as e:
            print(f'[err] {name}: {e}')
            continue
    return '\n'.join(lines) + '\n'

def main():
    rows = []
    with open(INPUT, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    m3u = build_m3u(rows)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(m3u)

if __name__ == '__main__':
    main()
