# ゴルフHILSセンサーユニット（M5StickC Plus2用ファームウェア）

このディレクトリは、M5StickC Plus2を用いたゴルフHILSシステムのセンサーユニット（ファームウェア）のソースコードを格納します。

---

## 概要

- **役割**  
  ゴルフスイング時の加速度・角速度などのデータをIMU（MPU6886）から取得し、クラブ種別やプレイヤー名などの入力情報とともにパケット化し、UARTまたはMQTT経由でシミュレーションユニット（Raspberry Pi等）へ送信します。

- **主な構成要素**
  - IMU（MPU6886）によるセンサデータ取得
  - ボタン入力によるクラブ種別・プレイヤー名選択
  - データのJSONパケット化
  - UART（USBシリアル）またはMQTT over Wi-Fiでの送信

---

## ディレクトリ構成例

```
sensor-firmware/
├── src/               # ソースコード（C/C++）
│   ├── SensorManager      # IMU制御
│   ├── InputManager       # ボタン処理
│   └── CommManager        # 通信・パケット生成
├── lib/               # 外部ライブラリ
├── platformio.ini      # ビルド設定例（PlatformIOの場合）
└── README.md
```

---

## 主要モジュール

- `/src/SensorManager`：IMU制御・データ取得
- `/src/InputManager`：ボタン入力監視・クラブ種別選択
- `/src/CommManager`：データパケット化・UART/MQTT送信

---

## サンプル：送信データ（C++/JSON over UART）

```cpp
struct SwingData {
    float accel_x, accel_y, accel_z;
    float gyro_x, gyro_y, gyro_z;
    uint8_t club_type; // 0=Driver, 1=Iron, ...
};
void sendSwing(const SwingData& d) {
    StaticJsonDocument<128> doc;
    doc["ax"] = d.accel_x;
    doc["ay"] = d.accel_y;
    doc["az"] = d.accel_z;
    doc["gx"] = d.gyro_x;
    doc["gy"] = d.gyro_y;
    doc["gz"] = d.gyro_z;
    doc["club"] = d.club_type;
    serializeJson(doc, Serial);
    Serial.println();
}
```

---

## 技術スタック

- マイコン: M5StickC Plus2（ESP32-PICO-V3-02）
- 言語: C/C++（Arduino Core for ESP32推奨）
- 通信: UART（USBシリアル）またはMQTT over Wi-Fi
- 開発環境: Arduino IDE, PlatformIO, UIFlow, MicroPython等

---

## 開発・運用

- **ブランチ戦略**  
  - `main`：リリース用
  - `develop`：結合テスト用
  - `feature/xxx`：機能別
  - `hotfix/xxx`：障害対応

- **CI/CD**  
  - GitHub Actionsでビルド＆ユニットテスト
  - リリース時はGitHub Releasesも活用

---

## 関連資料

- システム全体設計・API仕様は [`/README.md`](../README.md) および [`/docs`](../docs/) を参照してください。
- M5StickC Plus2の詳細仕様は [公式ドキュメント](https://docs.m5stack.com/ja/core/m5stickc_plus2) も参照してください。

---

## TODO

- **MicroPythonやUIFlowによる実装案**  
  - Arduino Core以外の開発環境にも対応検討
- **センサデータのキャリブレーション自動化**
- **MQTT通信の安定化・再接続処理**
- **外部センサ拡張（Grove端子利用）や音声・LEDフィードバック機能の追加**
- **Web UIやAPIサーバとの連携拡張も将来的に検討**

---

> 本READMEはプロジェクト全体READMEの内容を抜粋・要約しています。詳細はルートディレクトリのREADMEもご確認ください。