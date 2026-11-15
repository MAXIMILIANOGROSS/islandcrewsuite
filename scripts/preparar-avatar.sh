#!/bin/bash
# Descarga (una sola vez) lo necesario para el Avatar de la cabra. Gratis. Sin pagar nada.
set -e
cd "$(dirname "$0")"; V=vendor-avatar; mkdir -p $V/wasm $V/modelos; T=$(mktemp -d)
B=https://storage.googleapis.com/mediapipe-models
[ -s $V/modelos/face_landmarker.task ] || curl -fsSL -o $V/modelos/face_landmarker.task $B/face_landmarker/face_landmarker/float16/1/face_landmarker.task
[ -s $V/modelos/pose_landmarker_lite.task ] || curl -fsSL -o $V/modelos/pose_landmarker_lite.task $B/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task
[ -s $V/modelos/hand_landmarker.task ] || curl -fsSL -o $V/modelos/hand_landmarker.task $B/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
if [ ! -s $V/vision_bundle.mjs ]; then (cd $T && npm pack @mediapipe/tasks-vision@0.10.14 >/dev/null && tar xzf *.tgz && cp package/vision_bundle.mjs "$OLDPWD/$V/" 2>/dev/null || true; cp package/wasm/* "$OLDPWD/$V/wasm/" 2>/dev/null || true); fi
[ -s $V/three.module.min.js ] || cp ../node_modules/three/build/three.module.min.js $V/
ls -la $V $V/modelos $V/wasm
