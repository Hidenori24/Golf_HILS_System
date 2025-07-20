# data_stream_mock.pyからのデータを読み込み、ストリームデータを解析するスクリプト
# IMUデータを読み取り， (x,y,z) = (0,0,0) の状態からどのような変化を起こしたかをグラフで表示する
# x,y,zの加速度をもとに現在速度と位置を計算し、グラフ化する
# 簡単に x,y/y,z/z,x の平面でグラフを作成する
# giroセンサのデータはいったん無視する
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
def load_stream_data(file_path):
    df = pd.read_csv(file_path)
    # タイムスタンプを「ミリ秒」としてパース
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_velocity_and_position(df):
    # 静止区間（最初の10サンプル）の平均をオフセットとする
    offset = df[['accel_x', 'accel_y', 'accel_z']].iloc[:10].mean()
    # ここでz軸から1.0を引かない！

    position = np.array([0.0, 0.0, 0.0])
    velocity = np.array([0.0, 0.0, 0.0])
    positions = []
    velocities = []

    prev_time = df['timestamp'].iloc[0]
    for index, row in df.iterrows():
        # オフセット補正＋g→m/s²変換
        acc = np.array([
            row['accel_x'] - offset['accel_x'],
            row['accel_y'] - offset['accel_y'],
            row['accel_z'] - offset['accel_z']
        ]) * 9.80665

        # サンプリング間隔dtをタイムスタンプから計算
        curr_time = row['timestamp']
        dt = (curr_time - prev_time).total_seconds() * 0.02 # 20msのサンプリング間隔
        # デバッグ出力
        print(f"index={index}, dt={dt:.6f}, acc={acc}, velocity={velocity}, position={position}")
        prev_time = curr_time

        velocity += acc * dt
        position += velocity * dt

        positions.append(position.copy())
        velocities.append(velocity.copy())

    return np.array(positions), np.array(velocities)

def plot_results(positions, velocities):
    with PdfPages('imu_trajectory_plots.pdf') as pdf:
        # x,yグラフ
        plt.figure()
        plt.plot(positions[:, 0], positions[:, 1], label='Position (x,y)')
        plt.title('Position in XY Plane')
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.grid()
        plt.legend()
        pdf.savefig()
        plt.close()

        # y,zグラフ
        plt.figure()
        plt.plot(positions[:, 1], positions[:, 2], label='Position (y,z)')
        plt.title('Position in YZ Plane')
        plt.xlabel('Y Position (m)')
        plt.ylabel('Z Position (m)')
        plt.grid()
        plt.legend()
        pdf.savefig()
        plt.close()

        # z,xグラフ
        plt.figure()
        plt.plot(positions[:, 2], positions[:, 0], label='Position (z,x)')
        plt.title('Position in ZX Plane')
        plt.xlabel('Z Position (m)')
        plt.ylabel('X Position (m)')
        plt.grid()
        plt.legend()
        pdf.savefig()
        plt.close()

        # x,y,zの三次元グラフ
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], label='Position (x,y,z)')
        ax.set_title('3D Trajectory')
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Y Position (m)')
        ax.set_zlabel('Z Position (m)')
        ax.legend()
        pdf.savefig(fig)
        plt.close(fig)
    
def main():
    file_path = '/Users/matsumoto/work/Golf_HILS_System/sensor-firmware/examples/data/imu_log.csv'
    df = load_stream_data(file_path)
    
    # 速度と位置を計算
    positions, velocities = calculate_velocity_and_position(df)
    
    # 結果をプロット
    plot_results(positions, velocities) 
    # main()関数を実行することで、データを読み込み、速度と位置を計算し、グラフを表示します。
    # 必要に応じて、他の処理を追加できます。
    # 例えば、生成したデータをファイルに保存するなどの処理も可能です。
    # ここでは、生成したデータを表示するだけにしています。
if __name__ == "__main__":
    main()