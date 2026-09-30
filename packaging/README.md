# Packaging & release (maintainer notes)

`cgpt` ships as a Debian package built with **dh-virtualenv**: all Python
dependencies (including the Anthropic SDK) are bundled into a self-contained
virtualenv at `/opt/venvs/cgpt`, and `/usr/bin/cgpt` is symlinked to it. This is
what lets `apt install cgpt` work even though `anthropic` is not in the Debian
repositories.

A GitHub Actions workflow (`.github/workflows/release.yml`) builds the `.deb`
inside a `kalilinux/kali-rolling` container and publishes a signed **APT
repository to GitHub Pages** on every `v*` tag.

## One-time setup

### 1. Enable GitHub Pages (GitHub Actions source)
Repo **Settings → Pages → Build and deployment → Source = GitHub Actions**.
The repo will be served at `https://etix7.github.io/Cgpt/`.

### 2. Create a signing GPG key (recommended)
On any Linux box:

```bash
gpg --batch --gen-key <<'EOF'
%no-protection
Key-Type: eddsa
Key-Curve: ed25519
Subkey-Type: ecdh
Subkey-Curve: cv25519
Name-Real: Claude_Gpt APT
Name-Email: etienne.bigant@gmail.com
Expire-Date: 0
EOF

# Export the PRIVATE key (this is the CI secret — keep it safe):
gpg --armor --export-secret-keys etienne.bigant@gmail.com > cgpt-apt-private.asc
```

Add it to the repo secrets: **Settings → Secrets and variables → Actions → New
repository secret**:
- `GPG_PRIVATE_KEY` = the full contents of `cgpt-apt-private.asc`
- `GPG_PASSPHRASE` = only if you set a passphrase (the example above uses none)

If you skip this, the repo is still published but **unsigned**; users then need
`[trusted=yes]` in their sources entry (see the root README).

### 3. Cut a release
```bash
git tag v0.1.0
git push origin v0.1.0
```
The workflow builds the `.deb`, regenerates the APT indices, signs them, and
deploys to Pages. Bump the version in `debian/changelog` (and `pyproject.toml`)
for each release.

## Build locally instead

```bash
# On a Kali/Debian host:
./packaging/build-deb.sh
# Or, from anywhere with Docker:
USE_DOCKER=1 ./packaging/build-deb.sh
```

## Layout published to Pages

```
/                     -> https://etix7.github.io/Cgpt/
├── KEY.gpg           (public signing key, armored)
├── pool/main/c/cgpt/cgpt_<ver>_amd64.deb
└── dists/stable/
    ├── Release, Release.gpg, InRelease
    └── main/binary-amd64/Packages(.gz)
```
