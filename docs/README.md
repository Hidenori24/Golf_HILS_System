# 設計資料集

このディレクトリには本プロジェクトの設計資料・仕様書・API定義などを格納します。

---

## 運用ルール

- **ファイル命名規則**  
  `仕様書名_バージョン.md` 例: `system_architecture_v1.0.md`
- **ドキュメント構成**  
  1ファイル1テーマ（例：API仕様、システム構成、運用手順など）
- **更新履歴の記載**  
  各ドキュメント冒頭に「更新履歴」セクションを設けること
- **Markdown形式**  
  ドキュメントは原則Markdownで記述
- **図表の管理**  
  Mermaid記法や画像ファイル（`/docs/img/`配下）を活用
- **レビュー運用**  
  重要な設計変更はPull Requestでレビューを行う

---

## 例

- `system_overview_v1.0.md` … システム全体概要
- `api_spec_v1.1.md` … API仕様書
- `hardware_design_v1.0.md` … ハードウェア設計
- `operation_manual_v1.0.md` … 運用マニュアル

---

> 設計資料の追加・更新時は本READMEも適宜更