# MiniMax H3 長尺ワークフロー（PrefixStream × RefMod）

YouTube「AIカタチラボ」の動画で使った、動画生成モデル **MiniMax H3**（派生モデル 10Eros Max）用の [ComfyUI](https://github.com/Comfy-Org/ComfyUI) ワークフローです。**PrefixStream** で前の1本の終わり（約0.9秒）を、絵にする前の状態のまま次の1本に引き継ぐので、つなぎ目で動き・曲・声がなめらかにつながります。**RefMod** でキャラの顔画像を参照させて、最後のクリップまで同じ顔を保ちます。

- 動画：https://youtu.be/DyX4Btu6ozk

> **ライセンスについて（必ずお読みください）**
> 10Eros Max は **[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)** にしたがって配布されています。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文と各配布元のページを確認してください。10Eros は LTX 2.3・Wan 2.2・Krea 2 由来の要素も含み、それぞれのライセンスもかかります。
> このフォルダのワークフロー（JSON）と `custom_nodes/katachi_prefixstream` は MIT ライセンスですが、モデルとほかのカスタムノードにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 中身 |
|---|---|
| `PrefixStream_長尺.json` | 動画を作る本体。「実行する」1回で1本（初期値は約5秒）を作り、もう一度押すとその続きを作る。何本目かは自動で数え、その本数のプロンプトを使う（10本まで） |
| `PrefixStream_つないだ動画を作る.json` | 作ったクリップを古い順に1本の動画につなぐ |
| `PrefixStream_RefMod作成.json` | 顔画像（1〜10枚）から RefMod ファイルを作る。先にこちらを1回使います |
| `custom_nodes/katachi_prefixstream/` | 上のワークフローで使う小さなノード（何本目かでプロンプトを切り替える・1本ずつ保存する・つなぐ） |

- 初期設定：10Eros beta5（Turbo 内蔵）、`res_multistep / simple / 7 steps`、480×864（縦長）、1本 124 フレーム（約5秒）、引き継ぎ 22 フレーム（約0.9秒）、seed 固定。
- 初期のプロンプトは動画で使った5本（昼の街中で踊る場面、日本語のセリフつき）です。書き換えて使ってください。

## 必要なもの

- **ComfyUI**：動画では v0.34.0 を使っています。古い場合はノードが赤く表示されるので、ComfyUI を更新してください。
- **GPU**：動画では Google Colab の A100（40GB）で動かしています。家庭用 GPU では試していません。
- **ffmpeg**：つないだ動画を作るときに使います。
- **カスタムノード**（ComfyUI/custom_nodes/ に入れます。動画で使った版のコミットも書いておきます）

| ノード | ライセンス |
|---|---|
| [ComfyUI-MiniMaxH3-PrefixStream](https://github.com/knoic/ComfyUI-MiniMaxH3-PrefixStream)（`bdef956`） | MIT |
| [ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod)（RefMod、`f946208`） | MIT |
| このフォルダの `custom_nodes/katachi_prefixstream` | MIT |

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

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します。`custom_nodes/katachi_prefixstream` フォルダは中の2つのファイル（`__init__.py` と `web/h3ps_download.js`）を同じ形で ComfyUI/custom_nodes/ に置き、ComfyUI を起動し直します
2. **RefMod を作る**：ComfyUI の `input` フォルダの中に `character` フォルダを作り、キャラの顔画像を 1〜10 枚入れます（おすすめは5枚：正面・横顔の左右・斜めの左右）。`PrefixStream_RefMod作成.json` を ComfyUI にドラッグ＆ドロップし、Create H3 RefMod の name（初期値 `my_face`）を決めて実行。`models/refmods` に保存されます
3. **動画を作る**：`PrefixStream_長尺.json` をドラッグ＆ドロップし、
   - 「最初の画像（1本目だけ使う）」で、最初のフレームにする画像を選ぶ（最初は空です）
   - 「Load H3 RefMods」の mod_1 で、2 で作った RefMod を選ぶ
   - 左のオレンジ色の「★クリップNのプロンプト」を書き換える
4. 「実行する」を押すと1本目ができます。もう一度押すと、前の1本の続きの2本目ができます。何本目かは自動で数えるので、作りたい本数だけ押します。できた1本は `output/minimax_h3_bins/` に入ります
5. **つなぐ**：`PrefixStream_つないだ動画を作る.json` を開いて実行すると、`output/h3ps_joined/` に1本の動画ができます

- 気に入らない1本を作り直すときは、「続ける元のクリップ（素材箱）」の一覧で1つ前のクリップを選んでから実行します。戻すときは clip_selection を `latest` にします。
- 新しい動画を始めるときは、素材箱の名前（project_name、初期値 `my_video`）を新しい名前にします。ワークフロー内の4か所と、つなぐワークフローを同じ名前にそろえてください。
- 1本の長さは「H3 I2V」の length（フレーム数。24 で1秒、17 の倍数＋5、上限 345）で変えます。途中で変えないでください。
- 6本目からは、「★クリップNのプロンプト」ノードを複製して「何本目かでプロンプトを自動で切り替え」の `prompt_6`〜`prompt_10` につなぎます（10本まで）。
- 1本目のプロンプトの冒頭に入れる1行（Picture 1 …）は自動で足し、2本目からは自動で外します。
- RefMod が効いていないように見えるときは、Load H3 RefMods の `strength_1` と「RefMod ON/OFF（enable）」の `retention` が 1.0 か確認し、`copies_1` を 2〜3 に上げてみてください（遅くなります）。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で扱っています。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・ノード・モデルの更新への対応はお約束できません。
