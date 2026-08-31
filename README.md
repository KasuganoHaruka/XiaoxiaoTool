# XiaoxiaoTool · 医疗项目价格多版本智能查询

离线、移动端优先的医疗服务价格表查询系统。以《成都市医疗服务项目价格汇编（2024版）》为样本，把 PDF 价格表解析成结构化数据，提供关键词/拼音/首字母/别名/模糊检索、多版本横向对比、以及点结果跳到 PDF 原文页并高亮关键数据核验。全程本地、数据不出端。

## 架构（v2 · 混合）

```
桌面数据管线(Python/PyMuPDF)  ──►  标准数据包(data/proto_data.json)  ──►  安卓 APK(WebView)
   解析 1105 页 / 8500 项              项目 + 五级价 + 页码图 + 高亮框         内置数据 · 离线检索 · 跳页核验
```

- **主数据**：桌面解析一次、打包内置（数据公开且静态）。
- **端侧上传解析**：用户上传新 PDF 现场解析，作为后续可选高级路径（M5）。
- 数据/检索逻辑与渲染壳解耦，后续可用 uni-app 同源迁移微信小程序。

详见 [`docs/设计文档-v2.md`](docs/设计文档-v2.md)。

## 目录

| 路径 | 说明 |
| :-- | :-- |
| `docs/` | v2 设计文档 |
| `data/proto_data.json` | 预建标准数据包（项目 / 五级价原文 / 页码图 base64 / 高亮框坐标） |
| `prototype/index.template.html` | 应用逻辑与界面（单文件，数据在构建时注入） |
| `tools/` | 数据管线与构建脚本（extract / build_html / build_app / make_icon） |
| `android/` | 安卓工程（WebView 壳 + 免 Gradle 手工打包脚本） |

生成产物（`prototype/index.html`、`android/assets/index.html`、`android/build/`、APK）已 gitignore，按下方步骤本地生成。

## 构建

```bash
# 依赖：Python(pymupdf/pypinyin/pillow)、JDK17、Android SDK(build-tools 34 + android-34)
python tools/extract.py      # 解析样本 PDF → data/proto_data.json（需 MEDPRICE_PDF 指向源 PDF）
python tools/build_html.py   # → prototype/index.html（浏览器预览，带手机边框+说明栏+APK下载入口）
python tools/build_app.py    # → android/assets/index.html（满屏 app-mode）
python tools/make_icon.py    # 生成启动图标
bash   android/build_apk.sh  # aapt2→javac→d8→zipalign→apksigner → android/build/*.apk
```

## 功能

- **检索（P1）**：关键词 / 拼音全拼 / 首字母 / 别名 / 编辑距离模糊；命中类型标注。
- **多版本（P2）**：结果按版本横向分列五级价（三甲/三乙/二甲/二乙/二乙以下）；价格保留原文（含 `30%`、`不超过420` 等非数字）。
- **原文核验（P3）**：跳到 PDF 对应页码图，自动高亮名称行与五级价，支持缩放/拖动/双指捏合/双击/定位。
- **别名自管**：搜索选项目 → 增/改/删别名，localStorage 持久化，检索即时生效。
- **离线（P4）**：无 INTERNET 权限，零业务网络请求。

## 说明

- 样本 PDF 为公开政府数据，未纳入仓库；`data/proto_data.json` 为其派生的预建数据包。
- 当前内置 2024 版真实数据；多版本对比在导入其它年份价格表后展开。
