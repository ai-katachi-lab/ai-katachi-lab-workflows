# MOSS-Image 構図と文字 ワークフロー（枠で配置を決める）

YouTube「AIカタチラボ」の動画で使った、**MOSS-Image** で画像を作る [ComfyUI](https://github.com/Comfy-Org/ComfyUI) ワークフローです。

- 動画：https://youtu.be/6GA2ObAW-cs

画面の上で**枠を描いて「どこに何を置くか」を決め**、枠ごとに「何を描くか」を書けます。人や物の位置や、看板・雑誌の表紙のような**文字（英語・日本語）**の配置を決めたいときに向いています。枠を使わず、文だけで作ることもできます。

> **ライセンスについて**
> MOSS-Image（SFT）・Qwen3.5-9B・flux2-vae は Apache-2.0 で公開されています。使う前に各配布元のページでライセンス本文を確認してください。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルとカスタムノードにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 中身 |
|---|---|
| `MOSS_構図と文字.json` | 枠と文が空のワークフロー。画像の大きさ（横・縦・正方形）を選び、枠を描いて文を書くと1枚作ります |

## 必要なもの

- **ComfyUI**：動画では v0.43.0 で動かしています（MOSS-Image は PyTorch 2.9 以上が必要です）。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **カスタムノード**（ComfyUI/custom_nodes/ に入れます。動画で使った版のコミットも書いておきます）

| ノード | ライセンス |
|---|---|
| [MossImage-BBOX-Prompter](https://github.com/ukr8b3g-cmyk/MossImage-BBOX-Prompter)（v1.0.11、`c7a578b`） | MIT |

ほかのノードは ComfyUI 本体に入っているものです。

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ |
|---|---|---|
| [moss_image_sft_bf16.safetensors](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/530a4c94f92c35ef6818b1b035a983fe9dcf5f54/diffusion_models/moss_image_sft_bf16.safetensors) | `diffusion_models` | 約10.2GB |
| [qwen3.5_9b_bf16.safetensors](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/530a4c94f92c35ef6818b1b035a983fe9dcf5f54/text_encoders/qwen3.5_9b_bf16.safetensors) | `text_encoders` | 約19.3GB |
| [flux2-vae.safetensors](https://huggingface.co/Comfy-Org/MOSS-Image/resolve/530a4c94f92c35ef6818b1b035a983fe9dcf5f54/vae/flux2-vae.safetensors) | `vae` | 約0.34GB |

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. **★画像の大きさ** を選びます（横 3:2＝1728×1152、縦 2:3＝1152×1728、正方形 1:1＝1408×1408）
4. **枠（キャンバス）** に、置きたい場所の枠を描きます
5. **★全体の文と枠ごとの文** の一番上に画像全体の説明を、枠ごとの欄に「その枠に何を描くか」を書きます。文字を描かせたい枠は Type を **text** にします
6. Run を押すと1枚できます

- **★枠を使う** を false にすると、枠の位置は使わず文だけで作ります。
- 設定は、描き直し50回・CFG 3・er_sde／simple・SkipLayerGuidance オンです。
- 細かい使い方は、ワークフローの中の日本語メモを見てください。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で扱っています。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・ノード・モデルの更新への対応はお約束できません。
