# 《{标题}》· Vibe 知识大赏

{日期}。方案、开头设计、结构和事实核对见 `../PLAN.md`。工程底子：{base}。

## 成片

- `exports/{标题}-上传版-无配乐.mp4`：1920×1080，60fps，{秒数} 秒，没有音轨。上传抖音时在编辑页“选择音乐”里加《We Never (Remix)》- Hi Noise。
- `exports/{标题}-预览版-临时配乐.mp4`：同一画面，配原创临时配乐（126 BPM），只用来看节奏。

## 开头

- 0 秒：
- 2 秒：
- 5 秒：

## 画面怎么做的

- 

## 重新生成

```bash
{构建命令，如果有}
python3 scripts/fonts.py
npx --yes hyperframes@0.8.138 lint
python3 <skill>/scripts/deliver.py . --name "{标题}"
```

编辑要改 {源文件}，不要直接改生成出来的 `index.html`。

## QA

`qa/<轮次>/`：每一轮的抽帧；`qa/final-sheet.jpg`：从成片里抽的帧。已修：{问题列表}。未验证：配乐没有试听。
