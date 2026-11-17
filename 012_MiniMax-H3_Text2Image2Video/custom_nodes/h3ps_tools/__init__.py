"""PrefixStream 用の小さなノード（AIカタチラボ）。MIT License.

・H3PSPromptByClip  … 「クリップNのプロンプト（ここに貼る）」をまとめ、素材箱から「次は何本目か」を数えて自動で選ぶ。
                      1本目は冒頭の1行（Picture 1 …）を足し、続きのクリップでは外す
・H3PSDownloadClip  … 素材箱に入った1本（動画＋途中の状態ファイル）をパソコンにダウンロードするボタン
・H3PSJoinChain     … 選んだクリップまでの流れ（親をたどる）を1本の動画につなぐ
・素材箱の「続ける元」ノード（MiniMaxClipBinPicker）を Run のたびに読み直させる（2回目の Run で作られない不具合の対策）
・決めた本数（プロンプト欄をつないだ数）まで流れがつながったら、次の Run は自動で新しい流れの1本目にする（latest のときだけ）
・RefMod が選ばれていない（(none)・オフ）ときは、止めずに「今回使うプロンプト」の欄に注意を出す
"""
import json
import os
import subprocess
import time

import folder_paths
from aiohttp import web
from server import PromptServer

ALIGN_LINE = "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."
INITIAL_ID = "[INITIAL_GENERATION]"
BIN_SUBDIR = "minimax_h3_bins"


def _is_initial(clip_id):
    text = (clip_id or "").strip()
    return (not text) or text == INITIAL_ID


def _bins_root():
    return os.path.join(folder_paths.get_output_directory(), BIN_SUBDIR)


def _safe_name(text):
    return "".join(c for c in (text or "") if c.isalnum() or c in ("_", "-", " ")).strip()


def _project_dir(project_name):
    name = _safe_name(project_name) or "Default_Project"
    return os.path.join(_bins_root(), name), name


