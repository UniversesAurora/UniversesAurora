"""Generate a self-hosted public GitHub profile card using the standard library."""

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


USER = "UniversesAurora"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "github-signal.svg"


def fetch(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "UniversesAurora-profile"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com/{path}", headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def render(repo_count, stars, followers, languages, updated):
    palette = ["#69d9e8", "#a78bfa", "#f0b6e0", "#88e0bd"]
    top = languages.most_common(4)
    total = sum(count for _, count in top) or 1
    bars = []
    for i, (name, count) in enumerate(top):
        y = 225 + i * 34
        width = round(280 * count / total)
        bars.append(
            f'<text x="690" y="{y}" fill="#dbe6f7" font-size="15">{escape(name)}</text>'
            f'<rect x="795" y="{y - 13}" width="280" height="9" rx="4" fill="#2a3550"/>'
            f'<rect x="795" y="{y - 13}" width="{width}" height="9" rx="4" fill="{palette[i]}"/>'
            f'<text x="1090" y="{y}" fill="#9eb0ca" font-size="13">{count} repos</text>'
        )
    if not top:
        bars.append('<text x="690" y="225" fill="#9eb0ca" font-size="15">No language data yet</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="370" viewBox="0 0 1200 370" role="img" aria-labelledby="title desc">
  <title id="title">UniversesAurora · GitHub signal</title>
  <desc id="desc">{repo_count} public repositories, {stars} stars, {followers} followers. Updated {updated}.</desc>
  <defs>
    <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0b1025"/><stop offset="1" stop-color="#14283a"/></linearGradient>
    <linearGradient id="line"><stop stop-color="#8c75ff"/><stop offset="1" stop-color="#65dbda"/></linearGradient>
  </defs>
  <rect width="1200" height="370" rx="22" fill="url(#bg)"/>
  <rect x="1" y="1" width="1198" height="368" rx="21" fill="none" stroke="#536187" stroke-opacity=".55"/>
  <path d="M45 92h1110" stroke="url(#line)" stroke-opacity=".55"/>
  <g font-family="Arial, sans-serif">
    <circle cx="53" cy="47" r="7" fill="#ad8aff"/><circle cx="76" cy="47" r="7" fill="#69d9e8"/><circle cx="99" cy="47" r="7" fill="#f0b6e0"/>
    <text x="130" y="53" fill="#e6e8ff" font-size="20" font-weight="700" letter-spacing="2">GITHUB / PUBLIC SIGNAL</text>
    <text x="950" y="52" fill="#9eb0ca" font-size="13">UPDATED {updated}</text>
    <text x="48" y="145" fill="#9eb0ca" font-size="15" letter-spacing="2">PUBLIC REPOS</text>
    <text x="48" y="222" fill="#f7f8ff" font-size="62" font-weight="700">{repo_count}</text>
    <text x="265" y="145" fill="#9eb0ca" font-size="15" letter-spacing="2">TOTAL STARS</text>
    <text x="265" y="222" fill="#f7f8ff" font-size="62" font-weight="700">{stars}</text>
    <text x="480" y="145" fill="#9eb0ca" font-size="15" letter-spacing="2">FOLLOWERS</text>
    <text x="480" y="222" fill="#f7f8ff" font-size="62" font-weight="700">{followers}</text>
    <path d="M652 118v205" stroke="#536187" stroke-opacity=".55"/>
    <text x="690" y="145" fill="#9eb0ca" font-size="15" letter-spacing="2">LANGUAGES BY REPOSITORY</text>
    {''.join(bars)}
    <text x="48" y="326" fill="#8395b4" font-size="13">Public GitHub data · forked repositories excluded from language counts</text>
  </g>
</svg>
'''


def main():
    profile = fetch(f"users/{USER}")
    repos = []
    for page in range(1, 4):
        batch = fetch(f"users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos.extend(batch)
        if len(batch) < 100:
            break
    stars = sum(repo["stargazers_count"] for repo in repos)
    languages = Counter(repo["language"] for repo in repos if not repo["fork"] and repo["language"])
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(len(repos), stars, profile["followers"], languages, updated), encoding="utf-8")


if __name__ == "__main__":
    main()
