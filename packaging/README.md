# Packaging & release (maintainer notes)

`claude-gpt` ships as a **native Debian Python package** built with
`dh-python`/`pybuild`. It is a pure-Python (`Architecture: all`) package whose
runtime dependencies come from the distribution as `python3-*` packages
(`python3-anthropic`, `python3-typer`, `python3-rich`, `python3-prompt-toolkit`),
so nothing is vendored and `apt` resolves everything at install time.

A GitHub Actions workflow (`.github/workflows/release.yml`) builds the `.deb`
on the Ubuntu runner and publishes a signed **APT repository to GitHub Pages**
on every `v*` tag.

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
gpg --armor --export-secret-keys etienne.bigant@gmail.com > claude-gpt-apt-private.asc
```

Add it to the repo secrets: **Settings → Secrets and variables → Actions → New
repository secret**:
- `GPG_PRIVATE_KEY` = the full contents of `claude-gpt-apt-private.asc`
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
# On a Debian / Kali / Ubuntu host:
./packaging/build-deb.sh
# -> ../claude-gpt_0.1.0_all.deb
```

## Layout published to Pages

```
/                     -> https://etix7.github.io/Cgpt/
├── KEY.gpg           (public signing key, armored)
├── pool/main/c/claude-gpt/claude-gpt_<ver>_all.deb
└── dists/stable/
    ├── Release, Release.gpg, InRelease
    └── main/binary-{amd64,arm64}/Packages(.gz)
```
