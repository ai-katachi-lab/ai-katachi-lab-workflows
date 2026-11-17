"""H3 一気通貫ワークフロー用の小さなノード（AIカタチラボ、MIT License）。

区画どうしを「ファイル」でつなぐので、使わない区画をバイパスしても、ほかの区画は動きます。
・H3FlowSeeds          … seed を1つ決めると、seed, seed+1, … を5つ出す（画像を何枚か作るとき用）
・H3FlowSaveSet        … ①の画像4枚・②-2 の動かす画像を「最新の組」として保存（前の組は archive に残す）
・H3FlowSetSheet       … これまでの組を新しい順に1枚の一覧画像にする
・H3FlowPick           … 「何回前の組か」と番号で1枚選ぶ（②-1・③で使う。②-2 の服・背景も同じ選び方）
・H3FlowSaveCharacter  … ②-1 でできた人物の手本5枚を、input/h3flow_character に保存（前の5枚は character_old に移す）
・H3FlowCharacterRefs  … 保存した人物の手本を、RefMod を作るノード（Create H3 RefMod）に渡す形で読む（②-1 で使う）
・H3FlowLatestVideo    … いちばん新しい「つないだ動画」「高解像度にした動画」を自動で読む（⑥・⑦ で使う）
・H3FlowCharacter      … input/h3flow_character から人物の手本を読む（②-2 で使う）
・H3FlowParts          … ②-2 で使う服・背景の画像を読む（①-2 で作った画像から番号で選ぶ／input/h3flow_parts の画像／使わない）
・H3FlowPromptSwitch   … プロンプト拡張を使うかどうかの切り替え（使わないときは拡張を動かさない）
"""
import datetime
import hashlib
import json
import os
import shutil
import time

import numpy as np
import torch
from PIL import Image, ImageOps

import folder_paths

HERE = os.path.dirname(os.path.abspath(__file__))
SET_SUBDIR = "h3flow_images"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
KINDS = {"t2i": "①の画像", "start": "動かす画像", "clothes": "①-2 の服の画像", "background": "①-2 の背景の画像"}
IMAGE_ASPECT = 1536 / 2688  # 一覧の縮小画像の縦横比（画像の大きさと同じ 4:7）
CHARACTER_NAMES = ["1_front", "2_left_3q", "3_right_3q", "4_left_profile", "5_right_profile"]
CHARACTER_LABELS = ["正面", "斜め左", "斜め右", "横左", "横右"]


def _config():
    try:
        with open(os.path.join(HERE, "config.json"), encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def _character_dir():
    return _config().get("character_dir") or os.path.join(folder_paths.get_input_directory(), "h3flow_character")


def _parts_dir():
    return _config().get("parts_dir") or os.path.join(folder_paths.get_input_directory(), "h3flow_parts")


def _set_dir(kind):
    return os.path.join(folder_paths.get_output_directory(), SET_SUBDIR, kind)


def _images_in(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.join(folder, f) for f in os.listdir(folder)
                  if f.lower().endswith(IMAGE_EXTS) and not f.startswith("."))


def _fingerprint(paths):
    digest = hashlib.sha256()
    for path in paths:
        try:
            stat = os.stat(path)
            digest.update(f"{path}|{stat.st_size}|{stat.st_mtime_ns}\n".encode("utf-8"))
        except OSError:
            digest.update(f"{path}|missing\n".encode("utf-8"))
    return digest.hexdigest()


def _load(path):
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        array = np.asarray(image).astype(np.float32) / 255.0
    return torch.from_numpy(array)[None, ...]


def _save(tensor, path):
    array = (tensor[0].detach().cpu().clamp(0, 1).numpy() * 255.0).round().astype(np.uint8)
    Image.fromarray(array).save(path, compress_level=4)


def _temp_preview(tensor, name):
    folder = os.path.join(folder_paths.get_temp_directory(), "h3flow")
    os.makedirs(folder, exist_ok=True)
    filename = f"{name}_{int(time.time() * 1000)}.png"
    _save(tensor, os.path.join(folder, filename))
    return {"filename": filename, "subfolder": "h3flow", "type": "temp"}


def _image_slots(count):
    return {f"image_{n}": ("IMAGE",) for n in range(1, count + 1)}


class H3FlowSeeds:
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("seed_1", "seed_2", "seed_3", "seed_4", "seed_5")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53 - 6, "control_after_generate": True})}}

    def run(self, seed):
        return tuple(int(seed) + n for n in range(5))


JST = datetime.timezone(datetime.timedelta(hours=9))
SHEET_MAX_SETS = 6  # 「これまでの組」に並べる組の数（新しい順）


