#!/bin/bash
# Compila la ventana nativa (Mac Apple Silicon + Intel en un solo archivo). Solo hace falta en el Mac del dueño.
cd "$(dirname "$0")" || exit 1
swiftc -O -target arm64-apple-macos11 ventana.swift -o /tmp/ic-v-arm -framework Cocoa -framework WebKit || exit 1
swiftc -O -target x86_64-apple-macos11 ventana.swift -o /tmp/ic-v-x64 -framework Cocoa -framework WebKit || exit 1
lipo -create /tmp/ic-v-arm /tmp/ic-v-x64 -output ventana-mac && codesign -s - --force ventana-mac && ls -la ventana-mac
