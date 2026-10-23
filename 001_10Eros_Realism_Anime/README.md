# MiniMax H3 × 10Eros ワークフロー（実写版・アニメ版）

YouTube「AIカタチラボ」の動画で使った、動画生成モデル **MiniMax H3** の派生モデル **10Eros Max** 用の [ComfyUI](https://github.com/comfyanonymous/ComfyUI) ワークフローです。画像（または文章だけ）から、音声つきの動画を作ります。実写向けとアニメ向けの2本があります。

- 動画：https://youtu.be/Qqm-3XHxuH4

> **ライセンスについて（必ずお読みください）**
> 10Eros Max と2つの LoRA は、どれも **[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)** にしたがって配布されています。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文と各配布元のページを確認してください。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 中身 |
|---|---|
| `10Eros_実写_RealismPeople.json` | 実写向け。10Eros Max に Realism People LoRA（強さ 0.7）を組み合わせたもの |
| `10Eros_アニメ_AnimaBooster.json` | アニメ向け。10Eros Max に Anima H3 Booster LoRA（強さ 0.8）を組み合わせたもの |

どちらも ComfyUI 公式の MiniMax H3 画像→動画テンプレートを元に、次のように変えています。

- 本体を 10Eros Max に、LoRA を実写用・アニメ用に差し替え
- 高速化の Turbo LoRA は使わず、20ステップで画質を優先
- 初期値を 1344×768・5秒・24fps に
- 使い方の日本語メモを追加

## 3つの使い方

| モード | つなぎ方 | できること |
|---|---|---|
| I2V（初期設定） | 左の Load Image を自分の画像に替える | その画像から動き出す動画 |
| T2V | `first_frame` の線を外す | 文章だけから作る動画 |
| 先頭＋末尾 | `last_frame` に Load Image をもう1つつなぐ | 最初と最後のコマの間をつなぐ動画 |

## 必要なもの

- **ComfyUI**：MiniMax H3 に対応した新しいもの。古い場合はノードが赤く表示されるので、ComfyUI を更新してください。
- **カスタムノード**：不要です（ComfyUI 標準のノードだけで動きます）。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **モデル**：下の表のファイル。このリポジトリには入っていないので、配布元から取得してください。

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ | 使うワークフロー |
|---|---|---|---|
| [10Eros_Max_H3_FL2VA-INT8-ConvRot-HQ.safetensors](https://huggingface.co/DmitryDB/MiniMax-H3-10Eros-Max-Quants/resolve/ddc751be51e084ef1588e94a3c7b7720dea2a0c0/FL2VA/10Eros_Max_H3_FL2VA-INT8-ConvRot-HQ.safetensors) | `diffusion_models` | 約23.5GB | 両方 |
| [qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/dc559027db79c174125df4d827db55cd11178860/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors) | `text_encoders` | 約15.7GB | 両方 |
| [minimax_h3_video_vae_fp16.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/dc559027db79c174125df4d827db55cd11178860/vae/minimax_h3_video_vae_fp16.safetensors) | `vae` | 約5.2GB | 両方 |
| [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/dc559027db79c174125df4d827db55cd11178860/vae/minimax_h3_audio_vae_fp32.safetensors) | `vae` | 約0.6GB | 両方 |
| [h3-realism-people-t2v-i2v-r2v.safetensors](https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA/resolve/039cc8579d7aa357a882d7f4111b25da4f72dccc/h3-realism-people-t2v-i2v-r2v.safetensors) | `loras` | 約0.13GB | 実写 |
| [H3_Anima_Tokenizer.safetensors](https://huggingface.co/TenStrip/Anima-H3-Booster-Lora/resolve/c3c7f955aafce16f046c4327531a04b08e47b85c/H3_Anima_Tokenizer.safetensors) | `loras` | 約0.76GB | アニメ |

共通の4つで約45GB、LoRA を足して1本あたり約45〜46GBです。

配布元：[DmitryDB/MiniMax-H3-10Eros-Max-Quants](https://huggingface.co/DmitryDB/MiniMax-H3-10Eros-Max-Quants)（10Eros Max を ComfyUI 用に変換したもの）／[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)／[fal/MiniMax-H3-Realism-People-LoRA](https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA)／[TenStrip/Anima-H3-Booster-Lora](https://huggingface.co/TenStrip/Anima-H3-Booster-Lora)

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. 「入力：先頭フレーム」の Load Image で自分の画像を選びます。最初は公式テンプレートのサンプル画像の名前が入っていて、そのままだとエラーになります
4. プロンプトを書き換えて実行（Run / Queue Prompt）します。できた動画は ComfyUI の `output/video/` の中に保存されます

- 出力サイズは「生成設定」のノード（Resolution Selector）で変えます。軽く試すなら megapixels を小さくします（ワークフロー内の表を参考に）。
- **実写版**：プロンプトの先頭の `r34l1sm`（LoRA の合図の言葉）は消さないでください。LoRA の強さは 0.7 から、好みで 0.5〜1.0。
- **アニメ版**：LoRA の強さは 0.8 がおすすめで、好みで 0.6〜1.0。プロンプトはタグ形式（`1woman, anime style, ...`）か文章形式のどちらかで書き、混ぜないほうが安定します。
- 動画の長さは H3 の決まり（17k+5 フレーム、24fps）に合わせて自動で丸められるので、指定した秒数とぴったり同じにならないことがあります。

## 元にしたもの

- ComfyUI 公式テンプレート [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates)（MIT License）の `video_minimax_h3_i2v.json`（コミット `e95e3b2` の版）を元にしています。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で準備中です。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・モデルの更新への対応はお約束できません。
