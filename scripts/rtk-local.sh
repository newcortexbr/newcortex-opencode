#!/bin/sh
# Run an approved RTK command with project-local state and no hooks, telemetry,
# tracking, or recall.
set -eu

BASE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
TOOLS_DIR="$BASE_DIR/.opencode-local/tools/rtk"
RUNTIME_DIR="$BASE_DIR/.opencode-local/tools/rtk-runtime"
BIN="$TOOLS_DIR/rtk"
CONFIG="$RUNTIME_DIR/config/rtk/config.toml"

if [ ! -x "$BIN" ]; then
  printf '%s\n' "RTK is not installed: run $BASE_DIR/scripts/rtk-install.sh" >&2
  exit 127
fi
if [ "$#" -eq 0 ]; then
  printf '%s\n' "usage: $0 <approved-rtk-command> [args...]" >&2
  exit 2
fi

if [ ! -f "$CONFIG" ] || [ ! -r "$CONFIG" ]; then
  printf '%s\n' "RTK policy config missing or unreadable: $CONFIG" >&2
  exit 3
fi
if /usr/bin/grep -Fqx 'enabled = true' "$CONFIG" || \
   ! /usr/bin/grep -Fqx 'enabled = false' "$CONFIG" || \
   ! /usr/bin/grep -Fqx 'mode = "disabled"' "$CONFIG"; then
  printf '%s\n' 'RTK policy config is not explicitly non-persistent.' >&2
  exit 3
fi

if [ "$#" -eq 1 ]; then
  case "$1" in
    --version|--help)
      ;;
    *)
      case "$1" in
        ls|tree|read|smart|git|test|pytest|tsc|diff|log|grep|rg|wc|run)
          ;;
        *)
          printf '%s\n' "RTK command is not approved as the first argument: $1" >&2
          exit 3
          ;;
      esac
      ;;
  esac
else
  case "$1" in
    ls|tree|read|smart|git|test|pytest|tsc|diff|log|grep|rg|wc|run)
      ;;
    *)
      printf '%s\n' "RTK command must be an approved first argument: $1" >&2
      exit 3
      ;;
  esac
fi

mkdir -p "$RUNTIME_DIR/config/rtk" "$RUNTIME_DIR/data" "$RUNTIME_DIR/cache"
exec env -i \
  PATH=/usr/bin:/bin \
  HOME="$RUNTIME_DIR/home" \
  XDG_CONFIG_HOME="$RUNTIME_DIR/config" \
  XDG_DATA_HOME="$RUNTIME_DIR/data" \
  XDG_CACHE_HOME="$RUNTIME_DIR/cache" \
  RTK_RECALL=0 \
  RTK_TEE=0 \
  RTK_TELEMETRY_DISABLED=1 \
  RTK_HOOK_AUDIT=0 \
  "$BIN" "$@"
