# darkpandawarrior.github.io

The GitHub Pages site for my account. It holds three things, and none of them is the portfolio itself.

The portfolio lives at https://siddharth-pandalai.vercel.app. This repo used to be its home, so the root page (`index.html`) and `mileway/index.html` are now redirects that send old links there, and `404.html` points lost visitors there too. Nothing else in the repo is hand-edited.

## What is in here

| Path | What it is | Who writes it |
|---|---|---|
| `fdroid/` | Source for my F-Droid repository: the add-repo instructions, two Python tools, an icon. 44 KB. | Me, by hand |
| `cv/` | Heavy static assets the portfolio links to: the Wasm builds of my apps, screenshots, videos, audio, 3D models and the magazine cover images. 483 MB. | A workflow in [cv-siddharth](https://github.com/darkpandawarrior/cv-siddharth), never by hand |
| `index.html`, `mileway/index.html`, `404.html` | Two redirects and a not-found page with links back to the portfolio and the F-Droid repo | Me |

The `cv/` folder is why the repo is slow to clone. The portfolio keeps these files out of its own repo and its `publish-assets.yml` workflow copies them here on every push to `main`. Those commits are the ones titled `chore(cv): sync heavy assets from ...`. If you want to change something under `cv/`, change it in cv-siddharth or the next sync overwrites it.

## The F-Droid repository

Add this address in the F-Droid client (Settings, Repositories, plus):

```
https://darkpandawarrior.github.io/fdroid/repo
```

The signing fingerprint to check on first add is in [fdroid/README.md](fdroid/README.md). It lives in that one file on purpose, because `make-pages.py` reads it from there to print it on the landing page. A copy here would drift.

The live index currently lists three apps: Doori (`com.mileway`), Gaddi (`com.kursi.android`) and PaymentsLab-KMP (`com.paymentslab.app`). Doori and PaymentsLab-KMP carry the `NonFreeDep` anti-feature because they bundle proprietary SDKs. The reasons are in the table in `fdroid/README.md`.

### How it gets built

`.github/workflows/fdroid-publish.yml` runs on a published release, on an `app-released` dispatch from an app repo, by hand, and every Monday at 04:00 UTC to catch releases that sent no dispatch. It does this, in order:

1. Installs `fdroidserver` from PyPI. The Ubuntu package pins an androguard that cannot parse an APK built with AGP 8 or 9.
2. Downloads the signed APK from each app repo's latest GitHub Release. It asks for the exact asset name, not a glob, because every release also carries unsigned Google-services variants that a prefix match would pick up first.
3. Checks every APK against the pinned signing certificate and fails the run on any mismatch.
4. Runs `fdroid/tools/import-metadata.py` to copy each app's licence and anti-features from its own repo, then `fdroid update`, then `make-pages.py` for the human-readable pages.
5. Assembles the whole site (this repo minus build plumbing, plus the F-Droid output), refuses to continue if a keystore file is in it, and deploys it as a Pages artifact.

APKs are never committed. GitHub rejects blobs over 100 MB and one of the APKs is 115 MB.

The Pages source for this repo has to be set to "GitHub Actions". With "Deploy from a branch" the F-Droid output never goes live.

## Checking it is up

```bash
curl -sI https://darkpandawarrior.github.io/fdroid/repo/index-v2.json | head -1
curl -s  https://darkpandawarrior.github.io/fdroid/repo/index.xml | grep -o '<application id="[^"]*"'
```

I ran both on 2026-11-06. The first returned `200`, the second listed the three package ids above.

## Licence

MIT, see [LICENSE](LICENSE). The apps in the F-Droid repo are GPL-3.0-or-later and say so in their own listings.
