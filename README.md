# Vibe 知识大赏 · Agent Skill

让 Claude Code / Codex 帮你把知识做成动画：选题 → 前 5 秒 → 事实核对 → 代码动画 → 渲染 → 成片检查。

来自 Patrick 用 Claude 制作知识动画的工作流。默认约 2 分钟、无旁白、大字加一行字幕、黑金细线与连续运镜，也可按题材使用油画笔触等视觉语言。

## 安装

Claude Code（在你的项目目录运行）：
```bash
git clone https://github.com/AuroraBarista/vibe-knowledge-skill.git .claude/skills/vibe-knowledge
```
Codex（在你的项目目录运行）：
```bash
git clone https://github.com/AuroraBarista/vibe-knowledge-skill.git .agents/skills/vibe-knowledge
```
若目录已存在，请先保留原目录，不要覆盖。重新打开会话后让智能体读取 `SKILL.md`；自动发现以客户端版本为准。

## 怎么用

> 使用 vibe-knowledge，给我 5 个与日常生活有关的反直觉选题。每个都要能用点、线或粒子解释，并提供事实来源。

> 使用 vibe-knowledge，做一期布雷斯悖论。前 2 秒让观众进入堵车现场，前 5 秒出现反转。先给方案和关键帧。

> 按已确认方案直接制作全片。保留无配乐上传版，抽帧检查最后的 MP4，并列出未验证的部分。

## 包含什么

- `SKILL.md`：智能体入口。
- `references/`：选题、开头、视觉、工程、声音、QA 规范。
- `templates/`：方案、事实核对与交付记录模板。
- `scripts/new_episode.py`：独立创建方案和空工程，可复制你自己的工程。
- `scripts/deliver.py`：构建已有工程、HyperFrames 渲染、转码和音轨检查。
- `scripts/frame_sheet.py`：最终视频抽帧拼图。

**这是一套制作工作流，不是一键生成器。** 不包含四期完整动画引擎、成片、字体、商业音乐、账号数据或私人 AI OS。没有现成工程时，智能体需按方案编写动画。

## 依赖与命令

Python 3.10+、Node.js/npm、FFmpeg（包含 ffprobe）。渲染调用 `npx --yes hyperframes@0.8.138`，首次运行会安装该版本及其所需依赖；网络、浏览器运行环境和显卡能力会影响结果。Three.js / GSAP / TypeScript 由具体工程安装并保留其许可证。

```bash
python3 scripts/new_episode.py my-topic --title "我的题目" --output ./episodes
# 可选：复制自己拥有授权的工程
python3 scripts/new_episode.py next-topic --title "下一期" --base-dir /path/to/your/film
# 完成动画工程后
python3 scripts/deliver.py /path/to/film --name "我的题目"
python3 scripts/frame_sheet.py /path/to/final.mp4 -o /path/to/final-sheet.jpg
```

无配乐时只输出上传版；要生成预览版，提供有授权的 `assets/audio/preview-mix.wav` 并加 `--no-score`。工程专用的字体裁剪、配乐合成脚本不在仓库内。

## 公开版整理

去掉私人项目路径、账号表现数据和内部协作依赖。原始四期只保留方法摘要。公开版不保证播放量；每个事实需重新核查，技术检查不等于视觉验收或已发布。

许可暂未指定；公开可阅读，不代表授予任意再分发或商用许可。字体、音乐与第三方库分别遵循其权利人的许可。
