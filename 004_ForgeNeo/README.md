# Forge Neo × Anima Colab ノートブック

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ai-katachi-lab/ai-katachi-lab-workflows/blob/main/004_ForgeNeo/Forge_Neo_Colab.ipynb)

YouTube「AIカタチラボ」の動画で使った、画像生成ソフト Stable Diffusion WebUI **Forge Neo** を Google Colab で起動するノートブックです。アニメ・イラスト向けの画像生成モデル **Anima** を使えるようにしています。

- 動画：https://youtu.be/_0a4ULyLpAQ

> **ライセンスについて（必ずお読みください）**
> Anima のモデルは **[CircleStone Labs Non-Commercial License](https://huggingface.co/circlestone-labs/Anima/blob/main/LICENSE.md)（非商用ライセンス）** です。モデルを商用目的で使うことはできません。生成した画像の扱いも含め、使う前にライセンス本文を確認してください。
> このノートブックは MIT ライセンスですが、Forge Neo 本体・拡張機能・モデルにはそれぞれのライセンスが別にかかります。

## 必要なもの

- **Google アカウント**：モデルを Google ドライブに保存します（Anima 一式で約5.6GB の空きが必要です）
- **Colab の A100 GPU**：Colab Pro などの有料プランで A100 を選んでください。**A100 以外の GPU（無料版の T4 など）では、最初のチェックで止まる設定です。**

## 使い方

1. 上の「Open in Colab」ボタンを押して、ノートブックを開きます
2. メニューの「ランタイム」→「ランタイムのタイプを変更」で **A100 GPU** を選びます
3. 上のセルから順番に実行します（▶ ボタン）
   - 「3. Google Drive のマウント」で、Google ドライブへのアクセスを許可します
   - 「3-2. Anima モデルの自動ダウンロード」で、Anima を Google ドライブに保存します（2回目からはスキップされます）
   - Colab では毎回環境を作り直すので、起動（「8」で URL が出る）までに20分〜1時間ほどかかります（各セルの目安時間の合計）
4. 「8. Forge Neo 起動」のセルに表示される `https://….gradio.live` を開き、すぐ下に表示されるユーザー名とパスワードでログインします
5. 画面左上の Checkpoint で `anima-aesthetic-v1.1.safetensors` を選び、その横の「VAE / Text Encoder」で **`qwen_image_vae.safetensors` と `qwen_3_06b_base.safetensors` の2つだけ** を選んで生成します（SDXL 用の VAE `sdxl_vae.safetensors` などを一緒に選ぶとエラーになります）
6. 終わったら「9. 生成画像の ZIP ダウンロード」で画像を保存します。**Colab を終了すると、生成した画像は消えます**

## Anima について

- 自動ダウンロードは、配布元 [circlestone-labs/Anima](https://huggingface.co/circlestone-labs/Anima) から次の3つを Google ドライブの `StableDiffusion/models` に保存します。

| ファイル | 保存先 |
|---|---|
| 本体（初期設定は `anima-aesthetic-v1.1`） | `Stable-diffusion` |
| `qwen_3_06b_base.safetensors`（テキストエンコーダー） | `text_encoder` |
| `qwen_image_vae.safetensors`（VAE） | `VAE` |

- 本体は `ANIMA_MODEL` で選べます。`anima-turbo-v1.1` は高速版（配布元の推奨は CFG 1・8〜12 ステップ）、`anima-base-v1.0` は LoRA 学習向けの素の版です。
- 配布元の推奨設定は、512〜1536px、30〜50 ステップ、CFG 4〜5 です。プロンプトのコツは配布元のページに詳しく書かれています。
- Anima 以外のモデル（SDXL・Illustrious など）も、Google ドライブの `StableDiffusion/models/Stable-diffusion` に置けば使えます。

## 入っている拡張機能

ノートブックが起動時に次の拡張機能を自動で入れます（このリポジトリには入っていません）。

- [ADetailer-Neo](https://github.com/Haoming02/ADetailer-Neo)：顔などを自動で直す
- [Forge Couple](https://github.com/Haoming02/sd-forge-couple)：画面を区切って複数人物を描き分ける
- [Florence-2 Neo](https://github.com/AMGarkin/sd-webui-florence-2-neo)：画像から説明文を作る
- [Civitai Downloader](https://github.com/otacoo/sd-webui-civitai-downloader)：Civitai のモデルを画面から取得する（Colab の「シークレット」に `CIVITAI_API_TOKEN` を登録すると、ログインが必要なモデルも取得できます）

## 元にしたもの

- [Stable Diffusion WebUI Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo)（Haoming02）を、固定したバージョンで導入しています。

## 注意

- 動画の中で動作を確認したノートブックを、配布用に整えたものです。Anima の自動ダウンロード（3-2）は配布用に足した部分で、動画では使っていません。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、Colab・Forge Neo・モデルの更新への対応はお約束できません。
