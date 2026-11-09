#!/usr/bin/env python3
"""PostToolUse hook: herdr-mods 配下の Mod を編集したとき、storybook.json とモックの同期を促す。

契約: ~/Projects/herdr-mods/ModsStoryBook/STORYBOOK.md
- herdr-mods/<Mod>/ 直下の *.js(mock.js と *.d.ts を除く)を Edit/Write した直後だけ動く。
- 画面を持たない Mod は ~/Projects/herdr-mods/hooks/storybook-exempt に名前を書く。
- 出力は additionalContext(Claude への注意)のみ。編集は止めない。
- 同じ Mod への注意は、storybook.json が更新されない限り 10 分に 1 回まで。
"""
import json, os, re, sys, time

ROOT = os.path.realpath(os.path.expanduser("~/Projects/herdr-mods"))
HOOKS = os.path.dirname(os.path.realpath(__file__))
THROTTLE = 600

def emit(msg):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}, ensure_ascii=False))

def exempt():
    try:
        return {l.strip() for l in open(os.path.join(HOOKS, "storybook-exempt")) if l.strip() and not l.startswith("#")}
    except FileNotFoundError:
        return set()

def validate(path):
    """契約(STORYBOOK.md §1)に反する点を列挙。"""
    try:
        d = json.load(open(path))
    except Exception as e:
        return [f"storybook.json が読めません: {e}"]
    errs, seen = [], set()
    if d.get("version") != 1:
        errs.append('"version": 1 がありません')
    for i, s in enumerate(d.get("states", [])):
        k = s.get("key")
        if not k: errs.append(f"states[{i}] に key がありません"); continue
        if k in seen: errs.append(f"key が重複: {k}")
        seen.add(k)
        if s.get("kind") not in ("radio", "switch"): errs.append(f"{k}: kind は radio か switch")
        if "default" not in s: errs.append(f"{k}: default が必須")
        if s.get("kind") == "radio":
            vals = [o.get("value") for o in s.get("options", [])]
            if not vals: errs.append(f"{k}: radio には options が必要")
            elif s.get("default") not in vals: errs.append(f"{k}: default が options にありません")
    return errs

def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return
    fp = (ev.get("tool_input") or {}).get("file_path")
    if not fp:
        return
    fp = os.path.realpath(fp)
    if not fp.startswith(ROOT + os.sep):
        return
    parts = fp[len(ROOT) + 1:].split(os.sep)
    if len(parts) != 2:
        return
    mod, fn = parts
    if mod in exempt() or mod == "hooks" or not fn.endswith(".js") or fn == "mock.js":
        return
    mdir = os.path.join(ROOT, mod)
    if not os.path.isfile(os.path.join(mdir, "mod.json")):
        return
    sb = os.path.join(mdir, "storybook.json")
    spec = "~/Projects/herdr-mods/ModsStoryBook/STORYBOOK.md"

    if not os.path.isfile(sb):
        emit(f"[storybook] {mod} に storybook.json がありません。{spec} の契約に従い、描画を変える状態(入力)を "
             f"storybook.json に列挙し、モックデータ(main.js 内の MOCK)と storybook() の読み取りも作ってください。")
        return
    errs = validate(sb)
    if errs:
        emit(f"[storybook] {mod}/storybook.json が契約に反しています: " + " / ".join(errs) + f"。({spec})")
        return
    # 旧契約(v1)の読み取りが残っていないか(契約 v2: STORYBOOK.md §5)
    legacy = []
    for f in ("main.js", "mock.js"):
        try:
            src = open(os.path.join(mdir, f)).read()
        except OSError:
            continue
        src = re.sub(r"(?m)^\s*//.*$|(?<=\s)//.*$", "", src)  # コメント内の旧記述は無視
        if re.search(r"shared\(\s*[`\"']storybook:[^`\"']*[`\"']\s*\)", src) and not re.search(r"props\(\)\??\.storybook", src):
            legacy.append(f"{f}: 固定キー shared(\"storybook:<mod>\") を読んでいます")
        if re.search(r"\bs\??\.mock\b", src):
            legacy.append(f"{f}: 廃止された mock フラグ(s.mock)を参照しています")
    if legacy:
        emit(f"[storybook] {mod} に旧契約(v1)の読み取りが残っています: " + " / ".join(legacy) +
             f"。契約 v2 では props().storybook のプレビューIDで読みます。{spec} の「3. 読み取り」の正本に helper を差し替えてください。")
        return
    # 状態の構造が変わった可能性: storybook.json がこの編集より古いとき、間隔を空けて 1 度だけ促す。
    if os.path.getmtime(sb) >= os.path.getmtime(fp):
        return
    stamp = os.path.join("/tmp", f"storybook-sync-{ev.get('session_id', 'x')}-{mod}")
    try:
        last = os.path.getmtime(stamp)
    except FileNotFoundError:
        last = 0
    if last > os.path.getmtime(sb) and time.time() - last < THROTTLE:
        return
    open(stamp, "w").close()
    emit(f"[storybook] {mod}/{fn} を編集しました。状態(描画を変える入力)の構造が増減・変更した場合は、"
         f"storybook.json と main.js 内のモックを同時に更新してください。変わっていなければ対応は不要です。({spec})")

main()
