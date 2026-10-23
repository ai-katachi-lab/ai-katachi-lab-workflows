# MiniMax H3 × 10Eros Turbo 内蔵版 ワークフロー（I2V / T2V）

YouTube「AIカタチラボ」の動画で使った、動画生成モデル **MiniMax H3** の派生モデル **10Eros Max TURBO-hybrid Beta3** 用の [ComfyUI](https://github.com/comfyanonymous/ComfyUI) ワークフローです。高速化（Turbo）がモデルに入っているので、7ステップほどで音声つきの動画を作れます。

- 動画：https://youtu.be/xrwEXFcKt_k

> **ライセンスについて（必ずお読みください）**
> 10Eros Max は **[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)** にしたがって配布されています。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文と各配布元のページを確認してください。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | できること |
|---|---|
| `10Eros_Turbo内蔵_I2V.json` | 画像から動画（最後のコマの画像も指定できます） |
| `10Eros_Turbo内蔵_T2V.json` | 文章だけから動画 |

どちらも ComfyUI 公式の MiniMax H3 テンプレート（画像→動画・文章→動画）を元に、次のように変えています。

- 本体を 10Eros Max TURBO-hybrid Beta3 に、テキストエンコーダーを int8 版に差し替え
- Turbo がモデルに入っているので、公式テンプレートの Turbo LoRA の経路を外し、初期値を `res_multistep / simple / 7 steps` に
- 動画の長さを秒で指定できるように（5秒が初期値）
- I2V：入力画像の縦横比のまま約 0.40 MP に合わせるように。最後のコマ用の画像読み込み「LastImage（任意）」を追加（初期状態ではつながっていません）
- 使い方の日本語メモを追加

## 必要なもの

- **ComfyUI**：MiniMax H3 に対応した新しいもの。古い場合はノードが赤く表示されるので、ComfyUI を更新してください。
- **カスタムノード**：不要です（ComfyUI 標準のノードだけで動きます）。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **モデル**：下の表のファイル。このリポジトリには入っていないので、配布元から取得してください。

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ |
|---|---|---|
| [10Eros_Max_h3_TURBO-hybrid_beta3_int8_convrot_skip_edges.safetensors](https://huggingface.co/cicalooo/10Eros-Max-h3-int8-convrot/resolve/dbdd87944063bc01d8062bae1dba12212ca4061f/10Eros_Max_h3_TURBO-hybrid_beta3_int8_convrot_skip_edges.safetensors) | `diffusion_models` | 約22.5GB |
| [qwen3vl_32b_minimax_h3_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors) | `text_encoders` | 約27.1GB |
| [minimax_h3_video_vae_fp16.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_video_vae_fp16.safetensors) | `vae` | 約5.2GB |
| [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_audio_vae_fp32.safetensors) | `vae` | 約0.6GB |

合計 約55.5GB です。I2V と T2V で同じモデルを使います。

配布元：[cicalooo/10Eros-Max-h3-int8-convrot](https://huggingface.co/cicalooo/10Eros-Max-h3-int8-convrot)（[TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max) を int8 に変換したもの）／[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. I2V は「FirstImage（開始画像）」の Load Image で自分の画像を選びます。最初は公式テンプレートのサンプル画像の名前が入っていて、そのままだとエラーになります
4. プロンプトを書き換えて実行（Run / Queue Prompt）します。できた動画は ComfyUI の `output/video/` の中に保存されます

- ステップ数は Steps ノードで 6〜8 などに変えられます。
- I2V で最後のコマも決めたいときは、「LastImage（任意）」の IMAGE を生成ノードの `last_frame` につなぎます。
- T2V の大きさは Resolution Selector で決めます（初期値 16:9・0.40 MP＝864×480。ワークフロー内の表を参考に）。
- 動画の長さは H3 の決まり（17k+5 フレーム、24fps）に合わせて自動で丸められるので、指定した秒数とぴったり同じにならないことがあります（5秒 → 約5.17秒）。
- 初期のプロンプトは公式テンプレートの例（I2V はマウスの製品映像、T2V は街のアクション映像）のままです。

## 元にしたもの

- ComfyUI 公式テンプレート [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates)（MIT License）の `video_minimax_h3_i2v.json`・`video_minimax_h3_t2v.json`（コミット `66abae5` の版）を元にしています。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で準備中です。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・モデルの更新への対応はお約束できません。
