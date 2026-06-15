# Context Hooks Index

このファイルは、作成済みの context hook を一覧するためのサンプルです。

| id | topic | labels | confidence | source | hook |
|---|---|---|---|---|---|
| ctx-20260614-001 | CSV出力機能の扱い | out_of_scope, future_revisit, concern_seed, not_decision | medium | examples/raw/2026-06-14_meeting.md 00:12:01-00:13:30 | [examples/hooks/ctx-20260614-001.md](ctx-20260614-001.md) |
| ctx-20260615-001 | CSV出力機能の扱いと設計懸念 | out_of_scope, future_revisit, concern, not_decision | low | examples/raw/2026-06-15_multi_topic_meeting.md 00:03:10-00:06:20, 00:28:40-00:31:10 | [examples/hooks/ctx-20260615-001_csv_output.md](ctx-20260615-001_csv_output.md) |
| ctx-20260615-002 | エラー処理方針と設計書への反映事項 | open_issue, needs_follow_up, not_decision | medium | examples/raw/2026-06-15_multi_topic_meeting.md 00:10:30-00:18:44 | [examples/hooks/ctx-20260615-002_error_handling.md](ctx-20260615-002_error_handling.md) |
| ctx-20260615-003 | スケジュール遅延の可能性と確認事項 | schedule_risk, concern, task_candidate, not_decision | low | examples/raw/2026-06-15_multi_topic_meeting.md 00:18:45-00:23:29 | [examples/hooks/ctx-20260615-003_schedule_risk.md](ctx-20260615-003_schedule_risk.md) |
| ctx-20260615-004 | 顧客に確認が必要な未決事項 | customer_confirmation, open_issue, needs_follow_up | medium | examples/raw/2026-06-15_multi_topic_meeting.md 00:23:30-00:27:49 | [examples/hooks/ctx-20260615-004_customer_confirmation.md](ctx-20260615-004_customer_confirmation.md) |

## 使い方

- topic で関係しそうな hook を探す
- labels で決定 / 未決 / 懸念 / 対象外を見分ける
- confidence が低いものは、必ず原文を確認する
- source.ranges が複数ある hook は、どちらの箇所も原文を確認すること
- **index だけを見て仕様判断しない。必ず個別の hook と原文を確認すること**