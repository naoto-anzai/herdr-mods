# herdr-mods

[Herdr](https://herdr.dev) (herdr-app) の Mod と、そのレイアウト・補助ツールを集めたリポジトリ。
1 Mod = 1 リポジトリで、ここではサブモジュールとして束ねる。

## Mod 一覧

| フォルダ | 内容 |
|---|---|
| `launcher` | 同梱 `new-menu` の複製。space/タブ/エージェントの起動メニュー |
| `spaces-tree` | 同梱 `spaces` の複製。同じ親フォルダの space をまとめて表示 |
| `machine-login` | 他マシンのログイン(パスワード入力)を扱う Mod |
| `github` | GitHub(PR など)を表示する Mod |
| `tree-canvas` | エージェントが描く木構造を、箱と線のグラフで表示する Mod と `htree` CLI |
| `md-viewer` | Markdown を表示する Mod(Files パネルへの反映を検討中) |
| `ModsStoryBook` | 各 Mod のモック(Story)を切り替えて確認する Mod。契約は `ModsStoryBook/STORYBOOK.md` |
| `mods-watcher` | 画面を持たない。Mod の変更を検知して Herdr に読み直させる |
| `layout-mine` | 上記の Mod を使う個人用レイアウトと、Mod 開発用の recipe |

`hooks/` は Mod 開発用の Claude Code hook(`storybook-sync.py`)。`CLAUDE.md` は、このフォルダで Mod を作るときの決まりごと。

## 取得

    git clone --recurse-submodules git@github.com:naoto-anzai/herdr-mods.git ~/Projects/herdr-mods

各 Mod を Herdr に読み込むには、`~/.config/herdr-app/mods/<name>` に実体を並べる(mods-watcher の `sync.sh` を使う)。
詳細は各 Mod の README を参照。
