# MiniMax-H3-Image ＋ H3 一気通貫ワークフロー（テキスト → 画像 → 動画 → 長尺 → 仕上げ）

YouTube「AIカタチラボ」の動画で使った [ComfyUI](https://github.com/Comfy-Org/ComfyUI) のワークフローです。画像のモデル **MiniMax-H3-Image** で人物・服・背景の画像を作り、動画のモデル **MiniMax H3** で、その人物が話して動く動画にします。1本のワークフローの中で区画（グループ）をオン／オフしながら、上から順に進めます。

- 動画：https://youtu.be/gI7Rubcn18E

> **ライセンスについて（必ずお読みください）**
> **MiniMax-H3-Image** は [MiniMax-H3-Image Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3-Image/blob/main/LICENSE)、**MiniMax H3**（ハイブリッド版・Pika-H3-Flex・10Eros Max を含む）は [MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) にしたがって配布されています。MiniMax-H3-Image のライセンスでは、米国・EU・英国・韓国での利用と、作った画像・動画をそれらの地域で表示することが認められていません。SNS など世界から見られる場所に公開する前に、MiniMax の許可（waiver）の申請先 https://platform.minimax.io/console/license を確認してください。作ったものを公開するときは AI で作ったことを明示してください。年商や地域によって条件が変わるので、使う前にライセンス本文と各配布元のページを確認してください。10Eros Max は LTX 2.3・Wan 2.2・Krea 2 由来の要素も含み、それぞれのライセンスもかかります。
> このリポジトリのワークフロー（JSON）と `custom_nodes/h3flow`・`custom_nodes/h3ps_tools` は MIT ライセンスですが、モデルとほかのカスタムノードにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | 中身 |
|---|---|
| `H3Image_一気通貫.json` | ワークフロー本体。① から ⑦ の区画を、1つずつオンにして上から順に使います |
| `custom_nodes/h3flow/` | 区画どうしを画像・動画のファイルでつなぐ小さなノード（番号で1枚選ぶ・人物の手本を保存して読む・服と背景を選ぶ など） |
| `custom_nodes/h3ps_tools/` | 何本目かでプロンプトを切り替える・1本をダウンロードする・つないだ動画を作るノード |

| 順 | 区画 | 入れるもの | 出てくるもの |
|---|---|---|---|
| 1 | ① T2I | テキスト（人物の顔） | 画像4枚 → 番号で1枚選ぶ |
| 2 | ①-2 服・背景づくり | テキスト（服・場所） | 服・背景の画像（各2枚 → 番号で1枚ずつ選ぶ） |
| 3 | ②-1 手本づくり | ①で選んだ画像 | 人物の手本5枚＋RefMod（自動） |
| 4 | ②-2 動かす画像づくり | 人物の手本＋服・背景の画像＋テキスト | 動かす画像（2枚 → 番号で1枚選ぶ） |
| 5 | ③ I2V | 動かす画像＋RefMod＋テキスト | 動画1本目（約5秒） |
| 6 | ④ 長尺 | 前の動画の最後 約1.6秒＋RefMod＋テキスト | 続きの動画（2〜5本目） |
| 7 | ⑤ つなぐ | 動画1〜5本目 | つないだ動画（約19秒） |
| 8 | ⑥ 高解像度に | つないだ動画 | 約2倍の大きさの動画 |
| 9 | ⑦ 顔を直す | 高解像度にした動画＋人物の手本（正面）＋テキスト | 完成の動画 |

言葉の意味：**人物の手本**＝同じ人物の顔の写真5枚（正面・斜め左・斜め右・横左・横右）。**RefMod**＝人物の手本から作るファイルで、動画で顔を保つために使います。**動かす画像**＝動画の0秒目になる1枚。

- 初期設定：画像 1536×2688（6ステップ）、動画 768×1344・1本 124 フレーム（約5秒）×5本、引き継ぎ 39 フレーム（約1.6秒）、動画は Pika-H3-Flex＋lcm の6ステップ。
- ★のついたテキスト欄は空です。動画で使ったプロンプトは動画の中で紹介しています。

## 必要なもの

- **ComfyUI**：v0.45.0 以上（MiniMax-H3-Image のノードが入った版）。動画では v0.45.2 を使っています。
- **GPU**：動画では Google Colab の A100（80GB）で動かしています。家庭用 GPU では試していません。
- **ffmpeg**：つないだ動画を作るときに使います。
- **Python のパッケージ**：⑦ で `ultralytics`・`insightface`・`onnxruntime`（GPU 版）・`scenedetect` を使います。
- **カスタムノード**（ComfyUI/custom_nodes/ に入れます。動画で使った版のコミットも書いておきます）

| ノード | 使う区画 | ライセンス |
|---|---|---|
| [ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod)（RefMod、`f946208`） | ②-1・③④ | MIT |
| [ComfyUI-MiniMaxH3-PrefixStream](https://github.com/knoic/ComfyUI-MiniMaxH3-PrefixStream)（`e5dc4cd`） | ③④⑤ | MIT |
| [ComfyUI-H3-Video-Upsampler](https://github.com/dntpi/ComfyUI-H3-Video-Upsampler)（`36cb612`） | ⑥ | MIT |
| [ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine)（`d8521d1`） | ⑦ | MIT |
| [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)（`4d907be`） | ⑦ | GPL-3.0 |
| ComfyUI-H3-NativeAudioLock（[MiniMax-H3-NativeAudio-MusicVideo-Workflow](https://github.com/Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow) の `custom_nodes/` の中、`11a95f6`） | ⑦ | 配布元にライセンスの記載なし |
| このリポジトリの `custom_nodes/h3flow`・`custom_nodes/h3ps_tools` | 全体 | MIT |

## モデル

ファイル名のリンクから直接ダウンロードできます（動画で使った版に固定したリンクです）。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ | 使う区画 |
|---|---|---|---|
| [minimax_h3_image_pruned_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3-Image/resolve/0bb149f51e3156ed4b90dd45d5620346bfe1df8f/diffusion_models/minimax_h3_image_pruned_int8_convrot.safetensors) | `diffusion_models` | 約21.0GB | ①〜②-2 |
| [minimax_h3_image_vae_fp16.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3-Image/resolve/0bb149f51e3156ed4b90dd45d5620346bfe1df8f/vae/minimax_h3_image_vae_fp16.safetensors) | `vae` | 約1.2GB | ①〜②-2 |
| [qwen3.5_9b_w4a8_gptq.safetensors](https://huggingface.co/Comfy-Org/Qwen3.5/resolve/a3f61d217d07c6936174625ce5d06e6079e9393e/text_encoders/qwen3.5_9b_w4a8_gptq.safetensors) | `text_encoders` | 約7.3GB | ① のプロンプト拡張 |
| [qwen3vl_32b_minimax_h3_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors) | `text_encoders` | 約27.1GB | 画像と動画で共通 |
| [minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors](https://huggingface.co/smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models/resolve/a36feb17fbd1f20ff4bdd509ccd07e2b7b585a38/minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors) | `diffusion_models` | 約21.0GB | ③④ |
| [pika_h3_flex_fl2va_comfy_bf16.safetensors](https://huggingface.co/Pika-Labs/Pika-H3-Flex/resolve/ca45d99f9b1d1859ffb9dc1cd6bfaaa994257f56/comfy/loras/pika_h3_flex_fl2va_comfy_bf16.safetensors) | `loras` | 約2.0GB | ③④ |
| [minimax_h3_video_vae_fp16.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_video_vae_fp16.safetensors) | `vae` | 約5.2GB | ③〜⑦ |
| [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/vae/minimax_h3_audio_vae_fp32.safetensors) | `vae` | 約0.6GB | ③〜⑦ |
| [minimax_h3_ref2va_pruned_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/4cc1d817b6184899b41293954329f576cb5ae86b/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors) | `diffusion_models` | 約21.0GB | ⑥ |
| [minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/3f941d5d182014dd5c0a5e16330420ee2d4aa0c6/minimax_h3_latent_upscaler_3d_conv_v1/minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors)（**`minimax_h3_latent_upscaler_3d_bf16.safetensors` という名前で保存**） | `latent_upscale_models` | 約0.7GB | ⑥ |
| [h3upscale_v2_x2.safetensors](https://huggingface.co/sandpies/ComfyUI-H3-Video-Upsampler/resolve/9337fe00d0753d249aba6181b81d3b6a62bccb52/lora/h3upscale_v2_x2.safetensors) | `loras` | 約0.6GB | ⑥ |
| [10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors](https://huggingface.co/TenStrip/10Eros-Max/resolve/8a198588c8870ab0d613b3492a3150d091c8c2dd/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors) | `diffusion_models` | 約21.0GB | ⑦ |
| [face_yolov8m.pt](https://huggingface.co/Bingsu/adetailer/resolve/53cc19de382014514d9d4038601d261a7faa9b7b/face_yolov8m.pt) | `ultralytics/bbox` | 約52MB | ⑦ |
| [person_yolov8m-seg.pt](https://huggingface.co/Bingsu/adetailer/resolve/53cc19de382014514d9d4038601d261a7faa9b7b/person_yolov8m-seg.pt) | `ultralytics/segm` | 約55MB | ⑦ |

合計 約129GB です。⑦ では、顔を見分けるための InsightFace の buffalo_l をノードが初回に自動で取得します（非商用の研究用途とされています）。

| モデル | ライセンス |
|---|---|
| MiniMax-H3-Image | MiniMax-H3-Image Community License |
| MiniMax H3・ハイブリッド版・Pika-H3-Flex・10Eros Max | MiniMax H3 Community License（10Eros Max は LTX 2.3・Wan 2.2・Krea 2 のライセンスもかかります） |
| Qwen3.5 9B・潜在アップスケーラー（LBH-123-AI）・顔検出（Bingsu/adetailer） | Apache-2.0 |
| h3upscale LoRA（sandpies） | MIT |

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します。`custom_nodes/h3flow` と `custom_nodes/h3ps_tools` は中のファイル（`h3flow/__init__.py`、`h3ps_tools/__init__.py` と `h3ps_tools/web/h3ps_download.js`）を同じ形で ComfyUI/custom_nodes/ に置き、ComfyUI を起動し直します
2. `H3Image_一気通貫.json` を ComfyUI にドラッグ＆ドロップします。開いたときは **① T2I** の区画だけがオンです
3. 区画は、名前の帯をクリックして選び **Ctrl+B** でオン／オフします（紫＝オフ）。オンにする区画は1つずつです。各区画の左上のメモに、その区画の使い方を書いています
4. ① から順に、オレンジ色の **★…（ここに書く）** に書いて「実行する」を押し、できた画像・動画を見ながら次の区画へ進みます

- 人物の手本5枚は ComfyUI の `input/h3flow_character/` に保存されます（前の5枚は `input/character_old/` に移ります）。RefMod は `models/refmods/` に `h3flow_person` という名前で作られ、③④ はいつもこれを使います。
- 自分で用意した服・背景の画像を使うときは、②-2 の「服・背景」ノードで「input/parts の画像」を選び、ComfyUI の `input/h3flow_parts/` に `clothes.png`・`background.png` を置きます。
- できた1本1本は `output/minimax_h3_bins/` の素材箱に、つないだ動画は `output/h3ps_joined/` に、⑥⑦ の動画は `output/h3flow_finish/` に入ります。
- 5本そろったあとに ③④ で「実行する」を押すと、自動で新しい流れの1本目（動かす画像から）になります。

## Colab ですぐ動かしたい方へ

このワークフローを Colab ですぐ動かせるノートブックと、詳しい手順書は、BOOTH のショップ「AIカタチラボ」で扱っています。

→ [AIカタチラボ（BOOTH）](https://aikatachilabo.booth.pm/)

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 実在の人物に似せた画像・動画、未成年に見える人物、同意のない内容は作らないでください。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・ノード・モデルの更新への対応はお約束できません。
