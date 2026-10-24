# H3 動画の仕上げ ワークフロー（顔を直す・全体を高解像度に）

YouTube「AIカタチラボ」の動画で使った、**MiniMax H3** で作った動画をあとから仕上げるための [ComfyUI](https://github.com/comfyanonymous/ComfyUI) ワークフローです。

- 動画：https://youtu.be/mVo6Vim0Gpg

1. **顔を直す**：動画の中の顔を毎フレーム追いかけて切り出し、H3 で大きく描き直してから元の位置に戻します。本人の顔画像（Ref 1）を渡すので、人物がそろったまま直ります。口の動きと音声は元の動画のままです。
2. **全体を高解像度に**：動画全体を約2倍（初期値は約1080p）にし、元の動画を手本にして1回だけ軽く描き直します。

おすすめの順番は「顔を直す」→「全体を高解像度に」です。どちらか片方だけでも使えます。

> **ライセンスについて（必ずお読みください）**
> 10Eros Max と MiniMax H3 は **[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)** にしたがって配布されています。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文と各配布元のページを確認してください。人の見分けに使う InsightFace の buffalo_l は、非商用の研究用途とされています。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルとカスタムノードにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 使うとき |
|---|---|
| `01_顔を直す_実写.json` | 実写の動画。一番大きく写っている顔を自動で直す |
| `03_顔を直す_アニメ.json` | アニメ調の動画。顔の見つけ方をアニメ用の検出器に、人の見分け方を画風を問わない方式（clip_vision）に替えてあります |
| `05_全体を高解像度に.json` | 顔を直した動画（または元の動画）全体を高解像度にする |

- 1回の実行で直せるのは **1人** です。2人目を直すときは、1人目を直した動画を入力にしてもう一度実行します。
- 番号は動画の中の番号に合わせています（02・04 は動画で扱っていないため入っていません）。

FaceRefine と Upsampler の作者が配っているサンプル（版固定）を元に、次のように変えています。

- 本体を 10Eros Max TURBO-hybrid beta5 に。Turbo が入っているので、作者のサンプルの Turbo LoRA は外しました（10Eros との組み合わせは作者は試していません）
- 2枚目の参照画像・GGUF・SAM マスク（どれも初期状態で止まっていたもの）を外しました
- 01・03：動画を一覧から選べる読み込みノード（Load Video (Upload)）に替えました
- 03：アニメ用の顔検出器と clip_vision の人の見分けを追加
- 使い方の日本語メモを追加（作者の英語のメモも、合わなくなった2つ以外は残しています）

## 必要なもの

- **ComfyUI**：v0.38.2 以降（Upsampler が v0.35 以上を必要とします）。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **カスタムノード**（ComfyUI/custom_nodes/ に入れます。動画で使った版のコミットも書いておきます）

| ノード | 使うワークフロー | ライセンス |
|---|---|---|
| [ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine)（`d8521d1`） | 01・03 | MIT |
| [ComfyUI-H3-Video-Upsampler](https://github.com/dntpi/ComfyUI-H3-Video-Upsampler)（`36cb612`） | 05 | MIT |
| [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)（`4d907be`） | 01・03 | GPL-3.0 |
| ComfyUI-H3-NativeAudioLock（[MiniMax-H3-NativeAudio-MusicVideo-Workflow](https://github.com/Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow) の中の `custom_nodes/ComfyUI-H3-NativeAudioLock` フォルダ。`11a95f6`） | 01・03 | リポジトリに記載なし（配布元を確認してください） |

- FaceRefine は ultralytics・insightface などの Python パッケージを使います。各ノードの説明どおりに入れてください。
- 顔検出器の名前（`bbox/face_yolov8m.pt` など）は `models/ultralytics` フォルダを ComfyUI に登録して使います。ComfyUI-Impact-Pack（Subpack）を入れるか、ComfyUI のフォルダにある `extra_model_paths.yaml` に次を足してください（`base_path` は自分の ComfyUI の models フォルダ）。

```yaml
h3_finish:
  base_path: /path/to/ComfyUI/models
  ultralytics: ultralytics
```

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。**置き場所の名前が配布元と違うものは、その名前に変えて置いてください。**

| ファイル | 置き場所（ComfyUI/models/ の中）と名前 | 大きさ | 使うワークフロー |
|---|---|---|---|
| [10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors](https://huggingface.co/TenStrip/10Eros-Max/resolve/8a198588c8870ab0d613b3492a3150d091c8c2dd/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors) | `diffusion_models` | 約21GB | 01・03 |
| [minimax_h3_ref2va_pruned_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors) | `diffusion_models` | 約21GB | 05 |
| [qwen3vl_32b_minimax_h3_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors) | `text_encoders` | 約27.1GB | すべて |
| [minimax_h3_video_vae_fp16.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_video_vae_fp16.safetensors) | `vae` | 約5.2GB | すべて |
| [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_audio_vae_fp32.safetensors) | `vae` | 約0.6GB | すべて |
| [minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/3f941d5d182014dd5c0a5e16330420ee2d4aa0c6/minimax_h3_latent_upscaler_3d_conv_v1/minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors) | `latent_upscale_models/minimax_h3_latent_upscaler_3d_bf16.safetensors`（名前を変える） | 約0.69GB | 05 |
| [h3upscale_v2_x2.safetensors](https://huggingface.co/sandpies/ComfyUI-H3-Video-Upsampler/resolve/9337fe00d0753d249aba6181b81d3b6a62bccb52/lora/h3upscale_v2_x2.safetensors) | `loras` | 約0.62GB | 05 |
| [face_yolov8m.pt](https://huggingface.co/Bingsu/adetailer/resolve/53cc19de382014514d9d4038601d261a7faa9b7b/face_yolov8m.pt) | `ultralytics/bbox` | 約52MB | 01 |
| [person_yolov8m-seg.pt](https://huggingface.co/Bingsu/adetailer/resolve/53cc19de382014514d9d4038601d261a7faa9b7b/person_yolov8m-seg.pt) | `ultralytics/segm` | 約55MB | 01 |
| [model.pt（アニメ顔検出 v1.4_s）](https://huggingface.co/deepghs/anime_face_detection/resolve/784dc4c0bb692351ddcdbe6131a050b17d3025d5/face_detect_v1.4_s/model.pt) | `ultralytics/bbox/anime_face_detect_v1.4_s.pt`（名前を変える） | 約22MB | 03 |
| [sigclip_vision_patch14_384.safetensors](https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/5421dab31229df19801c8e3af446b5a8bc71a3bc/sigclip_vision_patch14_384.safetensors) | `clip_vision` | 約0.86GB | 03 |

- InsightFace の buffalo_l（実写の人の見分け用）は、FaceRefine が初回に自動で取ります。
- 05 は、Upsampler の LoRA が素の H3 で学習されているため、素の H3（ref2va pruned int8）を使います。顔を直すのと同じ 10Eros に替えても動く見込みですが、試していません。

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. **顔を直す（01・03）**：Ref 1 に本人の顔の画像を選び、プロンプトにその動画を作ったときのプロンプトを貼り、Load Video (Upload) で動画を選んで Run。Ref 1 は最初 `example.png` という名前が入っていて、そのままだとエラーになります
4. **全体を高解像度に（05）**：顔を直した動画（`output/FaceRefine/` の `…-audio.mp4`）を ComfyUI の `input/` に入れ、Load Video で選んで Run

- できた動画は ComfyUI の `output/FaceRefine/`（顔を直す）、`output/Upsampled/`（全体を高解像度に）に入ります。
- 直りが弱い・強すぎるときは BasicScheduler の denoise（初期値 0.4）を少しずつ変えます。上げすぎると頭と体がずれます。
- 細かい調整は、ワークフローの中の日本語メモと作者の英語メモを見てください。

## 元にしたもの

- [ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine)（MIT License、Copyright (c) 2026 Carasibana）の `example_workflows/H3_Face_Refine_Auto_Select.json`
- [ComfyUI-H3-Video-Upsampler](https://github.com/dntpi/ComfyUI-H3-Video-Upsampler)（MIT License、Copyright (c) 2026 Sandpies）の `example_workflows/H3_Video_Upsampler.json`

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で扱っています。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・ノード・モデルの更新への対応はお約束できません。
