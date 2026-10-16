---
name: vibe-knowledge
description: Plan, create and review Chinese code-made knowledge animations for 抖音 Vibe 知识大赏. Use for visual paradox explainers, immersive educational animations, hooks, rendering and QA. No voiceover; large typography and one subtitle line.
---
# Vibe 知识大赏

由 Patrick 的 Claude 制作流程整理的公开版：以图形解释机制，用大字和一行字幕讲清楚，约两分钟。默认黑金细线，连续运镜，HyperFrames + Three.js / TypeScript。

## 先读
- 结构与开头：[references/hook-and-structure.md](references/hook-and-structure.md)
- 画风：[references/style.md](references/style.md)
- 工程：[references/pipeline.md](references/pipeline.md)
- 方法案例：[references/episodes.md](references/episodes.md)
- 声音：[references/audio.md](references/audio.md)
- QA：[references/qa-delivery.md](references/qa-delivery.md)

## 工作流程
1. 用户没给题目时，提出 3–8 个有来源、能画出来、对生活有用的反直觉选题。推荐是编辑判断，不是流量预测。
2. 用 `templates/PLAN.md` 写方案，明确 0 / 2 / 5 秒、机制、字幕和事实核对。用户要求直接制作时继续执行，否则先展示方案和关键帧。
3. 用 `python3 <skill>/scripts/new_episode.py <slug> --title "标题" --output ./episodes` 建立目录。默认只有方案与空工程；可加 `--base-dir /path/to/your/film` 复制自己的引擎。本仓库不包含四期原始工程。
4. 按 pipeline.md 编写确定性的时间线与画面，所有数字从数据计算。按当前环境提供的 HyperFrames 指南确认接口。
5. 抽帧检查开头、全文可读性、转场和事实。来源留在方案中；不能为了视觉简洁删除影响理解的必要条件。
6. 工程完成后运行 `python3 <skill>/scripts/deliver.py <film> --name "标题"`。需要 Python 3、Node.js/npm、FFmpeg/ffprobe；CLI 固定为 HyperFrames 0.8.138。渲染时间依硬件与工程而定。
7. 用 `python3 <skill>/scripts/frame_sheet.py <成片.mp4> -o <film>/qa/final-sheet.jpg` 检查最终编码输出。汇报已验证内容、未试听或未播放内容和具体缺陷。

## 约束
- 画面以大字和一行底部字幕为主，不显示本机路径、外部链接或二维码。
- 数字、日期、引语逐条核查，不将示例当事实依据。
- 上传版无音轨；预览配乐可选，详见 audio.md。不附带商业音乐、字体或第三方工程。
- 遵循当前用户授权和工作区规则；发布、付费、对外发送需要对应授权。
- 保留旧成片，不覆盖用户材料。项目索引和反馈存放在用户指定的位置。