def _sets(kind):
    """archive の画像を「組」（1回の実行でできた画像）ごとにまとめ、新しい順に返す。[(作った時刻, {番号: パス})]"""
    archive = os.path.join(_set_dir(kind), "archive")
    groups = {}
    for path in _images_in(archive):
        stem = os.path.splitext(os.path.basename(path))[0]
        key, _, number = stem.rpartition("_")
        if key and number.isdigit():
            groups.setdefault(key, {})[int(number)] = path
    ordered = sorted(groups.values(), key=lambda g: max(os.path.getmtime(p) for p in g.values()), reverse=True)
    return [(max(os.path.getmtime(p) for p in g.values()), g) for g in ordered]


def _when(mtime):
    return datetime.datetime.fromtimestamp(mtime, JST).strftime("%m/%d %H:%M")


class H3FlowSaveSet:
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"kind": (list(KINDS),)}, "optional": _image_slots(5)}

    def run(self, kind, **images):
        tensors = [images[f"image_{n}"] for n in range(1, 6) if images.get(f"image_{n}") is not None]
        if not tensors:
            raise ValueError(f"{KINDS[kind]}がつながっていません。")
        folder = _set_dir(kind)
        latest = os.path.join(folder, "latest")
        archive = os.path.join(folder, "archive")
        os.makedirs(latest, exist_ok=True)
        os.makedirs(archive, exist_ok=True)
        for old in _images_in(latest):
            os.remove(old)
        now = datetime.datetime.now(JST)
        stamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"  # 日本時間
        results = []
        for number, tensor in enumerate(tensors, start=1):
            name = f"{number}.png"
            _save(tensor[:1], os.path.join(latest, name))
            archived = f"{stamp}_{number}.png"
            shutil.copy2(os.path.join(latest, name), os.path.join(archive, archived))
            # 画面には時刻つきの控え（archive）を出す。latest/1.png は毎回同じ名前なので、ブラウザが前の画像を出してしまうため。
            results.append({"filename": archived, "subfolder": f"{SET_SUBDIR}/{kind}/archive", "type": "output"})
        print(f"[H3 一気通貫] {KINDS[kind]} {len(tensors)} 枚を保存しました（番号 1〜{len(tensors)}）。前の組は archive に残っています。")
        return {"ui": {"images": results}, "result": (stamp,)}