def _read_meta(clip_dir):
    try:
        with open(os.path.join(clip_dir, "meta.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _list_clips(project_name):
    pdir, _ = _project_dir(project_name)
    if not os.path.isdir(pdir):
        return []
    clips = []
    for name in os.listdir(pdir):
        cdir = os.path.join(pdir, name)
        if os.path.isdir(cdir) and os.path.isfile(os.path.join(cdir, "meta.json")):
            clips.append((os.path.getmtime(os.path.join(cdir, "meta.json")), name, cdir))
    clips.sort()
    return clips


def _find_clip(project_name, selection):
    clips = _list_clips(project_name)
    if not clips:
        raise ValueError(f"素材箱「{project_name}」にクリップがありません。先に動画のワークフローで1本作ってください。")
    sel = (selection or "latest").strip()
    if sel in ("", "latest"):
        return clips[-1][1], clips[-1][2]
    for _, name, cdir in clips:
        if name == sel or _read_meta(cdir).get("shot_tag") == sel:
            return name, cdir
    raise ValueError(f"素材箱「{project_name}」に「{sel}」というクリップが見つかりません。")


def _files_for(project_name, clip_id):
    _, pname = _project_dir(project_name)
    cdir = os.path.join(_bins_root(), pname, clip_id)
    files = []
    for fname in sorted(os.listdir(cdir)):
        if fname.startswith("video.") or fname == "latent.safetensors":
            files.append({
                "filename": fname,
                "subfolder": f"{BIN_SUBDIR}/{pname}/{clip_id}",
                "type": "output",
                "save_as": f"{pname}_{clip_id}_{fname}",
                "size_mb": round(os.path.getsize(os.path.join(cdir, fname)) / 1024 ** 2, 1),
            })
    return files


def _align_prompt(text, source_clip_id):
    text = (text or "").strip()
    first_line, _, rest = text.partition("\n")
    has_align = "is fully referenced" in first_line
    if _is_initial(source_clip_id):
        if not has_align:
            text = ALIGN_LINE + "\n\n" + text
    elif has_align:
        text = rest.lstrip("\n")
    return text


def _chain_length(project_name, clip_id):
    """clip_id までの流れ（親をたどる）が何本か。"""
    if _is_initial(clip_id):
        return 0
    pdir, _ = _project_dir(project_name)
    try:
        current, _ = _find_clip(project_name, clip_id)
    except ValueError:
        current = clip_id
    count, seen = 0, set()
    while current and not _is_initial(current) and current not in seen:
        seen.add(current)
        count += 1
        current = _read_meta(os.path.join(pdir, current)).get("parent_clip_id")
    return count


PROMPT_SLOTS = 10
AUTO_LABEL = "自動（素材箱から数える）"

# Run のたびに _on_prompt で決める値（このワークフローの「何本で1つの流れか」と RefMod の状態）
_RUN_STATE = {"chain_limit": 0, "refmod_warning": "", "new_chain_from": None}


class H3PSPromptByClip:
    CATEGORY = "H3 PrefixStream"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "info")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "project_name": ("STRING", {"default": "my_video"}),
            "use_clip": ([AUTO_LABEL] + [f"{n}本目" for n in range(1, PROMPT_SLOTS + 1)], {
                "default": AUTO_LABEL,
                "tooltip": "ふだんは自動。素材箱の「続ける元」までの本数＋1 のプロンプトを使います。"}),
        }
        optional = {"source_clip_id": ("STRING", {"forceInput": True})}
        for n in range(1, PROMPT_SLOTS + 1):
            optional[f"prompt_{n}"] = ("STRING", {"forceInput": True})
        return {"required": required, "optional": optional}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # 注意の文を毎回出し直すため

    def run(self, project_name, use_clip, source_clip_id=None, **prompts):
        if use_clip == AUTO_LABEL:
            number = _chain_length(project_name, source_clip_id) + 1
        else:
            number = int(use_clip.replace("本目", ""))
        if number > PROMPT_SLOTS:
            raise ValueError(f"次は{number}本目ですが、プロンプトは{PROMPT_SLOTS}本目までです。use_clip で使うプロンプトを選んでください。")
        text = (prompts.get(f"prompt_{number}") or "").strip()
        if not text:
            raise ValueError(
                f"次は{number}本目ですが、「クリップ{number}のプロンプト（ここに貼る）」が空です（またはこの本数版に欄がありません）。"
                f"プロンプト作りの「クリップ{number}のプロンプト（できあがり）」を貼るか、本数の多い版のワークフローを開いてください。")
        if number == 1 and not _is_initial(source_clip_id):
            print("[PrefixStream] 注意：1本目のプロンプトですが、素材箱の続きから作ります。")
        text = _align_prompt(text, source_clip_id)
        start = "最初の画像から" if _is_initial(source_clip_id) else f"{source_clip_id} の続きから"
        info = f"{number}本目のプロンプトを使います（{start}）"
        notes = []
        reset = _RUN_STATE.get("new_chain_from")
        if reset and _is_initial(source_clip_id):
            notes.append(f"前の流れが {reset[1]} 本そろったので、新しい流れの1本目を動かす画像から作ります（{reset[0]} の続きにはしません）。")
        if _RUN_STATE.get("refmod_warning"):
            notes.append(_RUN_STATE["refmod_warning"])
        if notes:
            info = "\n".join("⚠ " + n for n in notes) + "\n" + info
        print("[PrefixStream] " + info)
        return (text, info)


