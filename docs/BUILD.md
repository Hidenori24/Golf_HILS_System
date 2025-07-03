# ゴルフHILSシステム ビルド手順書

## 概要
このドキュメントは、ゴルフHILSシステムのセンサーファームウェアとシミュレーションソフトウェアの両方のビルドとセットアップ手順を提供します。

---

## 前提条件

### ハードウェア要件
- **センサーユニット**: M5StickC Plus2
- **シミュレーションユニット**: Raspberry Pi 4 Model B (4GB RAM推奨)
- **ディスプレイ**: HDMI対応モニター/TV
- **接続**: USB-C to USB-Aケーブル

### ソフトウェア要件
- **開発環境**: PlatformIO または Arduino IDE
- **オペレーティングシステム**: Raspberry Pi OS (64bit推奨)
- **Python**: 3.9以降

---

## センサーファームウェアのビルド

### 方法1: PlatformIOを使用 (推奨)

1. **PlatformIOのインストール**
   ```bash
   # PlatformIO Coreのインストール
   pip install platformio
   
   # またはVS Code拡張機能を使用
   # VS Codeで"PlatformIO IDE"拡張機能をインストール
   ```

2. **ビルドとアップロード**
   ```bash
   cd sensor-firmware/
   
   # ファームウェアのビルド
   pio run
   
   # M5StickC Plus2へのアップロード (USB-C接続)
   pio run --target upload
   
   # シリアル出力の監視
   pio device monitor
   ```

### 方法2: Arduino IDEを使用

1. **Arduino IDEのセットアップ**
   - Arduino IDE 2.0以降をインストール
   - ESP32ボードサポートを追加:
     - ファイル → 環境設定
     - 追加のボードマネージャーのURLに追加:
       `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - ツール → ボード → ボードマネージャーでESP32ボードをインストール

2. **ライブラリのインストール**
   - M5StickCPlus2ライブラリ
   - ArduinoJsonライブラリ
   - PubSubClientライブラリ

3. **コンパイルとアップロード**
   - `examples/golf_swing_monitor.ino`を開く
   - ボード選択: "M5Stick-C"
   - ポート選択: デバイスポート
   - アップロードをクリック

### 設定

メインスケッチの設定を編集:
```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER = "192.168.1.100";
```

---

## シミュレーションソフトウェアのセットアップ

### Raspberry Piのセットアップ

1. **自動セットアップ (推奨)**
   ```bash
   cd simulator-py/
   chmod +x setup_raspberry_pi.sh
   ./setup_raspberry_pi.sh
   ```

2. **手動セットアップ**
   ```bash
   # システムの更新
   sudo apt update && sudo apt upgrade -y
   
   # 依存関係のインストール
   sudo apt install -y python3 python3-pip python3-venv
   sudo apt install -y python3-numpy python3-scipy python3-matplotlib
   sudo apt install -y python3-pygame python3-serial sqlite3
   
   # 仮想環境の作成
   cd simulator-py/
   python3 -m venv venv
   source venv/bin/activate
   
   # Pythonパッケージのインストール
   pip install -r requirements.txt
   
   # ディレクトリの作成
   mkdir -p data/exports trajectories logs
   
   # シリアルアクセス用にユーザーをdialoutグループに追加
   sudo usermod -a -G dialout $USER
   ```

### 開発環境のセットアップ

他のプラットフォームでの開発用:

**Ubuntu/Debian:**
```bash
sudo apt install python3-dev python3-venv libatlas-base-dev
cd simulator-py/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**macOS:**
```bash
brew install python3
cd simulator-py/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
cd simulator-py\
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## システムの実行

### シミュレーションソフトウェアの開始

```bash
cd simulator-py/
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate     # Windows

# デフォルト設定で実行
python main.py

# カスタム設定で実行
python main.py --port /dev/ttyUSB0 --baud 115200 --display live

