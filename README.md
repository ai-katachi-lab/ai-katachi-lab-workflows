# AIカタチラボ ワークフロー集

YouTube「AIカタチラボ」の動画で使った、[ComfyUI](https://github.com/comfyanonymous/ComfyUI) のワークフローと Colab ノートブックを無料で公開しています。動画ごとにフォルダを分けています。使い方は各フォルダの README を見てください。

## フォルダ一覧

| フォルダ | 中身 | 主に使うモデル | 動画 |
|---|---|---|---|
| [001_H3_I2V](001_H3_I2V) | 画像から音声つきの動画を作るワークフロー（I2V / L2V / FL2V） | MiniMax H3 | [1本目](https://youtu.be/Qqm-3XHxuH4) |
| [001_10Eros_Realism_Anime](001_10Eros_Realism_Anime) | 10Eros Max で動画を作るワークフロー（実写版・アニメ版） | MiniMax H3（10Eros Max） | [1本目](https://youtu.be/Qqm-3XHxuH4) |
| [002_10Eros_Turbo](002_10Eros_Turbo) | 高速化が入ったモデルで、7ステップほどで動画を作るワークフロー（I2V / T2V） | MiniMax H3（10Eros Max TURBO-hybrid） | [2本目](https://youtu.be/xrwEXFcKt_k) |
| [004_ForgeNeo](004_ForgeNeo) | Forge Neo を Google Colab で起動するノートブック（Anima 入り） | Anima 系（初期設定は anima-aesthetic-v1.1） | [4本目](https://youtu.be/_0a4ULyLpAQ) |
| [005_QwenImage21](005_QwenImage21) | 画像生成・画像編集・複数画像合成のワークフロー | Qwen-Image 2.1 | [5本目](https://youtu.be/bWXlMPHS9n0) |
| [006_H3_Extender_RefMod](006_H3_Extender_RefMod) | クリップをつないで長い動画にし、最後まで同じ顔を保つワークフロー | MiniMax H3（10Eros Max） | [6本目](https://youtu.be/oiusJ_s7w7M) |
| [008_H3_Finish](008_H3_Finish) | 作った動画の顔を直し、全体を高解像度にするワークフロー（顔を直す 実写・アニメ／全体を高解像度に） | MiniMax H3（10Eros Max ほか） | [8本目](https://youtu.be/mVo6Vim0Gpg) |

## モデルのライセンス

モデルはこのリポジトリに入っていません。各フォルダの README にある配布元から取得し、それぞれのライセンスにしたがって使ってください。

- **MiniMax H3 とその派生モデル（10Eros Max など）**：[MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)。生成した動画を公開するときは AI で作ったことを明示し、商用で使う場合は「MiniMax H3」の表示が必要です。地域や事業の規模によって条件が変わるので、使う前にライセンス本文を確認してください。
- **Anima**（004）：[CircleStone Labs Non-Commercial License](https://huggingface.co/circlestone-labs/Anima/blob/main/LICENSE.md)。非商用ライセンスです。
- **Qwen-Image 2.1**（005）：[Qwen RESEARCH LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE)。研究・評価のみで、商用利用はできません。
- **InsightFace buffalo_l**（008 の実写の顔の見分けに使用、ノードが自動で取得）：非商用の研究用です。

## このリポジトリのライセンス

このリポジトリのファイルは [MIT License](LICENSE) です。ほかの方のワークフローを元にしたものは、各フォルダの README に元にしたものとその著作権表示を書いています。カスタムノードや ComfyUI 本体は入っていないので、それぞれの配布元から入れてください。

## 注意

- どれも、動画の中で動作を確認したものを共有しています。
- 無保証です。使ったことで生じた損害について責任は負いません。
- 個別の使い方サポートや、ComfyUI・ノード・モデルの更新への対応はお約束できません。
