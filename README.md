# Memo Clock-记忆时钟 App Store Pages

GitHub Pages 发布在 `https://wojiaozyh123-hub.github.io/memoclock-pages/`。App Store Connect 里填的网址：

- 营销网址：`index.html`（英文 `index-en.html`）
- 技术支持网址：`support.html`（英文 `support-en.html`）
- 隐私政策网址：`privacy.html`（英文 `privacy-en.html`）

`jicui-jizai-website/` 是另一个项目，和这些页面无关。

## 改内容

- 隐私政策只改一处：MemoClock 项目里的 `privacy-2.0.0-zh.md` / `privacy-2.0.0-en.md`（App 内 AppLegal.swift 用的是同一份文字），然后重新生成网页：

  ```
  python3 tools/build_privacy.py <privacy-zh.md> <privacy-en.md>
  ```

- 首页由 `tools/build_home.py` 生成（文字、书桌物件、今天页小组件都在脚本里），改完运行 `python3 tools/build_home.py`。卡片和小组件里的公式是 App 自带 KaTeX 预先排好的，存在 `tools/home-formulas.json`。
- 小组件里的插画（猫、沙漏、台灯、咖啡）和收音机是 App 源码里的 SVG 原样拷出来的：`python3 tools/extract_art.py <App 的 MemoryClockApp/UI/HomeBoard/Widgets>` 重新拷到 `tools/widget-art.json`。
- 支持页直接改 `support.html` / `support-en.html`。

## 资源

- `assets/tex/`：纸、牛皮纸、皮面、亚麻纹理，和 App 设计稿同一套。
- `assets/katex/`：KaTeX 样式和字体（MIT，见 `assets/katex/LICENSE`）。
- `assets/fonts/memohand-subset.woff`：霞鹜文楷子集，只含首页手写体用到的字（`tools/hand-chars.txt`，由 build_home.py 写出）（SIL OFL 1.1，见 `assets/fonts/OFL.txt`）。首页手写体文字改了要重新取子集：`pyftsubset MemoHand-Regular.ttf --text-file=tools/hand-chars.txt --flavor=woff --output-file=assets/fonts/memohand-subset.woff`。