# ヘッドレスモードで実行
python main.py --display headless
```

### コマンドラインオプション

```
--port PORT         シリアルポート (デフォルト: /dev/ttyUSB0)
--baud BAUD         ボーレート (デフォルト: 115200)
--display MODE      表示モード: live, headless, both (デフォルト: live)
--log-level LEVEL   ログレベル: DEBUG, INFO, WARNING, ERROR (デフォルト: INFO)
```

### センサーユニットの開始

1. M5StickC Plus2の電源を入れる (Cボタンを2秒間長押し)
2. デバイスに「Golf HILS Sensor」と初期化状況が表示される
3. Aボタンでクラブ選択、Bボタンでプレイヤー選択
4. ゴルフスイングを行ってデータを生成

---

## テスト

### センサーファームウェアのテスト

```bash
cd sensor-firmware/
pio test
```

### シミュレーションソフトウェアのテスト

```bash
cd simulator-py/
source venv/bin/activate
pytest tests/ -v
```

### 統合テスト

1. シミュレーションソフトウェアを開始
2. センサーユニットをUSB接続
3. テストスイングを実行
4. データ受信と弾道計算を確認

---

## 使用例

### 弾道解析の例

```bash
cd simulator-py/
source venv/bin/activate
python examples/trajectory_analysis_example.py
```

これにより以下が実行されます:
- サンプルスイングデータの生成
- 複数のクラブタイプの解析
- 弾道可視化の作成
- データベースへの結果保存
- CSVへのデータエクスポート

---

## 設定

### センサー設定

`sensor-firmware/config/sensor_config.env`を編集:
```bash
WIFI_SSID=YOUR_NETWORK
WIFI_PASSWORD=YOUR_PASSWORD
MQTT_BROKER_IP=192.168.1.100
SWING_DETECTION_THRESHOLD=2.0
```

### シミュレーター設定

`simulator-py/config/simulator_config.yaml`を編集:
```yaml
serial:
  port: "/dev/ttyUSB0"
  baud_rate: 115200

display:
  mode: "live"
  screen_size: [1024, 768]

database:
  path: "golf_hils_data.db"
```

---

## トラブルシューティング

### よくある問題

**シリアルポートアクセス拒否:**
```bash
sudo usermod -a -G dialout $USER
# その後ログアウト・ログインを再実行
```

**M5StickC Plus2が検出されない:**
- USBケーブルを確認 (データ転送対応、充電専用でない)
- M5StickC Plus2のリセットボタンを押す
- 別のUSBポートを試す

**Raspberry Piでの表示問題:**
```bash
# GPUメモリ分割を有効化
sudo raspi-config
# Advanced Options → Memory Split → 128
```

**Pythonパッケージインストールエラー:**
```bash
# pipの更新
pip install --upgrade pip

# ビルド依存関係のインストール
sudo apt install python3-dev build-essential
```

### パフォーマンス最適化

**Raspberry Pi用:**
```bash
# GPUメモリの増加
echo "gpu_mem=128" | sudo tee -a /boot/config.txt

# 不要なサービスの無効化
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

---

## システムサービス (オプション)

シミュレーターをシステムサービスとして実行するには:

```bash
# サービスの有効化
sudo systemctl enable golf-hils.service

# サービスの開始
sudo systemctl start golf-hils.service

# ステータス確認
sudo systemctl status golf-hils.service

# ログの表示
sudo journalctl -u golf-hils.service -f
```

---

## 開発ワークフロー

### センサーファームウェア開発

1. ソースコードを変更
2. ローカルでビルド・テスト:
   ```bash
   pio run
   pio test
   ```
3. デバイスにアップロード:
   ```bash
   pio run --target upload
   ```
4. シリアル出力を監視:
   ```bash
   pio device monitor
   ```

### シミュレーションソフトウェア開発

1. Pythonコードを変更
2. テストを実行:
   ```bash
   pytest tests/ -v
   ```
3. サンプルデータでテスト:
   ```bash
   python examples/trajectory_analysis_example.py
   ```
4. フルシステム統合テスト

---

## ドキュメント生成

### APIドキュメント

```bash
cd simulator-py/
source venv/bin/activate
pip install sphinx
sphinx-quickstart docs/
sphinx-build -b html docs/ docs/_build/
```

### コードドキュメント

```bash
# ファームウェアドキュメント生成
cd sensor-firmware/
doxygen Doxyfile

# Pythonドキュメント生成
cd simulator-py/
pdoc --html . --output-dir docs/
```

---

追加のサポートとアップデートについては、プロジェクトリポジトリのREADMEとissuesセクションを確認してください。