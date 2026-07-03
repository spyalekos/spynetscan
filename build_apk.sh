#!/bin/bash
set -euo pipefail

APP_NAME="SpyNetScan"
PROJECT_NAME="spynetscan"
APK_OUTPUT="build/apk/${APP_NAME}.apk"
ANDROID_STAGE="/tmp/notespy_android_stage"

VERSION="$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
BUILD_NUMBER="$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["tool"]["flet"].get("build_number", 1))')"

echo "Cleaning previous Android build output (keeping stage caches)..."
rm -rf build/flutter build/apk build/.hash app_bundle src/build
mkdir -p build/apk

if [ -d "$ANDROID_STAGE" ]; then
    # Delete only top-level python files to force copying new source, but keep build/
    find "$ANDROID_STAGE" -maxdepth 1 -type f -delete
else
    mkdir -p "$ANDROID_STAGE"
fi

echo "Syncing Android base dependencies..."
uv sync --no-dev

echo "Preparing minimal Android source bundle..."
mkdir -p "$ANDROID_STAGE"
for FILE in \
    main.py \
    scanner.py \
    pyproject.toml \
    uv.lock \
    README.md; do
    if [ -f "$FILE" ]; then
        cp -p "$FILE" "$ANDROID_STAGE/"
    fi
done

echo "Caching python build interpreter from local cache to avoid serious_python download timeout..."
mkdir -p "$ANDROID_STAGE/build/flutter/build"
PYTHON_BUILD_CACHE_DIR="${PYTHON_BUILD_CACHE_DIR:-$(pwd)/.android_cache}"
if [ -d "$PYTHON_BUILD_CACHE_DIR/build_python_3.12.9" ]; then
    cp -rp "$PYTHON_BUILD_CACHE_DIR/build_python_3.12.9" "$ANDROID_STAGE/build/flutter/build/"
    echo "Successfully cached build_python_3.12.9 to stage."
else
    echo "WARNING: Python build cache directory not found."
fi


if [ -d assets ]; then
    mkdir -p "$ANDROID_STAGE/assets"
    cp -rp assets/* "$ANDROID_STAGE/assets/"
fi

export _JAVA_OPTIONS="-Xmx1536m -Xms512m -XX:MaxMetaspaceSize=512m"
export GRADLE_OPTS="-Xmx1536m -XX:MaxMetaspaceSize=512m -Dorg.gradle.daemon=false -Dorg.gradle.parallel=false -Dorg.gradle.workers.max=1 -Dorg.gradle.vfs.watch=false -Dkotlin.incremental=false"
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
export SERIOUS_PYTHON_SITE_PACKAGES="$(pwd)/build/site-packages"
FLUTTER_SDK_PATH="${FLUTTER_SDK_PATH:-$HOME/flutter/3.41.4}"
export PATH="$FLUTTER_SDK_PATH/bin:$PATH"

echo "Building Android APK for ${APP_NAME} ${VERSION} (${BUILD_NUMBER})..."
set +e
uv run flet build apk "$ANDROID_STAGE" \
    --project "$PROJECT_NAME" \
    --artifact "$APP_NAME" \
    --product "$APP_NAME" \
    --description "Local network IP and Port scanner" \
    --org "com.spyalekos" \
    --bundle-id "com.spyalekos.spynetscan" \
    --company "spyalekos" \
    --copyright "Copyright (C) 2026 by Spyalekos" \
    --arch arm64-v8a \
    --split-per-abi \
    --cleanup-app \
    --cleanup-app-files "__pycache__" "*.pyc" "*.pyo" ".pytest_cache" ".mypy_cache" \
    --cleanup-packages \
    --cleanup-package-files "__pycache__" "*.pyc" "*.pyo" "*.pyi" "py.typed" "tests" "test" "docs" "*.exe" \
    --build-version "$VERSION" \
    --build-number "$BUILD_NUMBER" \
    --android-adaptive-icon-background "#0A140E" \
    --android-permissions "android.permission.INTERNET=true" "android.permission.ACCESS_NETWORK_STATE=true" "android.permission.ACCESS_WIFI_STATE=true" \
    --flutter-build-args=--target-platform=android-arm64 \
    --yes
FLET_STATUS=$?
set -e

SOURCE_APK=""
for CANDIDATE in \
    "$ANDROID_STAGE/build/apk/${APP_NAME}-arm64-v8a-release.apk" \
    "$ANDROID_STAGE/build/apk/app-arm64-v8a-release.apk" \
    "$ANDROID_STAGE/build/apk/${APP_NAME}.apk" \
    "$ANDROID_STAGE/build/apk/app-release.apk" \
    "build/flutter/android/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk" \
    "build/flutter/android/build/app/outputs/flutter-apk/app-release.apk" \
    "build/flutter/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk" \
    "build/flutter/build/app/outputs/flutter-apk/app-release.apk" \
    "build/apk/${APP_NAME}.apk" \
    "build/apk/app-release.apk" \
    "$(find "$ANDROID_STAGE" -path '*outputs/flutter-apk/*arm64*.apk' -print -quit)" \
    "$(find "$ANDROID_STAGE" -path '*build/apk/*arm64*.apk' -print -quit)" \
    "$(find build -path '*outputs/flutter-apk/*arm64*.apk' -print -quit)" \
    "$(find build -path '*outputs/flutter-apk/*.apk' -print -quit)" \
    "$(find "$ANDROID_STAGE" -name '*.apk' -print -quit)" \
    "$(find build/apk -name '*.apk' -print -quit)"; do
    if [ -n "$CANDIDATE" ] && [ -f "$CANDIDATE" ]; then
        SOURCE_APK="$CANDIDATE"
        break
    fi
done

if [ -z "$SOURCE_APK" ]; then
    echo "ERROR: APK artifact was not found under build/. Flet exit code: $FLET_STATUS" >&2
    exit "$FLET_STATUS"
fi


if [ "$FLET_STATUS" -ne 0 ]; then
    echo "WARNING: flet build exited with $FLET_STATUS after Gradle output; using discovered APK: $SOURCE_APK" >&2
fi

if [ "$SOURCE_APK" != "$APK_OUTPUT" ]; then
    cp "$SOURCE_APK" "$APK_OUTPUT"
fi
ls -lh "$APK_OUTPUT"
echo "APK ready: $APK_OUTPUT"