class H3FlowSetSheet:
    """これまでの組を、新しい順に1枚の一覧画像にする（左の数字＝「何回前の組か」、画像の下の数字＝番号）。"""
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"kind": (list(KINDS),)}, "optional": {"saved": ("STRING", {"forceInput": True})}}

    @staticmethod
    def _font(size):
        from PIL import ImageFont
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    def run(self, kind, saved=None):
        from PIL import ImageDraw
        sets = _sets(kind)[:SHEET_MAX_SETS]
        if not sets:
            return {"ui": {"text": [f"{KINDS[kind]}はまだありません。"]}}
        thumb_h, gap, label_w = 280, 12, 200
        thumb_w = round(thumb_h * IMAGE_ASPECT)
        columns = max(max(g) for _, g in sets)
        width = label_w + columns * (thumb_w + gap) + gap
        row_h = thumb_h + 56
        sheet = Image.new("RGB", (width, len(sets) * row_h + gap), (32, 32, 32))
        draw = ImageDraw.Draw(sheet)
        big, small = self._font(56), self._font(26)
        for row, (mtime, group) in enumerate(sets):
            y = gap + row * row_h
            if row:
                draw.line([(0, y - gap // 2), (width, y - gap // 2)], fill=(90, 90, 90), width=2)
            draw.text((24, y + 20), str(row), fill=(255, 200, 80), font=big)
            draw.text((24, y + 100), "latest" if row == 0 else f"{row} back", fill=(220, 220, 220), font=small)
            draw.text((24, y + 136), _when(mtime), fill=(220, 220, 220), font=small)
            for number in range(1, columns + 1):
                x = label_w + (number - 1) * (thumb_w + gap)
                path = group.get(number)
                if path:
                    with Image.open(path) as image:
                        thumb = ImageOps.fit(image.convert("RGB"), (thumb_w, thumb_h))
                    sheet.paste(thumb, (x, y))
                draw.text((x + thumb_w // 2 - 8, y + thumb_h + 8), str(number), fill=(255, 255, 255), font=small)
        folder = os.path.join(folder_paths.get_temp_directory(), "h3flow")
        os.makedirs(folder, exist_ok=True)
        filename = f"sheet_{kind}_{int(time.time() * 1000)}.png"
        sheet.save(os.path.join(folder, filename), compress_level=4)
        return {"ui": {"images": [{"filename": filename, "subfolder": "h3flow", "type": "temp"}]}}


class H3FlowPick:
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "kind": (list(KINDS),),
            "sets_back": ("INT", {"default": 0, "min": 0, "max": 999,
                                  "tooltip": "何回前の組か。0＝いちばん新しい組、1＝その1つ前の組…（「これまでの組」の左の大きい数字）"}),
            "number": ("INT", {"default": 1, "min": 1, "max": 5, "tooltip": "その組の中の番号（左から 1, 2, …）"}),
        }}

    @staticmethod
    def _path(kind, sets_back, number):
        sets = _sets(kind)
        if not sets:
            raise ValueError(f"{KINDS[kind]}がまだありません。先にその区画を実行してください。")
        if sets_back >= len(sets):
            raise ValueError(f"{sets_back} 回前の組はありません（いまあるのは 0〜{len(sets) - 1}）。sets_back を直してください。")
        mtime, group = sets[sets_back]
        if number not in group:
            raise ValueError(f"その組に {number} 番はありません（1〜{max(group)} 番）。number を直してください。")
        return group[number], mtime

    @classmethod
    def IS_CHANGED(cls, kind, sets_back, number):
        try:
            return _fingerprint([cls._path(kind, sets_back, number)[0]])
        except ValueError as exc:
            return str(exc)

    def run(self, kind, sets_back, number):
        path, mtime = self._path(kind, sets_back, number)
        which = "いちばん新しい組" if sets_back == 0 else f"{sets_back} 回前の組"
        info = f"{KINDS[kind]}：{which}（{_when(mtime)} 作成）の {number} 番を使います"
        print(f"[H3 一気通貫] {info}")
        image = _load(path)
        # 選んだ1枚をこのノードの上に表示する（どれを使うか目で確かめられるように）。
        return {"ui": {"images": [_temp_preview(image, f"pick_{kind}_{number}")]}, "result": (image, info)}


class H3FlowSaveCharacter:
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved",)
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}, "optional": _image_slots(5)}

    def run(self, **images):
        tensors = [(n, images.get(f"image_{n}")) for n in range(1, 6)]
        tensors = [(n, t) for n, t in tensors if t is not None]
        if not tensors:
            raise ValueError("人物の手本がつながっていません。")
        folder = _character_dir()
        os.makedirs(folder, exist_ok=True)
        old = _images_in(folder)
        if old:
            backup = os.path.join(os.path.dirname(folder), "character_old", time.strftime("%Y%m%d_%H%M%S"))
            os.makedirs(backup, exist_ok=True)
            for path in old:
                shutil.move(path, os.path.join(backup, os.path.basename(path)))
            print(f"[H3 一気通貫] 前の人物の手本 {len(old)} 枚を {backup} に移しました（消していません）。")
        previews = []
        for n, tensor in tensors:
            _save(tensor[:1], os.path.join(folder, f"{CHARACTER_NAMES[n - 1]}.png"))
            previews.append(_temp_preview(tensor[:1], CHARACTER_NAMES[n - 1]))
        print(f"[H3 一気通貫] 人物の手本 {len(tensors)} 枚を {folder} に保存しました。続けて RefMod を作ります。")
        return {"ui": {"images": previews}, "result": (str(time.time()),)}


class H3FlowCharacterRefs:
    """保存した人物の手本を、Create H3 RefMod の refs_bundle に渡す形で読む。
    「保存した」の線をつなぐので、必ず人物の手本の保存が終わってから読みます。"""
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("H3_REF_LIST", "STRING")
    RETURN_NAMES = ("refs_bundle", "info")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "saved": ("STRING", {"forceInput": True}),
            "max_edge": ("INT", {"default": 2048, "min": 256, "max": 4096, "step": 64,
                                 "tooltip": "読み込むときの長い辺の上限（px）。RefMod を作る大きさは Create H3 RefMod の ref_resolution で決まります"}),
        }}

    def run(self, saved, max_edge):
        import nodes as comfy_nodes
        loader = comfy_nodes.NODE_CLASS_MAPPINGS.get("MiniMaxH3RefModFolderLoader")
        if loader is None:
            raise RuntimeError("RefMod のノード（ComfyUI-MiniMaxH3Mod）が入っていません。ComfyUI-MiniMaxH3Mod を custom_nodes に入れてください。")
        paths = _images_in(_character_dir())[:5]
        if not paths:
            raise ValueError(f"人物の手本がありません（{_character_dir()}）。")
        refs, count = loader().load(_character_dir(), max_items=len(paths), max_frames=2, max_edge=max_edge)
        info = f"RefMod に使う人物の手本 {len(paths)} 枚：" + "、".join(os.path.basename(p) for p in paths)
        print(f"[H3 一気通貫] {info}")
        return (refs, info)


