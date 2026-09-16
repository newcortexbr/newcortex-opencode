#!/bin/sh
# Install the pinned RTK prebuilt binary into the local project tools directory.
set -eu

BASE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
VERSION=0.49.0
TOOLS_DIR="$BASE_DIR/.opencode-local/tools/rtk"
TMP_ROOT="$BASE_DIR/.opencode-local/tmp"

if [ "$(uname -s)" != "Linux" ]; then
  printf '%s\n' 'RTK local install blocked: only Linux prebuilt assets are pinned.' >&2
  exit 2
fi

case "$(uname -m)" in
  x86_64)
    ASSET=rtk-x86_64-unknown-linux-musl.tar.gz
    SHA256=7278231dfd7e6a730a4ab7f847b195bcf02289c2d57622b0dab75a6411100c8f
    ;;
  aarch64)
    ASSET=rtk-aarch64-unknown-linux-gnu.tar.gz
    SHA256=c8ea4b6560841e73157c134fd4a3293914c6ede42e786ee985cf491fde691ba7
    ;;
  *)
    printf '%s\n' "RTK local install blocked: unsupported architecture $(uname -m)." >&2
    exit 2
    ;;
esac

command -v curl >/dev/null 2>&1 || {
  printf '%s\n' 'RTK local install blocked: curl is required.' >&2
  exit 2
}
command -v sha256sum >/dev/null 2>&1 || {
  printf '%s\n' 'RTK local install blocked: sha256sum is required.' >&2
  exit 2
}
command -v tar >/dev/null 2>&1 || {
  printf '%s\n' 'RTK local install blocked: tar is required.' >&2
  exit 2
}

mkdir -p "$TMP_ROOT" "$TOOLS_DIR"
tmpdir=$(mktemp -d "$TMP_ROOT/rtk-install.XXXXXX")
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM

url="https://github.com/rtk-ai/rtk/releases/download/v$VERSION/$ASSET"
curl --config /dev/null --fail --location --retry 3 --silent --show-error \
  "$url" -o "$tmpdir/$ASSET"
printf '%s  %s\n' "$SHA256" "$tmpdir/$ASSET" | sha256sum -c -

tar -xzf "$tmpdir/$ASSET" -C "$tmpdir"
if [ ! -x "$tmpdir/rtk" ]; then
  printf '%s\n' 'RTK local install blocked: release archive has no executable rtk.' >&2
  exit 1
fi
install -m 0755 "$tmpdir/rtk" "$TOOLS_DIR/rtk"
"$TOOLS_DIR/rtk" --version
