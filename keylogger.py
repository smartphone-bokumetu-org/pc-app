from pynput import keyboard
from collections import Counter, deque
import time
import threading
from threading import Lock

# スレッド間のデータ共有を安全に行うためのロック
data_lock = Lock()
data_dict = {}

# ユーザープロファイルの定義
class UserProfile:
    def __init__(self):
        self.baseline_wpm = 0
        self.baseline_std_deviation = 0
        self.calibrated = False

    def calibrate(self, key_times, key_intervals):
        if len(key_times) > 5:  # 最低限のデータ量を設定
            minutes = (key_times[-1] - key_times[0]) / 60
            char_count = len(key_times)
            self.baseline_wpm = (char_count / 5) / minutes  # WPM計算

            average_interval = sum(key_intervals) / len(key_intervals)
            variance = sum((interval - average_interval) ** 2 for interval in key_intervals) / len(key_intervals)
            self.baseline_std_deviation = variance ** 0.5

            self.calibrated = True
            # print("キャリブレーションが完了しました。")
            # print(f"ベースラインWPM: {self.baseline_wpm:.2f}")
            # print(f"ベースライン標準偏差: {self.baseline_std_deviation:.4f}")
            data_dict['baseline_wpm'] = self.baseline_wpm
            data_dict['baseline_std_deviation'] = self.baseline_std_deviation
        else:
            # print("キャリブレーションに十分なデータがありません。もう少しタイピングしてください。")
            pass

# ユーザープロファイルのインスタンス
user_profile = UserProfile()

# タイポを記録するためのカウンター
typo_counter = Counter()
# キー入力の時間を記録（過去60秒分）
key_times = deque()
# バックスペースとデリートキーの使用頻度を記録
backspace_counter = 0
delete_counter = 0

# タイピング速度を計測するための変数（WPM）
typing_speed = 0
previous_typing_speed = 0

# 疲労度の評価
fatigue_level = 0

# キー入力間隔のリズムを記録（過去60秒分）
key_intervals = deque()

# バックスペースとデリートキーのしきい値
BACKSPACE_THRESHOLD = 5
DELETE_THRESHOLD = 5

# リズムの乱れ検出のしきい値（ユーザーごとに調整可能）
RHYTHM_THRESHOLD = 0.1  # ユーザープロファイルのベースラインに基づいて調整

# 各要素の重み付け
TYPO_WEIGHT = 0.2
BACKSPACE_WEIGHT = 0.3
DELETE_WEIGHT = 0.3
RHYTHM_WEIGHT = 0.2
SPEED_DROP_WEIGHT = 0.1

# キー入力間隔の標準偏差を計算する関数
def get_key_intervals_std_deviation():
    with data_lock:
        intervals = list(key_intervals)
    if len(intervals) > 1:
        average_interval = sum(intervals) / len(intervals)
        variance = sum((interval - average_interval) ** 2 for interval in intervals) / len(intervals)
        std_deviation = variance ** 0.5
        return std_deviation
    else:
        return 0

# タイピング速度を計算する関数（WPM）
def calculate_wpm():
    global typing_speed, previous_typing_speed
    while True:
        time.sleep(1)  # 毎秒チェック
        with data_lock:
            if len(key_times) > 1:
                current_time = time.time()
                # 60秒より古いタイムスタンプを削除
                while key_times and current_time - key_times[0] > 60:
                    key_times.popleft()
                minutes = (key_times[-1] - key_times[0]) / 60
                if minutes > 0:
                    char_count = len(key_times)
                    previous_typing_speed = typing_speed
                    typing_speed = (char_count / 5) / minutes  # WPM計算
                else:
                    typing_speed = 0
            else:
                typing_speed = 0
        # print(f"タイピング速度: {typing_speed:.2f} WPM")
        data_dict['typing_speed'] = typing_speed

        # 速度低下の検出（疲労の可能性）
        if user_profile.calibrated and typing_speed < user_profile.baseline_wpm * 0.8:
            # print("速度低下が顕著です。疲労の可能性があります。")
            pass

