#!/usr/bin/env bash
# Build the claude-gpt .deb locally on a Debian/Kali host.
#
# Usage:
#   ./packaging/build-deb.sh            # build natively (must be on Kali/Debian)
#   USE_DOCKER=1 ./packaging/build-deb.sh   # build inside a kali-rolling container
#
# The resulting package lands in ../  (one level above the source tree), e.g.
#   ../claude-gpt_0.1.0_amd64.deb
# Install it with:  sudo apt install ../claude-gpt_0.1.0_amd64.deb
set -euo pipefail

cd "$(dirname "$0")/.."
SRC="$(pwd)"

build_native() {
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends \
    debhelper dh-virtualenv python3 python3-dev python3-venv python3-pip \
    build-essential dpkg-dev libffi-dev ca-certificates
  dpkg-buildpackage -us -uc -b
  echo "Built packages:"
  ls -1 ../claude-gpt_*.deb
}

build_docker() {
  mkdir -p dist
  docker run --rm -v "$SRC":/w -w /w kalilinux/kali-rolling bash -c '
    set -eux
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y --no-install-recommends \
      debhelper dh-virtualenv python3 python3-dev python3-venv python3-pip \
      build-essential dpkg-dev libffi-dev ca-certificates
    dpkg-buildpackage -us -uc -b
    cp ../claude-gpt_*.deb /w/dist/
  '
  echo "Built packages:"
  ls -1 dist/claude-gpt_*.deb
}

if [ "${USE_DOCKER:-0}" = "1" ]; then
  build_docker
else
  build_native
fi
