# P-H3-Image 同じ人物 ワークフロー（LoRA なしで、画像で人物・服・ポーズを指定）

YouTube「AIカタチラボ」の動画で使った、**P-H3-Image** で画像を作る [ComfyUI](https://github.com/Comfy-Org/ComfyUI) ワークフローです。

- 動画：https://youtu.be/pgHUkuruoyE

**LoRA を作らずに**、入れた画像（人物の顔・服・ポーズ）とプロンプトから画像を作ります。同じ人物のまま場面・向き・表情・服を変えたり、ポーズの画像からポーズだけを使ったり、2人を並べたりできます。入れる画像の枚数（1〜5枚）ごとに、ワークフローが1本ずつあります。

> **ライセンスについて**
> P-H3-Image の重みは MiniMax H3 Community License です。日本は利用できる地域です（EU・英国・韓国・米国は対象外）。年間の売上が2,000万米ドルを超える場合は MiniMax の許可が要ります。作った画像を公開・販売するときは、AI で作ったことを明示してください。製品やサービスに組み込むときは「Powered by MiniMax H3」の表示が要ります。使う前に配布元のページでライセンス本文を確認してください。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルにはそれぞれのライセンスが別にかかります。

Powered by MiniMax H3

## 入っているもの

| ファイル | 入れる画像の例 |
|---|---|
| `同じ人物_画像1枚.json` | 顔1枚 → 場面・向き・表情を変える |
| `同じ人物_画像2枚.json` | 顔＋服 → 服を着せ替える |
| `同じ人物_画像3枚.json` | 顔＋服＋ポーズ／同じ人物の顔3枚（正面・斜め・横） |
| `同じ人物_画像4枚.json` | 2人：顔A＋服A＋顔B＋服B |
| `同じ人物_画像5枚.json` | 2人＋ポーズ：顔A＋服A＋顔B＋服B＋ポーズ |

## 必要なもの

- **ComfyUI**：動画では v0.44.2 で動かしています（P-H3-Image の部品が入った最初の正式版です）。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **カスタムノード**：いりません。ComfyUI 本体に入っているノードだけで動きます。

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。動画では int8 を使っています。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ |
|---|---|---|
| [p-h3-image_int8_convrot.safetensors](https://huggingface.co/PrunaAI/P-H3-Image-Comfy/resolve/44a0fb73f299da1bb715bdb5ff59ce3fd3c6f543/diffusion_models/p-h3-image_int8_convrot.safetensors) | `diffusion_models` | 約21.2GB |
| [p-h3-image_text_encoder_int8_convrot.safetensors](https://huggingface.co/PrunaAI/P-H3-Image-Comfy/resolve/44a0fb73f299da1bb715bdb5ff59ce3fd3c6f543/text_encoders/p-h3-image_text_encoder_int8_convrot.safetensors) | `text_encoders` | 約5.1GB |
| [p-h3-image_vae_int8_convrot.safetensors](https://huggingface.co/PrunaAI/P-H3-Image-Comfy/resolve/44a0fb73f299da1bb715bdb5ff59ce3fd3c6f543/vae/p-h3-image_vae_int8_convrot.safetensors) | `vae` | 約3.1GB |

bf16 版（約55GB）を使うときは、[P-H3-Image-Comfy](https://huggingface.co/PrunaAI/P-H3-Image-Comfy) から取り、「画像を作る本体」「文章と画像を読み取る部分」「画像に変換する部分」のファイル名を選び直してください。

## 使い方

1. このページ上のファイル一覧から、入れる画像の枚数の JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. **★画像1〜** に画像をアップロードします。★画像1 が元にする画像で、できる画像の縦横はこの画像に合わせます
4. **★プロンプト（ここに書く）** に、作りたい場面と、それぞれの画像の役割を英語で書きます。画像は `<Picture 1>` のように番号で呼びます
5. Run を押すと1枚できます。**★シード** は毎回ランダムに変わります

- 書き方の例（画像1＝人物の顔、画像2＝服）：`The woman from <Picture 1>: keep her same face and hairstyle, and dress her in the outfit from <Picture 2>.` に続けて、場面・ポーズ・写し方を書きます。
- ポーズの画像を入れるときは `Use <Picture N> only as a reference for the pose. Do not copy the face, hair or clothes of the person in <Picture N>.` と書き添えます。
- 2人のときは `Woman A is the woman from <Picture 1> … Woman B is the woman from <Picture 3> …` のように人ごとに画像を書き分け、`Woman A on the left, Woman B on the right.` のように並びも書きます。
- **★画像の大きさ** は、できる画像の総画素（MP）です。初めは 4。公式のおすすめは 4 か 8 です。
- 設定は、描き直し8回・CFG なし・euler（公式の edit ワークフローと同じ）です。
- 細かい使い方は、ワークフローの中の日本語メモを見てください。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書・プロンプト例は、BOOTH のショップ「AIカタチラボ」で扱っています。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 実在の人物の画像を使うときは、本人の同意があり法令に沿う素材だけを使ってください。未成年・同意のない内容・なりすましには使わないでください。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・モデルの更新への対応はお約束できません。
