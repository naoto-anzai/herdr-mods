# herdr-mods

herdr-app の Mod を作るリポジトリ群。1 Mod = 1 リポジトリ = 1 space。

## 新しい Mod を作るとき
手で組み立てず、レシピを使う:

    ~/Projects/herdr-mods/layout-mine/recipes/mod-dev.sh <ModName>

これが次をまとめて行う(正本はこのスクリプト):
- `~/Projects/herdr-mods/<ModName>` を作る(git init, mod.json, main.js)
- `~/.config/herdr-app/mods/<ModName>` へ symlink を張る
- `<ModName>` の space を作り、左に Claude、右にその Mod の Mod ペインを開く

`--dry-run` を付けると実行内容だけ表示する。

## Story(モック)を必ず合わせる
画面を持つ Mod は、`storybook.json`(状態の一覧)と、`main.js` 内のモック(`storybook(mod)` と `MOCK`)を持つ。
モックは別ファイル(`mock.js`)にしない: mods-watcher がファイル単位で symlink するため、`./mock.js` の import は `herdr-app check` に「フォルダ外」と弾かれる。
契約の正本: `~/Projects/herdr-mods/ModsStoryBook/STORYBOOK.md`。

- 状態(描画を変える入力)が増えた・消えた・選択肢が変わったら、**同じ作業の中で** `storybook.json` と `main.js` 内のモックも直す。
- モックは Story が開いたプレビュー(ペイン)ごと。`props().storybook` が無いペインは常に本番(契約 v2)。読み取りは `main.js` の `storybook(mod)`(正本は STORYBOOK.md §3)を使い、旧 `mock` フラグは使わない。
- モック中は本番データ関数(`spaces()` など)と副作用のある呼び出し(`run()` `exec()` など)を使わない。
- 画面を持たない Mod(例: mods-watcher)は `~/Projects/herdr-mods/hooks/storybook-exempt` に名前を書いて対象外にする。
- `hooks/storybook-sync.py` が、Mod の `*.js` を編集した直後に同期の確認を促す(契約違反の `storybook.json` も指摘する)。
  登録は各 Mod の `.claude/settings.local.json`(git 管理外)だけ。ユーザー設定には入れない。recipe が新規 Mod に作る。
- 契約そのものを変えたくなったら、ModsStoryBook のセッションに相談する。

## 守ること
- 同梱 Mod / 同梱 layout は編集せず `mod.clone` / `layout.clone` で複製する。
- 変更後は `herdr-app check <mod>` と `herdr-app shot` で確認する。
- layout 切替・keys.json・space の並べ替えなど挙動が変わる操作は、実行前にユーザーへ報告する。
- layout は画面全体の枠で、space ごとのペイン構成ではない。ペイン構成は `pane.split` で作る(レシピ参照)。
- 詳細: `~/.config/herdr-app/AGENTS.md` と `herdr.d.ts`。
