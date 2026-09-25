#!/bin/sh
# Refresh the vendored copy of netprint (https://github.com/alex-mextner/netprint), the
# device-classification rules + engine, in router_cli/_vendor/netprint.
#
#   scripts/vendor-netprint.sh ../netprint        # a local checkout (at the commit you want)
#
# The OUI table is NOT vendored: router-cli ships (and updates) its own and passes the vendor
# in. Commit the result together with the new VERSION file.
set -eu
src="${1:?usage: scripts/vendor-netprint.sh <path to a netprint checkout>}"
here="$(cd "$(dirname "$0")/.." && pwd)"
dst="$here/router_cli/_vendor/netprint"
rm -rf "$dst"
mkdir -p "$dst/data/rules"
cp "$src"/netprint/*.py "$dst"/
cp "$src"/netprint/data/categories.json "$dst/data/"
cp "$src"/netprint/data/rules/*.json "$dst/data/rules/"
cp "$src"/LICENSE "$dst/LICENSE"
rev="$(git -C "$src" rev-parse HEAD 2>/dev/null || echo unknown)"
ver="$(sed -n "s/^__version__ = \"\(.*\)\"/\1/p" "$src/netprint/__init__.py")"
printf "netprint %s (%s)\nhttps://github.com/alex-mextner/netprint\n" "$ver" "$rev" > "$dst/VERSION"
echo "vendored netprint $ver ($rev) into $dst"
