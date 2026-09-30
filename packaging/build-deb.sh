#!/usr/bin/env bash
# Build the claude-gpt .deb locally on a Debian/Kali/Ubuntu host.
#
# Usage:  ./packaging/build-deb.sh
#
# It's a native, pure-Python package: runtime deps come from python3-* packages
# at install time, so the build just needs debhelper + dh-python + pybuild.
# The resulting package lands one level above the source tree, e.g.
#   ../claude-gpt_0.1.0_all.deb
# Install it with:  sudo apt install ../claude-gpt_0.1.0_all.deb
set -euo pipefail

cd "$(dirname "$0")/.."

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  debhelper dh-python python3-all pybuild-plugin-pyproject \
  python3-hatchling dpkg-dev build-essential

dpkg-buildpackage -us -uc -b

echo "Built package(s):"
ls -1 ../claude-gpt_*.deb
