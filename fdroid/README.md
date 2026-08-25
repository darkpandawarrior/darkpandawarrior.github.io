# darkpandawarrior F-Droid repository

An F-Droid repository serving apps built from source in GitHub Actions.

## Add it

In the F-Droid client: Settings, Repositories, plus, then enter

```
https://darkpandawarrior.github.io/fdroid/repo
```

Verify the fingerprint on first add:

```
31CFDDD6396E2941CC478909F19D19864CAE281F671E89EDD5AE866B607E1504
```

## What is here

| App | Package | Licence | Notes |
|---|---|---|---|
| Kursi | `com.kursi.android` | GPL-3.0-or-later | Bluffing card game. No proprietary dependencies. |
| Mileway | `com.mileway` | GPL-3.0-or-later | Mileage and expense tracker. Ships Google Play Services components for location and on-device text recognition. |
| PaymentsLab | `com.paymentslab.app` | GPL-3.0-or-later | Payments integration lab. Bundles proprietary payment gateway SDKs by design. |

Apps carrying proprietary dependencies are tagged with the `NonFreeDep`
anti-feature, so the F-Droid client shows the warning before you install.

## How it is built

`.github/workflows/fdroid-publish.yml` downloads the signed release APK from
each app repo's GitHub Release, runs `fdroid update` to build and sign the
index, and deploys the result as a GitHub Pages artifact. APKs are not stored
in git.
