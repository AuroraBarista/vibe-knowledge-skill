# 工程：HyperFrames + three.js / TypeScript

CLI 固定版本：`npx --yes hyperframes@0.8.138 <lint|snapshot|render>`。每个工程文件夹里有 `CLAUDE.md` / `AGENTS.md`，写的是 HyperFrames 的通用规则。

## 选哪一期当底子

| base | 引擎 | 适合 | 主要编辑的文件 |
|---|---|---|---|
| `simpson` | 2D HTML / SVG + GSAP，点阵、卡片、水位 | 比例、分组、统计反转 | `index.html` |
| `braess` | three.js 线框场景 + 粒子流 + bokeh + bloom，HTML 标签跟着 3D 走 | 流动、交通、系统、城市 | `index.html` |
| `friendship` | three.js 三维网络，布局用 `scripts/net.mjs` 离线算好 | 网络、传播、社交关系 | `scripts/template.html.txt` → `node scripts/net.mjs` 生成 index.html |
| `vangogh` | TypeScript + three.js 世界，GPU 笔触（point sprite），一镜到底飞行 | 一个人的一生、地理之旅、画作世界 | `src/*.ts`、`scripts/template.html` → `node scripts/build.mjs` 生成 index.html |

公开版 `new_episode.py` 默认只创建方案和工程空目录。上述四种引擎不随仓库提供。可用 `--base-dir` 复制自己的已有工程；必须自行核查代码、字体、素材的授权，并替换旧内容。

## 时间线（每一期都一样）

- 根节点：`<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="<秒>">`。
- 一条暂停的 GSAP 时间线，注册为 `window.__timelines["main"] = tl`。这句必须直接写在 `index.html` 里，lint 是静态检查的。TypeScript 的 bundle 要内联进 index.html（`/*BUNDLE*/` 占位），不能用外部 js 文件。
- 画面只由时间 t 决定：`renderAt(t)` 读 t，设置相机、uniform 后渲染。用 `tl.eventCallback("onUpdate", () => go(tl.time()))` 和 `window.addEventListener("hf-seek", ...)` 驱动，`go()` 里用 `lastT` 去重。
- 只能写确定性的逻辑：用带种子的随机数（mulberry32），不要 `Math.random()`、`Date.now()`，不要联网请求。
- 结尾加 `tl.to({}, { duration: 0.01 }, DUR - 0.01)`，让时间线长度等于片长。
- 文字是叠在 canvas 上的 HTML，用 `data-s` / `data-e` 标记出现和消失的时间，用一个通用的 `show()` 做淡入（opacity + y + blur）和淡出。跟着 3D 物体走的标签，每帧把三维坐标投影到屏幕。

## three.js 要点

- three r169 放在 `assets/vendor/`（含 `jsm/postprocessing`、`jsm/lines`），用 importmap 引入。
- 渲染器：`preserveDrawingBuffer: true`、pixelRatio 1、1920×1080。后期链：RenderPass → UnrealBloomPass → OutputPass → 自定义调色 pass（暗角、颗粒、可选径向模糊）。
- 颜色：调色板用 sRGB 值写，在 shader 里 `pow(c, 2.2)` 转成线性，OutputPass 再转回 sRGB。
- 不要在页面里做重计算：O(N²) 的力导布局之类的，lint 和 snapshot 会重跑页面脚本，内存会溢出。在 Node 里离线算好再注入（参考 friendship 的 `net.mjs`）。线性的生成没问题，梵高那期在页面里生成了 200 万笔。
- 更新几何体时原地改 attribute（比如 `setLine`），不要每帧新建。

## 笔触世界（vangogh 底子）

- 每一笔是一个 GPU point sprite：按三维切线在屏幕上的投影旋转，画成带刷毛和侧光的短笔触。尺寸 = max(长度像素, 宽度像素)，限制在 1.5–120px。
- 笔触类型 `kind`：0 静止、1 随风摆、2 天空（颜色来自调色板 uniform）、3 发光、4 乌鸦（移动）、5/6 隧道（由 `uTun` 控制显隐）。
- 天空球跟着相机走，换时代只换调色板（`pal(t, 时长, {top, low, light, swirl, star, sun, glow, fogN, fogF})`）。
- 镜头：关键帧 `[t, 位置, 目标, ease]`，用 GSAP 补间一个 cam 对象。`roll` 在 `lookAt` 之后用 `rotateZ` 加，fov 单独补间。
- 已知坑：
  - 相机离笔触只有几个单位时，笔触会变成大方块。远离一点，或者给近景物体用更细、更密的笔触（`house(..., { fine, density })`）。
  - 室内、街道要去掉地面笔触，否则会从地板里戳出来。
  - 从高处平视时会看到世界的边缘：用雾遮，或者让镜头朝上、朝下看。

## 整体挪时间

开头变短或变长时，要把开头之后所有的时间一起平移：镜头关键帧、调色、`data-s` / `data-e`、闪光，还有配乐（`compose-score.py` 里用 `OFF`）。用脚本统一减，不要手改。v2 梵高就是把 ≥11.9 秒的时间全部减了 3.6 秒。

## 命令

```bash
npx --yes hyperframes@0.8.138 lint            # 0 error 才能渲染；文件过大的 warning 可以忽略
npx --yes hyperframes@0.8.138 snapshot --at 0.5,2,5,10 --no-end --describe false --timeout 30000 -o qa/<轮次> .
npx --yes hyperframes@0.8.138 render --fps 60 --workers 4 --quality delivery --output exports/_raw.mp4
```

渲染很慢（约 108 秒的片、200 万笔，要 13 分钟以上），一定在后台跑，不要让父 shell 退出导致渲染中断。平时直接用 `deliver.py`。

## 其他坑

- 绝对定位的文字放在宽度为 0 的容器里会竖着换行，加 `white-space: nowrap`。
- 补间 CSS `filter` 时，先 `set` 好起始值，比如 `brightness(1)`，否则会从 0 开始。
- zsh 里 `$VAR:l` 会被当成修饰符；带 `*` 的参数要加引号（`'--external:three/addons/*'`）。
- 路径里有空格：Node 脚本用 `fileURLToPath`，不要把 `%20` 编码的路径当 cwd。
- 判断渲染是否完成，要等输出文件和进程退出，不要 grep 进度文字（“complete” 会匹配到 “framesCompleted”）。
- 下载的数据（例如 Wikimedia 的图）要带 User-Agent，遇到 429 要退避重试；不可信的文件放在单独的空文件夹里处理。
- 成片很大是正常的：笔触密、有颗粒，CRF 20 时 2 分钟约 0.5 GB，抖音可以接受。
