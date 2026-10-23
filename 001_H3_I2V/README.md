# MiniMax H3 画像から動画 ワークフロー（I2V / L2V / FL2V）

YouTube「AIカタチラボ」の動画で使った、動画生成モデル **MiniMax H3** 用の [ComfyUI](https://github.com/comfyanonymous/ComfyUI) ワークフローです。1枚または2枚の画像から、音声つきの動画を作ります。

- 動画：https://youtu.be/Qqm-3XHxuH4

> **ライセンスについて（必ずお読みください）**
> MiniMax H3 のモデルは **[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)** です。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文を確認してください。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 中身 |
|---|---|
| `video_minimax_h3_i2v.json` | ComfyUI 公式の MiniMax H3 画像→動画テンプレートに、使いやすくする調整を加えたもの |

公式テンプレートから変えたところ：

- 出力サイズを、数字で直接入力できる「出力幅 Width」「出力高さ Height」の青いノードに置き換え（初期値は縦長の 768×1344）
- 最後のコマ用の画像読み込みノード「最終画像」を追加（初期状態ではつながっていません）
- 動画の長さの初期値を5秒に変更
- 使い方の日本語メモ「日本語ガイド：I2V / L2V / FL2V」を追加

## 3つの使い方

| モード | つなぎ方 | できること |
|---|---|---|
| I2V | 最初の画像を first_frame につなぐ | 最初のコマから動き出す動画 |
| L2V | 「最終画像」を last_frame につなぎ、first_frame は外す | 最後のコマに向かって終わる動画 |
| FL2V | 両方つなぐ | 最初と最後のコマの間をつなぐ動画 |

## 必要なもの

- **ComfyUI**：MiniMax H3 に対応した新しいもの。古い場合はノードが赤く表示されるので、ComfyUI を更新してください。
- **カスタムノード**：不要です（ComfyUI 標準のノードだけで動きます）。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **モデル**：下の表のファイル。このリポジトリには入っていないので、配布元から取得してください。

## モデル

配布元は [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)（Hugging Face）です。ファイル名のリンクから直接ダウンロードできます。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ |
|---|---|---|
| [minimax_h3_fl2va_pruned_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors) | `diffusion_models` | 約21GB |
| [qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors) | `text_encoders` | 約16GB |
| [minimax_h3_video_vae_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_int8_convrot.safetensors) | `vae` | 約2.8GB |
| [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors) | `vae` | 約0.6GB |
| （任意）[minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors](https://huggingface.co/lightx2v/Minimax-h3-Turbo/resolve/main/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors) | `loras` | 約2GB |

必須の4つで合計約40GBです。最後の LoRA は高速化用で、なくても動きます。

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. 画像読み込みノードで自分の画像を選びます。最初は公式テンプレートのサンプル画像の名前が入っていて、そのままだとエラーになります
4. プロンプトを書き換えて実行（Run / Queue Prompt）します。できた動画は ComfyUI の `output/video/` の中に保存されます

- 出力サイズは青い「出力幅 Width」「出力高さ Height」ノードで変えます。必ず **32の倍数** にしてください（例：縦長 768×1344、軽く試すなら 480×864、横長 1344×768）。
- 動画の長さは4〜15秒で指定できます。24fps の決まったコマ数に合わせるため、指定した秒数とぴったり同じにならないことがあります。
- 高速化 LoRA を使うときは、`loras` に入れたうえで、ワークフロー内の「Enable Lightning LoRA」を true にします。
- 動画で使った Colab ノートブックでは、VAE に `minimax_h3_video_vae_fp16.safetensors` を使っていました。今の公式テンプレートに合わせて、このワークフローでは int8 版を使います。

## 元にしたもの

- ComfyUI 公式テンプレート [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates)（MIT License）の `video_minimax_h3_i2v.json`（2026年10月時点の版）を元にしています。

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出し、今の公式テンプレートに合わせたものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・モデルの更新への対応はお約束できません。
