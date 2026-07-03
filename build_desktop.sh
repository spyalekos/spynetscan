#!/bin/bash
set -euo pipefail

VERSION="$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
ANDROID_APK_BACKUP=""

restore_android_apk() {
    if [ -n "${ANDROID_APK_BACKUP:-}" ] && [ -d "$ANDROID_APK_BACKUP/apk" ]; then
        mkdir -p build
        rm -rf build/apk
        cp -a "$ANDROID_APK_BACKUP/apk" build/apk
        rm -rf "$ANDROID_APK_BACKUP"
    fi
}
trap restore_android_apk EXIT

if [ -d build/apk ]; then
    ANDROID_APK_BACKUP="$(mktemp -d)"
    cp -a build/apk "$ANDROID_APK_BACKUP/apk"
fi

echo "Restoring developer and desktop dependencies..."
uv sync

uv run pyinstaller spynetscan.spec --clean -y --distpath dist/desktop
