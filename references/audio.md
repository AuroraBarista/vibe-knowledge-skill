# 声音与授权
默认交付无音轨上传版。平台发布时，由用户选择其账号和用途获授权的音乐；平台曲库的存在不代表允许下载或跨平台使用。

原系列偏好《We Never (Remix)》- Hi Noise，本仓库不含音乐，也不声称使用它能提高留存。126 BPM 是工作流的剪辑参考网格，并非对所有 Remix 版本的测速结果。

可选预览配乐：把自行制作或获得授权的 WAV 放到工程 `assets/audio/preview-mix.wav`，使用 `deliver.py --no-score` 混入预览版。上传版仍无音轨。

如果工程自身提供 `scripts/compose-score.py` 和 `scripts/render-score`，交付脚本可运行它们并做两遍 loudnorm（目标 −14 LUFS、−1.5 dBTP）。这两个工程专用脚本不包含在此 skill 中，不要假设它们已安装。原始 Swift 音色渲染器依赖 macOS；自带 WAV 的流程不依赖它。

交付时区分响度测量和实际试听；没有试听就明确说明。
