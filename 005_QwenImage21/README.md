# Qwen-Image 2.1 ワークフロー（画像生成／画像編集／複数画像合成）

YouTube「AIカタチラボ」の動画で使った [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 用のワークフローです。

- 動画：https://youtu.be/bWXlMPHS9n0

> **ライセンスについて（必ずお読みください）**
> Qwen-Image 2.1 のモデルは **[Qwen RESEARCH LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE)（研究・評価のみ、非商用）** です。生成した画像の商用利用はできません。
> このフォルダのワークフロー（JSON）は MIT ライセンスですが、モデルにはそれぞれのライセンスが別にかかります。

## 入っているもの

| ファイル | できること |
|---|---|
| `Type-A_T2I_Text-to-Image.json` | 文章（プロンプト）だけから画像を作る |
| `Type-B_I2I_Prompt-Image-Edit.json` | 1枚の画像を、文章の指示で編集する（服・背景・色の変更など） |
| `Type-C_Multi-Image-Composition.json` | 2枚の画像を参照して1枚にまとめる（例：1枚目の人物に、2枚目の服を着せる） |

- 3本とも初期設定は、高速化用の Turbo LoRA を使った 8ステップです。
- プロンプトは日本語で書けます。書いた文章は、プロンプト補強用の言語モデル（Prompt Enhancer）が自動で詳しく書き直してから画像を作ります。

## 必要なもの

- **ComfyUI**：Qwen-Image 2.1 に対応した新しいもの（2026年10月時点の版で動作を確認。コミット `79be670`）。古い場合はノードが赤く表示されるので、ComfyUI を更新してください。
- **カスタムノード**：不要です（ComfyUI 標準のノードだけで動きます）。
- **GPU**：動画では Google Colab の A100 GPU で動かしています。モデルが大きいので、一般的な家庭用 GPU ではメモリが足りない可能性があります（家庭用 GPU では未検証です）。
- **モデル**：下の表のファイル。このリポジトリには入っていないので、配布元から取得してください。

## モデル

配布元は [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)（Hugging Face）です。ファイル名のリンクから直接ダウンロードできます。

| ファイル | 置き場所（ComfyUI/models/ の中） | 大きさ | 使うワークフロー |
|---|---|---|---|
| [qwen_image_2.1_bf16.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_bf16.safetensors) | `diffusion_models` | 約14GB | A・B・C |
| [qwen3vl_8b_bf16.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3vl_8b_bf16.safetensors) | `text_encoders` | 約18GB | A・B・C |
| [qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors) | `text_encoders` | 約9.5GB | A |
| [qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors) | `text_encoders` | 約9.5GB | B・C |
| [qwen_image_2.1_vae_bf16.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/vae/qwen_image_2.1_vae_bf16.safetensors) | `vae` | 約0.7GB | A・B・C |
| [qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/loras/qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors) | `loras` | 約0.9GB | A・B・C |

3本すべて使う場合は合計で約52GB、タイプAだけなら約43GBです。

## 使い方

1. このページ上のファイル一覧から JSON ファイルを開き、右上のダウンロードボタン（Download raw file）で保存します
2. 保存した JSON ファイルを ComfyUI の画面にドラッグ＆ドロップします
3. タイプB・C は、画像読み込みノード（① image_1、② image_2）で自分の画像を選びます。最初は動画で使ったサンプル画像の名前が入っていて、そのままだとエラーになります
4. プロンプトを書き換えて実行（Run / Queue Prompt）します。できた画像は ComfyUI の `output/QwenImage21/` の中に保存されます

- LoRA ノードは3つあります。LoRA 1 が Turbo LoRA（有効）、LoRA 2・3 は無効（紫色）です。ノードを選んで **Ctrl+B** で有効・無効を切り替えます。自分の LoRA を使うときは、Qwen-Image 用のものを `models/loras` に入れて LoRA 2・3 で選びます。
- ワークフロー内のメモには、動画で使った Google Colab 版の説明（Google ドライブの置き場所、「Colab を終了すると画像が消える」など）が残っています。自分の PC で使う場合は、上の表の置き場所に読み替えてください。

## 元にしたもの

- ComfyUI 公式テンプレート [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates)（MIT License）を元に、LoRA の差し込み口・メモなどを追加しています。

## 注意

- 動画の中で動作を確認したノートブックから、ワークフローの部分を取り出したものです。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・モデルの更新への対応はお約束できません。
