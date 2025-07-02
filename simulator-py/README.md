# ゴルフHILSシミュレーションユニット（Python版）

このディレクトリは、Raspberry Pi上で動作するゴルフHILSシステムのシミュレーションユニット（Python実装）のソースコードを格納します。

---

## 概要

- **役割**  
  M5StickC Plus2から送信されるスイングデータ（UARTまたはMQTT経由）を受信し、弾道計算・シミュレーション・結果保存・ディスプレイ表示を行います。

- **主な構成要素**
  - データ受信（UART/MQTT）
  - 弾道シミュレーション（飛距離・角度・スピン等の計算）
  - 結果/履歴データの保存（SQLiteまたはCSV）
  - シミュレーション結果のディスプレイ表示（HDMIやタッチ液晶/Pygame/Matplotlib等）

---

## ディレクトリ構成例

```
simulator-py/
├── comm/              # 通信（UART/MQTT）受信モジュール
├── sim/               # 弾道計算・シミュレーションロジック
├── data/              # データ保存・履歴管理
├── disp/              # ディスプレイ描画
├── main.py            # エントリポイント
└── README.md
```

---

## 主要モジュール

- `/comm/CommListener`：シリアル/MQTT受信
- `/sim/SimulatorEngine`：弾道計算ロジック
- `/data/DataStore`：SQLite/CSV保存
- `/disp/DisplayManager`：シミュレーションと履歴結果の画面表示（Matplotlib, Pygame等）

---

## サンプル：データ受信（Python + pyserial）

```python
import serial, json
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
while True:
    line = ser.readline().decode().strip()
    if not line: continue
    data = json.loads(line)
    # data['ax'], data['gy'], data['club'] などを処理
```

---

## 技術スタック

- 言語: Python 3.x
- データベース: SQLiteまたはCSV
- 表示: Matplotlib, Pygame, Tkinter等

---

## 開発・運用

- **ブランチ戦略**  
  - `main`：リリース用
  - `develop`：結合テスト用
  - `feature/xxx`：機能別
  - `hotfix/xxx`：障害対応

- **CI/CD**  
  - GitHub ActionsでLint（flake8）＆ユニットテスト
  - リリース時はGitHub Releases + Dockerイメージ公開も検討

---

## 関連資料

- システム全体設計・API仕様は [`/README.md`](../README.md) および [`/docs`](../docs/) を参照してください。

---

## TODO

- **Python以外の実装案**  
  - TypeScript（Node.js）による実装も可能です。  
    - MQTTやシリアル通信は`mqtt.js`や`serialport`パッケージで対応
    - グラフ表示はElectronやWeb UI（React等）と連携も検討
  - C++による高速処理版や、Go/Rust等の他言語による実装も将来的に検討可能です。
  - Web UI拡張やAPIサーバ（Flask/Express）経由での外部連携も視野に入れています。

---

> 本READMEはプロジェクト全体READMEの内容を抜粋・要約しています。詳細はルートディレクトリのREADMEもご確認ください。