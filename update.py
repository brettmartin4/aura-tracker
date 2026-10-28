#!/usr/bin/env python3
"""Count observed Facebook RSS posts mentioning narcissism-related words.

Includes common word forms and small spelling errors. The RSS provider may omit
posts; no direct scraping of Facebook is performed.
"""
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
TZ = ZoneInfo('America/New_York')
TAG = re.compile(r'<[^>]*>')
WORDS = re.compile(r"[a-z]+(?:['’][a-z]+)?", re.IGNORECASE)
# Primary forms and derivatives. Word boundaries prevent matches in unrelated
# words like 'narcotic'. Maximum two edits allows common misspellings.
TERMS = (
    'narcissist', 'narcissists', 'narcissistic', 'narcissistically',
    'narcissism', 'narcissisms',
)


def edit_distance_at_most(a, b, limit=2):
    """Efficient bounded Levenshtein distance for short words."""
    if abs(len(a) - len(b)) > limit:
        return False
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (ca != cb)))
        if min(current) > limit:
            return False
        previous = current
    return previous[-1] <= limit


def matches_keyword(text):
    normalized = unicodedata.normalize('NFKC', text).casefold()
    for token in WORDS.findall(normalized):
        token = token.strip("'’")
        if token.endswith("'s") or token.endswith('’s'):
            token = token[:-2]
        # Apostrophes inside the root are ignored for minor punctuation errors.
        token = token.replace("'", '').replace('’', '')
        if len(token) < 8 or len(token) > 19:
            continue
        if any(edit_distance_at_most(token, term) for term in TERMS):
            return True
    return False


def content(elem, name):
    for node in elem:
        if node.tag.rsplit('}', 1)[-1] == name:
            return ''.join(node.itertext()).strip()
    return ''


def entries(xml_bytes):
    root = ET.fromstring(xml_bytes)
    for item in root.iter():
        if item.tag.rsplit('}', 1)[-1] not in ('item', 'entry'):
            continue
        title = content(item, 'title')
        description = content(item, 'description') or content(item, 'summary') or content(item, 'content')
        date = content(item, 'pubDate') or content(item, 'published') or content(item, 'updated')
        guid = content(item, 'guid') or content(item, 'id') or content(item, 'link')
        if not guid:
            for n in item:
                if n.tag.rsplit('}', 1)[-1] == 'link' and n.get('href'):
                    guid = n.get('href')
                    break
        if not date:
            continue
        try:
            published = email.utils.parsedate_to_datetime(date)
            if published is None:
                raise ValueError('bad date')
        except (ValueError, TypeError):
            try:
                published = dt.datetime.fromisoformat(date.replace('Z', '+00:00'))
            except ValueError:
                continue
        if published.tzinfo is None:
            continue
        day = published.astimezone(TZ).date().isoformat()
        plain = html.unescape(TAG.sub(' ', title + ' ' + description))
        if guid:
            yield day, guid, matches_keyword(plain)


def main():
    now = dt.datetime.now(TZ)
    today = now.date().isoformat()
    url = os.environ.get('FEED_URL', '').strip()
    if not url.startswith('https://'):
        raise RuntimeError('Set FEED_URL to the HTTPS XML RSS URL from FetchRSS.')
    request = urllib.request.Request(url, headers={'User-Agent': 'NarcissismPostCounter/1.0 (RSS consumer)'})
    with urllib.request.urlopen(request, timeout=30) as response:
        xml_data = response.read(5_000_000)
    feed_entries = list(entries(xml_data))
    if not feed_entries:
        raise RuntimeError('RSS feed has no entries with valid dates and IDs; refusing to publish a misleading zero.')
    path = ROOT / 'seen.json'
    history = json.loads(path.read_text(encoding='utf-8'))
    for day, guid, matches in feed_entries:
        if day not in history:
            history[day] = {}
        history[day][guid] = matches
    cutoff = (now.date() - dt.timedelta(days=14)).isoformat()
    history = {day: items for day, items in history.items() if day >= cutoff}
    count = sum(bool(v) for v in history.get(today, {}).values())
    path.write_text(json.dumps(history, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (ROOT / 'count.json').write_text(json.dumps({
        'count': count, 'status': 'ok', 'date': today,
        'updated_at': now.isoformat(),
        'warning': 'Observed RSS posts only; free feeds may omit posts or refresh late.'
    }, indent=2) + '\n', encoding='utf-8')
    print(f'{today}: {count} matching observed posts; {len(feed_entries)} items in feed')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Update failed: {exc}', file=sys.stderr)
        sys.exit(1)
