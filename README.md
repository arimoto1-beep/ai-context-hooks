# ai-context-hooks

AIが原文へ戻るための索引メモ（context hook）を作る、軽量な実験キットです。

---

## 何を解決したいか

会議ログやメモをAIに読ませるとき、2つの問題があります。

**問題1：要約しすぎると、ニュアンスが消える**

- 迷い、違和感、将来含み、未決事項、却下案、設計懸念
- こうした情報は要約に残りにくい

**問題2：全文を毎回読ませると、重くてノイズも多い**

- AIが未決事項や雑談を決定事項として誤用する可能性がある
- コストと速度の問題もある

このリポジトリは、その中間を探ります。

---

## 基本思想

> **要約しない。ただし、探せるようにする。**

- AIに答えを渡すのではなく、**原文に戻るための入口**を渡す
- 索引メモは「結論」ではなく「どこに何があるかの目印」
- 断定しすぎず、原文確認を前提にする

---

## 何をしないか

| 目的 | このリポジトリ |
|------|---------------|
| 議事録ツール | ❌ 対象外（人間が読む整理資料は別途） |
| 自動要約ツール | ❌ 対象外（要約は情報を圧縮しすぎる） |
| RAG基盤そのもの | ❌ 対象外（検索・埋め込みは別レイヤー） |
| 索引メモの作成・レビュー実験 | ✅ これが目的 |

---

## ディレクトリ構成

```text
ai-context-hooks/
├─ README.md               このファイル
├─ docs/
│  ├─ concept.md           思想・設計方針
│  ├─ index_memo_format.md 索引メモの書き方
│  └─ examples.md          例と使い方の解説
├─ examples/
│  ├─ raw/
│  │  └─ 2026-06-14_meeting.md   サンプル会議ログ（原文）
│  └─ hooks/
│     ├─ ctx-20260614-001.md     サンプル索引メモ
│     └─ index.md                索引メモ一覧のサンプル
├─ prompts/
│  ├─ create_context_hook.md     索引メモを作成するプロンプト
│  ├─ review_context_hook.md     索引メモをレビューするプロンプト
│  └─ use_context_hook.md        索引メモを使って確認するプロンプト
├─ templates/
│  ├─ context_hook_template.md   索引メモのMarkdownテンプレート
│  └─ context_hook_template.yaml 索引メモのYAMLテンプレート
└─ tools/
   └─ validate_hooks.py          索引メモの簡易バリデーター
```
---

## 最初の使い方

1. **サンプルで流れを確認する**
   - `examples/raw/2026-06-14_meeting.md` で原文ログを見る
   - `examples/hooks/ctx-20260614-001.md` で対応する索引メモを見る
   - `examples/hooks/index.md` で索引メモの一覧を見る
   - topic / labels / confidence / source を使って、どの hook を参照すべきか確認する

2. **原文ログを用意する**
   - 会議ログ、Slackエクスポート、メモなどを `examples/raw/` に置く

3. **索引メモを作成する**
   - `prompts/create_context_hook.md` のプロンプトをAIに渡す
   - 原文と合わせて索引メモを生成する

4. **索引メモをレビューする**
   - `prompts/review_context_hook.md` のプロンプトで品質確認
   - 断定しすぎていないか、原文参照があるかを確認する

5. **索引メモを活用する**
   - `prompts/use_context_hook.md` のプロンプトで設計確認・タスク整理に使う

---

## サンプルを見る

- 原文ログ例（1議題）：[examples/raw/2026-06-14_meeting.md](examples/raw/2026-06-14_meeting.md)
- 原文ログ例（複数議題）：[examples/raw/2026-06-15_multi_topic_meeting.md](examples/raw/2026-06-15_multi_topic_meeting.md)
- 索引メモ例：[examples/hooks/ctx-20260614-001.md](examples/hooks/ctx-20260614-001.md)
- 索引メモ一覧例：[examples/hooks/index.md](examples/hooks/index.md)
- 詳しい解説：[docs/examples.md](docs/examples.md)

`examples/hooks/index.md` は、作成済みの context hook を一覧するためのサンプルです。索引メモが増えたときに、topic、labels、confidence、source などで横断的に確認するために使います。index はあくまで入口であり、仕様判断をする場合は必ず個別の hook と原文を確認してください。

---

## 注意事項

- **機密情報・個人情報・認証情報を入れない**
  - このリポジトリはGitHubで管理する前提。センシティブな情報は含めないこと。

- **外部情報と自分の意見を混同しない**
  - 索引メモに書く内容は、あくまで原文からの参照であること。

- **索引メモだけで仕様判断しない**
  - 索引メモは入口。最終的な判断は原文を確認してから行う。

---

## 関連ドキュメント

- [docs/concept.md](docs/concept.md) — なぜこのアプローチか
- [docs/index_memo_format.md](docs/index_memo_format.md) — 索引メモの書き方
- [docs/examples.md](docs/examples.md) — 具体例と使い方

---

## 索引メモの簡易チェック

`tools/validate_hooks.py` で、Markdown の索引メモに最低限必要な項目があるか確認できます。

```bash
python tools/validate_hooks.py examples/hooks/ctx-20260614-001.md
```

このバリデーターは項目の有無と confidence の値を簡易チェックするものです。内容の正しさ、安全性、機密情報の不在、AIによる誤用防止、仕様判断への利用可否は保証しません。

---

## index と hook の整合性チェック

`tools/validate_index.py` で、`examples/hooks/index.md` と各 hook ファイルの対応関係を簡易チェックできます。

```bash
python tools/validate_index.py examples/hooks/index.md examples/hooks
```

チェック内容：index に書かれた hook ファイルの存在、hook ファイルが index に載っているか、id / topic / labels / confidence の一致。

内容の正しさ、原文の妥当性、AIによる誤用防止は保証しません。
