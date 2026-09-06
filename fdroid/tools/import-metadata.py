#!/usr/bin/env python3
"""Pull each app's authored F-Droid metadata into this repo before `fdroid update`.

Without this, `fdroid update --create-metadata` synthesises metadata from the APK
alone: no licence, and no AntiFeatures. An app bundling proprietary SDKs would then
install with no warning shown at all, which is the one thing this repo must not do.

The authored ymls live in each app repo. Only the descriptive fields are copied:
Binaries, Builds and AllowedAPKSigningKeys exist for an fdroiddata submission and
mean nothing to a local repo.
"""
import base64, json, os, shutil, subprocess, sys, tempfile

APPS = [("Gaddi", "com.kursi.android"),
        ("Doori", "com.mileway"),
        ("PaymentsLab-KMP", "com.paymentslab.app")]

KEEP = ("License", "AuthorName", "AuthorEmail", "WebSite", "SourceCode",
        "IssueTracker", "Translation", "Changelog", "Categories",
        "AntiFeatures", "Donate", "Name", "AutoName")

def sh(*a, **kw):
    return subprocess.run(a, check=True, capture_output=True, text=True, **kw).stdout

def main():
    import yaml
    os.makedirs("metadata", exist_ok=True)
    failed = []
    for repo, appid in APPS:
        try:
            raw = sh("gh", "api", f"repos/darkpandawarrior/{repo}/contents/metadata/{appid}.yml",
                     "--jq", ".content")
            src = yaml.safe_load(base64.b64decode(raw)) or {}
        except subprocess.CalledProcessError:
            failed.append(f"{repo}: no metadata/{appid}.yml")
            continue

        out = {k: src[k] for k in KEEP if k in src}
        if "License" not in out:
            failed.append(f"{appid}: no License field")
        with open(f"metadata/{appid}.yml", "w") as f:
            yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)
        print(f"  {appid}: {', '.join(out)}")

        d = os.path.join("metadata", appid, "en-US")
        os.makedirs(d, exist_ok=True)
        tmp = tempfile.mkdtemp()
        try:
            sh("git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse",
               f"https://github.com/darkpandawarrior/{repo}.git", tmp)
            sh("git", "-C", tmp, "sparse-checkout", "set", "fastlane/metadata/android/en-US")
            fl = os.path.join(tmp, "fastlane", "metadata", "android", "en-US")
            for src_name, dst_name in (("short_description.txt", "summary.txt"),
                                       ("full_description.txt", "description.txt"),
                                       ("title.txt", "name.txt")):
                p = os.path.join(fl, src_name)
                if os.path.isfile(p):
                    shutil.copy(p, os.path.join(d, dst_name))
            imgs = os.path.join(fl, "images")
            if os.path.isdir(imgs):
                shutil.copytree(imgs, d, dirs_exist_ok=True)
            chg = os.path.join(fl, "changelogs")
            if os.path.isdir(chg):
                shutil.copytree(chg, os.path.join(d, "changelogs"), dirs_exist_ok=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    if failed:
        print("::error::" + "; ".join(failed))
        sys.exit(1)

if __name__ == "__main__":
    main()