class H3PSDownloadClip:
    CATEGORY = "H3 PrefixStream"
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "my_video"}),
            },
            "optional": {
                "clip_id": ("STRING", {"forceInput": True}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def run(self, project_name, clip_id=None):
        if not clip_id or _is_initial(clip_id):
            clip_id, _ = _find_clip(project_name, "latest")
        files = _files_for(project_name, clip_id)
        videos = [{"filename": f["filename"], "subfolder": f["subfolder"], "type": "output"} for f in files if f["filename"].startswith("video.")]
        print(f"[PrefixStream] ダウンロード対象 {clip_id}: " + "、".join(f"{f['filename']}（{f['size_mb']} MB）" for f in files))
        return {"ui": {"images": videos, "animated": (bool(videos),), "h3ps_files": files}}


class H3PSJoinChain:
    CATEGORY = "H3 PrefixStream"
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "my_video"}),
                "last_clip": ("STRING", {"default": "latest", "tooltip": "つなぐ流れの最後のクリップ。latest＝一番新しいクリップ。素材箱の clip_id か shot_tag も書けます。"}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def run(self, project_name, last_clip):
        clip_id, cdir = _find_clip(project_name, last_clip)
        pdir, pname = _project_dir(project_name)
        chain = []
        seen = set()
        while clip_id and not _is_initial(clip_id) and clip_id not in seen:
            seen.add(clip_id)
            cdir = os.path.join(pdir, clip_id)
            meta = _read_meta(cdir)
            video = next((os.path.join(cdir, f) for f in sorted(os.listdir(cdir)) if f.startswith("video.")), None) if os.path.isdir(cdir) else None
            if not video:
                raise ValueError(f"クリップ {clip_id} の動画（video.mp4）が素材箱にありません。")
            chain.append((clip_id, video))
            clip_id = meta.get("parent_clip_id")
        chain.reverse()
        out_dir = os.path.join(folder_paths.get_output_directory(), "h3ps_joined")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{pname}_{len(chain)}clips_{time.strftime('%Y%m%d_%H%M%S')}.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for _, video in chain:
            cmd += ["-i", video]
        parts = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(len(chain)))
        cmd += ["-filter_complex", f"{parts}concat=n={len(chain)}:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # 音声のないクリップが混じっていたときは、映像だけでつなぎます。
            parts = "".join(f"[{i}:v:0]" for i in range(len(chain)))
            cmd2 = ["ffmpeg", "-y", "-loglevel", "error"]
            for _, video in chain:
                cmd2 += ["-i", video]
            cmd2 += ["-filter_complex", f"{parts}concat=n={len(chain)}:v=1:a=0[v]", "-map", "[v]",
                     "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", out_path]
            result2 = subprocess.run(cmd2, capture_output=True, text=True)
            if result2.returncode != 0:
                raise RuntimeError(f"動画をつなげませんでした: {result.stderr[-800:]} / {result2.stderr[-800:]}")
        report = f"{len(chain)} 本をつなぎました（古い順）：" + " → ".join(c for c, _ in chain)
        print("[PrefixStream] " + report)
        name = os.path.basename(out_path)
        entry = {"filename": name, "subfolder": "h3ps_joined", "type": "output"}
        files = [dict(entry, save_as=name, size_mb=round(os.path.getsize(out_path) / 1024 ** 2, 1))]
        return {"ui": {"images": [entry], "animated": (True,), "h3ps_files": files}}


@PromptServer.instance.routes.get("/h3ps/latest_files")
async def h3ps_latest_files(request):
    project = request.rel_url.query.get("project", "my_video")
    try:
        clip_id, _ = _find_clip(project, "latest")
        return web.json_response({"clip_id": clip_id, "files": _files_for(project, clip_id)})
    except Exception as exc:
        return web.json_response({"error": str(exc)}, status=404)


# ---- 素材箱の「続ける元」ノードを、Run のたびに必ず読み直させる ----
# MiniMaxClipBinPicker は設定（latest など）が前回と同じだと ComfyUI が結果を使い回し、
# 2回目の Run で新しいクリップが作られない。毎回読み直すよう IS_CHANGED を足す。
def _always_changed(cls, **kwargs):
    return float("nan")


def _wrap_pick(original):
    """latest で続けるとき、流れが決めた本数に達していたら、新しい流れの1本目（initial）にする。"""
    def pick(self, project_name="Default_Project", mode="Auto", filter_rating="All", clip_selection="latest",
             custom_clip_path="", **kwargs):
        args = dict(project_name=project_name, mode=mode, filter_rating=filter_rating, custom_clip_path=custom_clip_path, **kwargs)
        _RUN_STATE["new_chain_from"] = None
        result = original(self, clip_selection=clip_selection, **args)
        limit = _RUN_STATE.get("chain_limit") or 0
        sel = (clip_selection or "latest").strip().lower()
        if limit <= 0 or not str(mode).startswith("Auto") or sel not in ("latest", "", "0", "auto", "default") \
                or (custom_clip_path or "").strip():
            return result
        try:
            clip_id = result["result"][4]
        except Exception:
            return result
        if _is_initial(clip_id):
            return result
        length = _chain_length(project_name, clip_id)
        if length < limit:
            return result
        print(f"[PrefixStream] {clip_id} までで {length} 本そろっています（1つの流れは {limit} 本）。新しい流れの1本目を作ります。")
        _RUN_STATE["new_chain_from"] = (clip_id, length)
        return original(self, clip_selection="initial", **args)
    pick._h3ps_wrapped = True
    return pick


def _patch_clip_bin_picker():
    try:
        import nodes as comfy_nodes
    except Exception:
        return False
    patched = False
    for key in ("MiniMaxClipBinPicker", "MiniMaxClipBinTreePicker"):
        cls = comfy_nodes.NODE_CLASS_MAPPINGS.get(key)
        if cls is not None and not getattr(cls, "_h3ps_always_reload", False):
            cls.IS_CHANGED = classmethod(_always_changed)
            cls._h3ps_always_reload = True
            patched = True
        func_name = getattr(cls, "FUNCTION", None) if cls is not None else None
        func = getattr(cls, func_name, None) if func_name else None
        if func is not None and not getattr(func, "_h3ps_wrapped", False):
            setattr(cls, func_name, _wrap_pick(func))
            patched = True
    return patched


def _available_refmods():
    """いま選べる RefMod の名前（Load H3 RefMods の mod_1 の選択肢）。読めないときは None。"""
    try:
        import nodes as comfy_nodes
        loader = comfy_nodes.NODE_CLASS_MAPPINGS.get("MiniMaxH3RefModsLoader")
        if loader is None:
            return None
        types = loader.INPUT_TYPES()
        spec = (types.get("required") or {}).get("mod_1") or (types.get("optional") or {}).get("mod_1")
        choices = spec[0] if spec else None
        return set(choices) if isinstance(choices, (list, tuple)) else None
    except Exception:
        return None


def _read_run_state(prompt):
    """これから動かすワークフローから、1つの流れの本数と RefMod の状態を読む。"""
    limit, warning = 0, ""
    if not isinstance(prompt, dict):
        return limit, warning
    nodes = [n for n in prompt.values() if isinstance(n, dict)]
    by_class = lambda name: [n for n in nodes if n.get("class_type") == name]
    for node in by_class("H3PSPromptByClip"):
        inputs = node.get("inputs") or {}
        linked = [k for k, v in inputs.items() if k.startswith("prompt_") and isinstance(v, list)]
        limit = max(limit, len(linked))
    if limit and by_class("MiniMaxClipBinPicker") + by_class("MiniMaxClipBinTreePicker"):
        loaders = by_class("MiniMaxH3RefModsLoader")
        bridges = by_class("MiniMaxH3RefModContinuumBridge")
        mods, missing = [], []
        available = _available_refmods()
        for node in loaders:
            inputs = node.get("inputs") or {}
            for key, value in list(inputs.items()):
                if not (key.startswith("mod_") and isinstance(value, str)):
                    continue
                name = value.strip()
                if name and name != "(none)" and available is not None and name not in available:
                    # まだ作られていない RefMod の名前（②-1 を実行すると作られる）は、止めずに「なし」にして続けます。
                    missing.append(name)
                    inputs[key] = "(none)"
                    continue
                if name and name != "(none)":
                    mods.append(name)
        enabled = any((b.get("inputs") or {}).get("enable", True) is not False for b in bridges)
        if missing and not mods:
            warning = (f"RefMod「{'、'.join(missing)}」がまだありません（②-1 手本づくりを実行すると作られます）。"
                       "このまま RefMod なしで作ります。")
        elif not loaders or not mods:
            warning = "RefMod が選ばれていません（mod_1 が (none)）。このまま RefMod なしで作ります。使うときは「RefMod」ノードの mod_1 で選んでください。"
        elif bridges and not enabled:
            warning = "RefMod ON/OFF（enable）が false です。このまま RefMod なしで作ります。"
    return limit, warning


def _on_prompt(json_data):
    _patch_clip_bin_picker()  # 読み込み順で間に合わなかったときのため、実行の直前にも当てる
    try:
        limit, warning = _read_run_state(json_data.get("prompt"))
        _RUN_STATE["chain_limit"], _RUN_STATE["refmod_warning"] = limit, warning
        if warning:
            print("[PrefixStream] 注意: " + warning)
    except Exception as exc:
        print(f"[PrefixStream] 注意: 実行前の確認ができませんでした: {exc}")
    return json_data


_patch_clip_bin_picker()
try:
    PromptServer.instance.add_on_prompt_handler(_on_prompt)
except Exception as exc:
    print(f"[PrefixStream] 注意: 実行前の処理を登録できませんでした: {exc}")


NODE_CLASS_MAPPINGS = {
    "H3PSPromptByClip": H3PSPromptByClip,
    "H3PSDownloadClip": H3PSDownloadClip,
    "H3PSJoinChain": H3PSJoinChain,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "H3PSPromptByClip": "何本目かでプロンプトを自動で切り替え",
    "H3PSDownloadClip": "この1本をダウンロード（動画＋途中の状態）",
    "H3PSJoinChain": "クリップをつないだ動画を作る（流れをたどる）",
}
WEB_DIRECTORY = "./web"
