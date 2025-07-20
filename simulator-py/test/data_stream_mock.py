# /Users/matsumoto/work/Golf_HILS_System/sensor-firmware/examples/data/imu_log.csv からデータを持ってきて
# streamdataのように提供するpythonスクリプト
# analyze_data.pyから呼び出して使う

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_imu_data(file_path):
    # ヘッダー行を自動認識
    df = pd.read_csv(file_path)
    # タイムスタンプ（ミリ秒）をdatetime型に変換
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    imu_data = df[['timestamp', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']].to_numpy()
    return imu_data

def generate_stream_data(imu_data, start_time, interval=0.01):
    stream_data = []
    for i, row in enumerate(imu_data):
        timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = row
        # 開始時刻＋サンプル間隔でストリーム時刻を生成
        adjusted_timestamp = start_time + timedelta(seconds=i * interval)
        stream_data.append([adjusted_timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z])
    return np.array(stream_data)

def main():
    file_path = '/Users/matsumoto/work/Golf_HILS_System/sensor-firmware/examples/data/imu_log.csv'
    imu_data = load_imu_data(file_path)
    start_time = datetime.now()
    stream_data = generate_stream_data(imu_data, start_time)
    for row in stream_data:
        # ISO8601形式で出力
        print(f"{row[0].isoformat()},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]}")
    # main()関数を実行することで、データを読み込み、ストリームデータを生成して表示します。
    # 必要に応じて、他の処理を追加できます。
    # 例えば、生成したデータをファイルに保存するなどの処理も可能です。
    # ここでは、生成したデータを表示するだけにしています。

if __name__ == "__main__":
    main()