# 疲労度を計算する関数
def calculate_fatigue_level():
    global fatigue_level, typo_counter, backspace_counter, delete_counter, typing_speed, previous_typing_speed

    std_deviation = get_key_intervals_std_deviation()

    current_time = time.time()
    with data_lock:
        # ベースラインとの差を計算
        if user_profile.calibrated:
            rhythm_difference = max(0, (std_deviation - user_profile.baseline_std_deviation))
            
            if key_times:
                time_since_last_key = current_time - key_times[-1]
            else:
                time_since_last_key = None

            # 直近のキー入力が一定時間以内の場合のみ速度低下を計算
            if typing_speed > 0 and time_since_last_key is not None and time_since_last_key < 10:
                speed_drop = max(0, (user_profile.baseline_wpm - typing_speed))
            else:
                speed_drop = 0
        else:
            rhythm_difference = 0
            speed_drop = 0

        # 疲労度の計算
        fatigue_level = (
            TYPO_WEIGHT * sum(typo_counter.values()) +
            BACKSPACE_WEIGHT * max(0, (backspace_counter - BACKSPACE_THRESHOLD)) +
            DELETE_WEIGHT * max(0, (delete_counter - DELETE_THRESHOLD)) +
            RHYTHM_WEIGHT * rhythm_difference +
            SPEED_DROP_WEIGHT * speed_drop
        )
        # カウンターのリセット
        typo_counter.clear()
        backspace_counter = 0
        delete_counter = 0

    # print("推定疲労度:", fatigue_level)
    data_dict['fatigue_level'] = fatigue_level
    pass
# タイピングの一貫性を計算する関数
def calculate_typing_consistency():
    std_deviation = get_key_intervals_std_deviation()
    # print(f"タイピングの一貫性（標準偏差）: {std_deviation:.4f}")
    data_dict['typing_consistency'] = std_deviation
    pass

# キーが押されたときの処理
def on_press(key):
    global backspace_counter, delete_counter
    current_time = time.time()
    with data_lock:
        if key_times:
            interval = current_time - key_times[-1]
            key_intervals.append(interval)
            # 60秒より古い間隔を削除
            while key_intervals and current_time - key_times[0] > 60:
                key_intervals.popleft()
        key_times.append(current_time)

    try:
        print(f'Key {key.char} pressed', flush=True)
        data_dict['key_pressed'] = key.char
        print(data_dict)
        pass
    except AttributeError:
        # print(f'Special key {key} pressed', flush=True)
        pass

    with data_lock:
        # バックスペースキーの使用頻度を計測
        if key == keyboard.Key.backspace:
            backspace_counter += 1
            typo_counter['backspace'] += 1
        # デリートキーの使用頻度を計測
        elif key == keyboard.Key.delete:
            delete_counter += 1
            typo_counter['delete'] += 1

    # キャリブレーションが完了していない場合、一定のキー入力後にキャリブレーションを実行
    if not user_profile.calibrated and len(key_times) >= 50:
        user_profile.calibrate(list(key_times), list(key_intervals))

    # 疲労度の推定
    calculate_fatigue_level()

    # キー入力リズムの乱れを検知
    if user_profile.calibrated:
        rhythm_difference = abs(get_key_intervals_std_deviation() - user_profile.baseline_std_deviation)
        if rhythm_difference > RHYTHM_THRESHOLD:
            # print("キー入力リズムの乱れが検出されました。")
            # print(f"キー入力リズムの乱れ: {rhythm_difference:.4f}")
            data_dict['rhythm_difference'] = rhythm_difference
            pass

    # タイピングの一貫性を計算
    calculate_typing_consistency()

# タイピング速度の計測をバックグラウンドで実行
typing_speed_thread = threading.Thread(target=calculate_wpm)
typing_speed_thread.daemon = True
typing_speed_thread.start()

# キーボードリスナーを開始
try:
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
except KeyboardInterrupt:
    print("プログラムを終了します。")