VIDEO_KINDS = {"つないだ動画（⑤）": "h3ps_joined", "高解像度にした動画（⑥）": "h3flow_finish/Upsampled"}


class H3FlowLatestVideo:
    """⑤ でつないだ動画・⑥ で高解像度にした動画のうち、いちばん新しい1本を読む。
    ComfyUI の input/h3flow_finish/ に写してから使います（⑦ は input の外を読まない設定のため）。"""
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("VIDEO", "STRING", "STRING")
    RETURN_NAMES = ("video", "path", "info")
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"kind": (list(VIDEO_KINDS), {"tooltip": "どの動画を読むか"})}}

    @staticmethod
    def _newest(kind):
        folder = os.path.join(folder_paths.get_output_directory(), VIDEO_KINDS[kind])
        if not os.path.isdir(folder):
            return None
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".mp4") and not f.startswith(".")]
        return max(files, key=os.path.getmtime) if files else None

    @classmethod
    def IS_CHANGED(cls, kind):
        path = cls._newest(kind)
        return _fingerprint([path]) if path else "missing"

    def run(self, kind):
        path = self._newest(kind)
        if not path:
            before = "⑤ つなぐ" if kind.startswith("つないだ") else "⑥ 高解像度に"
            raise ValueError(f"{kind}がまだありません。先に {before} を実行してください。")
        target_dir = os.path.join(folder_paths.get_input_directory(), "h3flow_finish")
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, os.path.basename(path))
        if not (os.path.isfile(target) and os.path.getsize(target) == os.path.getsize(path)):
            shutil.copy2(path, target)
        info = f"{kind}：{os.path.basename(path)}（{_when(os.path.getmtime(path))} 作成）を使います"
        print(f"[H3 一気通貫] {info}")
        from comfy_api.latest import InputImpl
        return {"ui": {"text": [info]}, "result": (InputImpl.VideoFromFile(target), target, info)}


class H3FlowCharacter:
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("image_1", "image_2", "image_3", "image_4", "image_5", "info")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    @classmethod
    def IS_CHANGED(cls):
        return _fingerprint(_images_in(_character_dir()))

    def run(self):
        paths = _images_in(_character_dir())[:5]
        if not paths:
            raise ValueError(f"人物の手本がありません（{_character_dir()}）。先に ②-1 を実行してください。")
        tensors = [_load(p) for p in paths] + [None] * (5 - len(paths))
        info = f"人物の手本 {len(paths)} 枚：" + "、".join(os.path.basename(p) for p in paths)
        print(f"[H3 一気通貫] {info}")
        return tuple(tensors) + (info,)


PART_FROM_SET = "①-2 で作った画像"
PART_FROM_FOLDER = "input/parts の画像"
PART_NONE = "使わない"
PART_SOURCES = [PART_FROM_SET, PART_FROM_FOLDER, PART_NONE]
PART_LABELS = {"clothes": "服", "background": "背景"}


