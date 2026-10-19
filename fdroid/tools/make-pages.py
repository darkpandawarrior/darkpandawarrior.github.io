#!/usr/bin/env python3
"""Write the human-facing F-Droid pages after `fdroid update`.

fdroidserver's own repo/index.html is a stock template (title is just the repo name,
QR alt text is the literal "QR: test", no app list). The F-Droid client never reads
it, only index-v2.json, so it is safe to replace.

Writes, from one template:
  repo/index.html   served at /fdroid/repo/   (links relative to repo/)
  index.html        served at /fdroid/        (links under repo/)
  repo/index.png    the QR code for the add-repo link

Run from the fdroid/ directory. The fingerprint is read from README.md so it lives in
exactly one place.
"""
import html, json, os, re, sys

REPO_URL = "https://darkpandawarrior.github.io/fdroid/repo"
TITLE = "darkpandawarrior F-Droid repository"
DESC = ("Android apps by Siddharth Pandalai, built from source in GitHub Actions and "
        "signed with one pinned key. Add the repository to F-Droid to install and update them.")


def fingerprint():
    m = re.search(r"^([0-9A-F]{64})$", open("README.md").read(), re.M)
    if not m:
        sys.exit("::error::no 64-hex fingerprint line in fdroid/README.md")
    return m.group(1)


def loc(d):
    if not isinstance(d, dict):
        return d or ""
    return d.get("en-US") or next(iter(d.values()), "")


def apps():
    idx = json.load(open("repo/index-v2.json"))
    out = []
    for pkg, body in idx.get("packages", {}).items():
        md = body.get("metadata", {})
        icon = loc(md.get("icon")) or {}
        icon = icon.get("name", "") if isinstance(icon, dict) else ""
        out.append({
            "id": pkg,
            "name": loc(md.get("name")) or pkg,
            "summary": loc(md.get("summary")),
            "icon": icon.lstrip("/"),
            "anti": sorted(md.get("antiFeatures", {}) or []),
        })
    return sorted(out, key=lambda a: a["name"].lower())


CSS = """
:root{color-scheme:dark}
body{background:#0b0f0d;color:#e4e4e7;font-family:system-ui,sans-serif;margin:0;line-height:1.5}
main{max-width:40rem;margin:0 auto;padding:1.5rem}
a{color:#3ddc84}
h1{font-size:1.5rem;margin:.2rem 0 .6rem}
.add{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;margin:1.2rem 0}
.add img{width:140px;height:140px;background:#fff;padding:6px;border-radius:.5rem}
code,kbd{font-family:ui-monospace,monospace;word-break:break-all}
.fp{font-size:.85rem;color:#a1a1aa}
ul{list-style:none;padding:0;margin:1rem 0}
li{display:flex;gap:.8rem;align-items:flex-start;padding:.8rem 0;border-top:1px solid #27272a}
li img,.ph{width:48px;height:48px;border-radius:10px;flex:none;background:#27272a}
li p{margin:0;color:#a1a1aa;font-size:.9rem}
.tag{font-size:.75rem;color:#fbbf24}
"""


def page(prefix, qr, items, fp):
    rows = []
    for a in items:
        img = (f'<img src="{prefix}{html.escape(a["icon"])}" alt="" width="48" height="48">'
               if a["icon"] and os.path.isfile(os.path.join("repo", a["icon"]))
               else '<span class="ph" aria-hidden="true"></span>')
        tag = (f' <span class="tag">Anti-feature: {html.escape(", ".join(a["anti"]))}</span>'
               if a["anti"] else "")
        rows.append(f'<li>{img}<div><strong>{html.escape(a["name"])}</strong>{tag}'
                    f'<p>{html.escape(a["summary"])}</p></div></li>')
    link = f"{REPO_URL}?fingerprint={fp}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{html.escape(DESC)}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{html.escape(DESC)}">
<link rel="icon" href="{prefix}icons/icon.png">
<style>{CSS}</style>
</head>
<body>
<main>
<h1>{TITLE}</h1>
<p>{html.escape(DESC)}</p>
<div class="add">
<a href="https://fdroid.link/#{link}"><img src="{prefix}{qr}" alt="QR code that adds the darkpandawarrior F-Droid repository to the F-Droid app"></a>
<div>
<p>Scan the code on your phone, or open <a href="https://fdroid.link/#{link}">the add link</a>. Or in F-Droid, go to Settings, Repositories, plus, and enter:</p>
<p><code>{REPO_URL}</code></p>
</div>
</div>
<p class="fp">Repository key fingerprint (SHA-256), check it matches on first add:<br><code>{fp}</code></p>
<h2>Apps ({len(items)})</h2>
<ul>
{chr(10).join(rows)}
</ul>
<p class="fp">Apps tagged with an anti-feature bundle non-free components, and F-Droid warns before install. Source for each app is linked from its F-Droid listing.</p>
</main>
</body>
</html>
"""


def main():
    import qrcode
    fp = fingerprint()
    qrcode.make(f"{REPO_URL}?fingerprint={fp}").save("repo/index.png")
    items = apps()
    open("repo/index.html", "w").write(page("", "index.png", items, fp))
    open("index.html", "w").write(page("repo/", "index.png", items, fp))
    print(f"wrote repo/index.html and index.html for {len(items)} apps")


if __name__ == "__main__":
    main()
