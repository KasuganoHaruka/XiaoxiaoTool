# 医疗价格查询 · 安卓 APK（M1）

WebView 壳 App：加载 `assets/index.html`（自包含 Web 应用——内置样本数据、离线检索、原文高亮跳页核验、别名 localStorage 持久化）。**无 INTERNET 权限，数据不出端。**

- 包名 `com.sora.medprice`，minSdk 21 / targetSdk 34，versionName 0.1.0
- 产物：`build/医疗价格查询-0.1.0.apk`

## 构建前置
- JDK 17（`/usr/lib/jvm/java-17-openjdk-amd64`）
- Android SDK：`/opt/android-sdk`（build-tools 34.0.0 + platforms;android-34）
- Python venv（PyMuPDF/pypinyin/Pillow）用于生成数据与图标

## 从零构建
```bash
# 1) 解析样本 PDF → /tmp/proto_data.json（含项目/页码图/高亮框）
python tools/extract.py
# 2) 生成 app 版页面 → android/assets/index.html（满屏 app-mode）
python tools/build_app.py
# 3) 生成图标（首次）
python tools/make_icon.py      # 若已存在 res/mipmap-* 可跳过
# 4) 手工打包 APK（aapt2 → javac → d8 → zipalign → apksigner）
bash android/build_apk.sh
```

## 说明
- 采用 v2「混合架构」：当前内置桌面预建数据（主路径）；用户上传新 PDF 端侧解析为后续 M5。
- 数据/检索逻辑与渲染壳解耦，后续可用 uni-app 同源迁移微信小程序（复用 `assets/index.html` 内的应用逻辑）。
