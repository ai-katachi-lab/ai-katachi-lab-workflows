# MiniMax H3 長尺＋顔固定 ワークフロー（Extender × RefMod）

YouTube「AIカタチラボ」の動画で使った、動画生成モデル **MiniMax H3**（派生モデル 10Eros Max）用の [ComfyUI](https://github.com/comfyanonymous/ComfyUI) ワークフローです。**MiniMax H3 Extender** でクリップをつないで15秒を超える長尺の動画を作り、**RefMod** でキャラの顔画像を参照させて、最後のクリップまで同じ顔を保ちます。

- 動画：https://youtu.be/oiusJ_s7w7M

> **ライセンスについて（必ずお読みください）**
> 10Eros Max は **[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)** にしたがって配布されています。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文と各配布元のページを確認してください。10Eros は LTX 2.3・Wan 2.2・Krea 2 由来の要素も含み、それぞれのライセンスもかかります。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルとカスタムノードにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 中身 |
|---|---|
| `H3長尺_Extender_RefMod_3本.json` | 長尺動画を作る本体。3クリップ（初期値は1本10秒）を Extender でつなぎ、RefMod で顔を保つ |
| `H3長尺_RefMod作成.json` | 顔画像（1〜10枚）から RefMod ファイルを作る。先にこちらを1回使います |

- 初期設定：10Eros beta5（Turbo 内蔵）、`res_multistep / simple / 7 steps`、864×480、seed 固定、1本ずつ作って確かめるモード（clip_by_clip）。
- 初期のプロンプトは動画で使った3本（海辺の人物の場面、日本語のセリフつき）です。書き換えて使ってください。
- 動画を作ったノートブックはプロンプトの本数を設定ファイルで変えられましたが、このワークフローは3本で固定しています。

## 必要なもの

- **ComfyUI**：動画では v0.34.0 を使っています。古い場合はノードが赤く表示されるので、ComfyUI を更新してください。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **カスタムノード**（ComfyUI/custom_nodes/ に入れます。動画で使った版のコミットも書いておきます）

| ノード | ライセンス |
|---|---|
| [ComfyUI_MiniMax_H3_Extender](https://github.com/tritant/ComfyUI_MiniMax_H3_Extender)（v2.9.2、`79d1978`） | Apache-2.0 |
| [ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod)（RefMod、`f946208`） | MIT |

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ |
|---|---|---|
| [10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors](https://huggingface.co/TenStrip/10Eros-Max/resolve/8a198588c8870ab0d613b3492a3150d091c8c2dd/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors) | `diffusion_models` | 約21GB |
| [qwen3vl_32b_minimax_h3_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors) | `text_encoders` | 約27.1GB |
| [minimax_h3_video_vae_fp16.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_video_vae_fp16.safetensors) | `vae` | 約5.2GB |
| [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_audio_vae_fp32.safetensors) | `vae` | 約0.6GB |

合計 約54GB です。配布元：[TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max)／[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. **RefMod を作る**：ComfyUI の `input` フォルダの中に `character` フォルダを作り、キャラの顔画像を 1〜10 枚入れます（おすすめは5枚：正面・横顔の左右・斜めの左右）。`H3長尺_RefMod作成.json` を ComfyUI にドラッグ＆ドロップし、Create H3 RefMod の name（初期値 `my_face`）を決めて Run。`models/refmods` に保存されます
3. **動画を作る**：`H3長尺_Extender_RefMod_3本.json` をドラッグ＆ドロップし、
   - 1本目のクリップカードの「First」欄で、最初のフレームにする画像を選ぶ（最初は空です）
   - 「Load H3 RefMods」の mod_1 で、2 で作った RefMod を選ぶ
   - 左の「クリップNのプロンプト」を書き換える
4. Run を押すと、まだ確かめていない最初のクリップが作られます。プレビューを見て良ければクリップカードの **Validate** を押し、1本ずつ繰り返します
5. **Final Decode** のプレビューに、つないだ動画が表示されます。ここから保存できます

- まとめて作るときは、Extender の run_mode を `full_batch` にします。
- 1本の長さは各クリップカードで変えます（上限は約14.4秒）。全クリップ同じ値にしてください。
- クリップを減らすときは、カードの × ではなく「クリップNのプロンプト」ノードを**後ろから**削除します。
- 各クリップの seed が同じ値で `after: fixed` になっていることを確認してください。
- RefMod が効いていないように見えるときは、Load H3 RefMods の `strength_1` と「RefMod ON/OFF（enable）」の `retention` が 1.0 か確認し、`copies_1` を 2〜3 に上げてみてください（遅くなります）。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で扱っています。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・ノード・モデルの更新への対応はお約束できません。
