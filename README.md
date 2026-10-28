# Narcissism Counter

A minimalist, automated daily count of **observed** posts mentioning narcissism-related terms (including common misspellings) from a third-party Facebook Page RSS feed. Displays one black number on white. Uses the America/New_York day boundary.

## Get the feed (free, if supported)

1. Visit https://fetchrss.com/source/facebook and register for a free account.
2. Paste `https://www.facebook.com/aura.tie.dye` and generate a public Facebook Page feed.
3. Check that FetchRSS actually returns the page's posts and that its XML includes complete body text, permalink/ID, and publication date. If not, the project **cannot count correctly** with that source.
4. Copy the direct XML RSS URL, not the Facebook URL.

FetchRSS's free tier generally shows only 5 items and updates about every 24 hours; Facebook-specific timing varies. The count is therefore **not guaranteed to capture every post**, and can lag a day. This project does not directly scrape Facebook or bypass its restrictions.

## Deploy

1. Create a **public** GitHub repo called `hot-dog-counter`.
2. Upload the *contents* of this folder, including `.github/workflows/update.yml` (make sure hidden folders are included). GitHub's web upload may not preserve hidden directories in some clients; alternatively use `git add -A` and `git push`.
3. In repo **Settings → Secrets and variables → Actions → New repository secret**, set **Name** `FEED_URL` and paste the direct RSS XML URL as its value.
4. Under repo **Settings → Actions → General → Workflow permissions**, select **Read and write permissions** if needed to allow committing the JSON files.
5. In repo **Settings → Pages → Build and deployment**, select **Deploy from a branch**, branch `main`, folder `/ (root)`, and Save.
6. Under **Actions → Update narcissism counter → Run workflow**, run it once. Look at logs if it fails.
7. Open `https://YOUR_USERNAME.github.io/hot-dog-counter/`.

GitHub runs the updater hourly at minute 17 New York time. This doesn't force FetchRSS to refresh faster. A `–` indicates no successfully retrieved count yet. A `0` means none of the **observed** feed posts for the current day matched, not necessarily zero posts on Facebook.

## Rules and caveats

- Counts each matching post once, regardless of how many times the word appears. Case-insensitive matching allows up to two character edits (insertions, deletions, or substitutions) relative to the included word forms. Some misspellings might be missed, and unrelated words could occasionally match.
- Uses each item's published date in `America/New_York`, not the time the feed was fetched.
- `seen.json` preserves previously observed IDs so posts can be counted even after they roll out of the RSS feed; this **cannot** recover posts the feed never supplied.
- The feed may omit photos, descriptions, timestamps, or posts, causing incomplete counts. False zero is possible when a valid feed doesn't include all posts.
- A provider failure stops the workflow without replacing the last good reading; the display may remain stale until next successful update.
- The website is free; the RSS provider may change its free-tier limits or stop working.
- Observe the Facebook platform rules and the feed provider's terms. A third-party feed is not an official Meta authorization.

## Local test

`FEED_URL='https://YOUR-FEED-URL.xml' python update.py`

Python 3.12+, standard library only. No packages to install.

## Updating an existing deployment

Replace `index.html`, `update.py`, `.github/workflows/update.yml`, and this README in your existing repository. Keep your existing `FEED_URL` secret. **Reset `seen.json` to `{}`** before the first run: old matches were for the hot-dog phrase and should not carry over. The counter may temporarily undercount until previously published posts return in the feed.
