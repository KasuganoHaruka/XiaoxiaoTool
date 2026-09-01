#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
SDK=/opt/android-sdk
BT=$SDK/build-tools/34.0.0
ANDROID_JAR=$SDK/platforms/android-34/android.jar
JAVA=$JAVA_HOME/bin
PROJ=/root/projects/pdftool/.claude/worktrees/xiaoxiao/android
OUT=$PROJ/build
APP=医疗价格查询

rm -rf "$OUT"
mkdir -p "$OUT/compiled" "$OUT/gen" "$OUT/obj" "$OUT/dex"

echo "== [1/7] aapt2 compile resources =="
"$BT/aapt2" compile --dir "$PROJ/res" -o "$OUT/compiled/res.zip"

echo "== [2/7] aapt2 link (assets + manifest) =="
"$BT/aapt2" link \
  -o "$OUT/base.apk" \
  -I "$ANDROID_JAR" \
  --manifest "$PROJ/AndroidManifest.xml" \
  -A "$PROJ/assets" \
  --java "$OUT/gen" \
  --min-sdk-version 21 --target-sdk-version 34 \
  --version-code 3 --version-name 0.3.0 \
  "$OUT/compiled/res.zip"

echo "== [3/7] javac (MainActivity + R.java) =="
RJAVA=$(find "$OUT/gen" -name R.java)
"$JAVA/javac" \
  -classpath "$ANDROID_JAR" \
  -d "$OUT/obj" \
  "$PROJ/src/com/sora/medprice/MainActivity.java" $RJAVA

echo "== [4/7] d8 (dex) =="
CLASSES=$(find "$OUT/obj" -name '*.class')
"$BT/d8" --min-api 21 --output "$OUT/dex" --lib "$ANDROID_JAR" $CLASSES

echo "== [5/7] add classes.dex into apk =="
cp "$OUT/base.apk" "$OUT/unsigned.apk"
( cd "$OUT/dex" && "$JAVA/jar" uf "$OUT/unsigned.apk" classes.dex )

echo "== [6/7] zipalign =="
"$BT/zipalign" -f -p 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"

echo "== [7/7] sign (debug keystore) =="
# 固定密钥放在工程根（不随 rm -rf build 删除），保证版本间签名一致 => 可覆盖更新安装
KS=$PROJ/debug.keystore
if [ ! -f "$KS" ]; then
  "$JAVA/keytool" -genkeypair -v -keystore "$KS" -alias androiddebugkey \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass android -keypass android \
    -dname "CN=Med Price Debug, O=sora, C=CN" >/dev/null 2>&1
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android --key-pass pass:android \
  --out "$OUT/医疗价格查询-0.3.0.apk" "$OUT/aligned.apk"

"$BT/apksigner" verify --print-certs "$OUT/医疗价格查询-0.3.0.apk" | head -3

echo "== DONE =="
ls -la "$OUT/医疗价格查询-0.3.0.apk"