class H3FlowParts:
    """②-2 で使う服・背景の画像を1枚ずつ決める。①-2 の「これまでの組」から番号で選ぶか、input/parts の画像を使う。"""
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("clothes", "background", "info")
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        required = {}
        for part, label in PART_LABELS.items():
            required[f"{part}_from"] = (PART_SOURCES, {"default": PART_FROM_SET,
                                                       "tooltip": f"{label}の画像をどこから使うか（①-2 で作った画像／input/h3flow_parts の {part} の画像／使わない）"})
            required[f"{part}_sets_back"] = ("INT", {"default": 0, "min": 0, "max": 999,
                                                     "tooltip": f"①-2 の「{label}のこれまでの組」の左の大きい数字（0＝いちばん新しい組）"})
            required[f"{part}_number"] = ("INT", {"default": 1, "min": 1, "max": 5, "tooltip": "その組の中の番号（左から 1, 2, …）"})
        return {"required": required}

    @staticmethod
    def _find(stem):
        for path in _images_in(_parts_dir()):
            if os.path.splitext(os.path.basename(path))[0].lower() == stem:
                return path
        return None

    @classmethod
    def _resolve(cls, part, source, sets_back, number):
        """(パス, 説明) を返す。使わないときは (None, 説明)。"""
        label = PART_LABELS[part]
        if source == PART_NONE:
            return None, f"{label}：使いません"
        if source == PART_FROM_FOLDER:
            path = cls._find(part)
            if not path:
                return None, f"{label}：input/parts に {part} の画像がないので使いません"
            return path, f"{label}（input/parts の {os.path.basename(path)}）"
        try:
            path, mtime = H3FlowPick._path(part, sets_back, number)
        except ValueError as exc:
            raise ValueError(f"{label}：{exc} 使わないときは {part}_from を「{PART_NONE}」にしてください。") from None
        which = "いちばん新しい組" if sets_back == 0 else f"{sets_back} 回前の組"
        return path, f"{label}（①-2 の{which}・{_when(mtime)} 作成の {number} 番）"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        paths = _images_in(_parts_dir()) + _images_in(_character_dir())
        for part in PART_LABELS:
            try:
                path, _ = cls._resolve(part, kwargs[f"{part}_from"], kwargs[f"{part}_sets_back"], kwargs[f"{part}_number"])
                paths += [path] if path else []
            except ValueError as exc:
                return str(exc)
        return _fingerprint(paths) + json.dumps(kwargs, sort_keys=True, ensure_ascii=False)

    def run(self, **kwargs):
        count = min(5, len(_images_in(_character_dir())))
        lines = [f"Picture 1〜{count}：人物の手本"] if count else []
        number = count
        images, previews = {}, []
        for part in PART_LABELS:
            path, text = self._resolve(part, kwargs[f"{part}_from"], kwargs[f"{part}_sets_back"], kwargs[f"{part}_number"])
            if path:
                number += 1
                lines.append(f"Picture {number}：{text}")
                images[part] = _load(path)
                previews.append(_temp_preview(images[part], f"part_{part}"))
            else:
                lines.append(text)
        info = "\n".join(lines)
        print("[H3 一気通貫] " + info.replace("\n", " / "))
        # 選んだ服・背景をこのノードの上に表示する（どれを使うか目で確かめられるように）。
        return {"ui": {"images": previews},
                "result": (images.get("clothes"), images.get("background"), info)}


class H3FlowPromptSwitch:
    CATEGORY = "H3 一気通貫"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "use_expansion": ("BOOLEAN", {"default": True, "tooltip": "オン：プロンプト拡張で書き足した文章を使う／オフ：書いたテキストをそのまま使う"}),
                "text": ("STRING", {"forceInput": True}),
            },
            "optional": {"expanded": ("STRING", {"forceInput": True, "lazy": True})},
        }

    def check_lazy_status(self, use_expansion, text, expanded=None):
        return ["expanded"] if use_expansion and expanded is None else []

    def run(self, use_expansion, text, expanded=None):
        if use_expansion:
            if not (expanded or "").strip():
                raise ValueError("プロンプト拡張の結果が空でした。もう一度「実行する」を押すか、use_expansion をオフにしてください。")
            return (expanded.strip(),)
        if not (text or "").strip():
            raise ValueError("テキストが空です。")
        return (text.strip(),)


NODE_CLASS_MAPPINGS = {
    "H3FlowSeeds": H3FlowSeeds,
    "H3FlowSaveSet": H3FlowSaveSet,
    "H3FlowSetSheet": H3FlowSetSheet,
    "H3FlowPick": H3FlowPick,
    "H3FlowSaveCharacter": H3FlowSaveCharacter,
    "H3FlowCharacter": H3FlowCharacter,
    "H3FlowCharacterRefs": H3FlowCharacterRefs,
    "H3FlowLatestVideo": H3FlowLatestVideo,
    "H3FlowParts": H3FlowParts,
    "H3FlowPromptSwitch": H3FlowPromptSwitch,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "H3FlowSeeds": "seed（5つ）",
    "H3FlowSaveSet": "できた画像を保存（最新の組）",
    "H3FlowSetSheet": "これまでの組（新しい順）",
    "H3FlowPick": "番号で1枚選ぶ",
    "H3FlowSaveCharacter": "人物の手本を保存（input/h3flow_character）",
    "H3FlowCharacter": "人物の手本を読む（input/h3flow_character）",
    "H3FlowCharacterRefs": "人物の手本を RefMod 用に読む",
    "H3FlowLatestVideo": "いちばん新しい動画を読む（⑤・⑥ の出力）",
    "H3FlowParts": "服・背景の画像を選ぶ（①-2 の画像／input/h3flow_parts）",
    "H3FlowPromptSwitch": "プロンプト拡張を使う／使わない",
}
