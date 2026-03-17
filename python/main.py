import cv2
import cv2.aruco as aruco
from pythonosc import udp_client
from collections import defaultdict
import time
import numpy as np

# ==============================
# 設定
# ==============================

OSC_IP = "127.0.0.1"  # TDとPythonでPC分ける場合はここを変更

STABLE_FRAMES = 5    # 現れるまでの安定フレーム数
REM_PATIENCE = 15    # 【重要】見えなくなってから消すまでの猶予フレーム数 (約0.5秒〜1秒)

seen_counter = defaultdict(int)    # 現れる時のカウント
missing_counter = defaultdict(int) # 【追加】消える時のカウント

last_event_time = 0
EVENT_COOLDOWN = 0.4

PORT_UI_ACTIVE = 8000 
PORT_LEFT_RADIUS = 8001 
PORT_LEFT_LABEL = 8002 
PORT_RIGHT_RADIUS = 8003 
PORT_UI_LAST_LAKE = 8004 
PORT_EVENT = 8005 
PORT_STATE_ACTIVE = 8006 
PORT_EVENT_NEW_LAKE = 8007 

# ==============================
# OSC クライアント
# ==============================

client_ui_active = udp_client.SimpleUDPClient(OSC_IP, PORT_UI_ACTIVE)
client_left_radius = udp_client.SimpleUDPClient(OSC_IP, PORT_LEFT_RADIUS)
client_left_label = udp_client.SimpleUDPClient(OSC_IP, PORT_LEFT_LABEL)
client_right_radius = udp_client.SimpleUDPClient(OSC_IP, PORT_RIGHT_RADIUS)
client_ui_last_lake = udp_client.SimpleUDPClient(OSC_IP, PORT_UI_LAST_LAKE)
client_event = udp_client.SimpleUDPClient(OSC_IP, PORT_EVENT)
client_state_active = udp_client.SimpleUDPClient(OSC_IP, PORT_STATE_ACTIVE)
client_event_new_lake = udp_client.SimpleUDPClient(OSC_IP, PORT_EVENT_NEW_LAKE)

# ==============================
# データ読み込み
# ==============================

from lake_data import LAKES              
from comparison_data import find_comparison 

# ==============================
# 状態管理
# ==============================

active_ids_set = set()      # 確定して表示中の湖ID
active_ids_order = []      

# ==============================
# ArUco 初期化
# ==============================

cap = cv2.VideoCapture(0)
# 自動露出をオフにして固定する設定（カメラによりますが、安定化に効きます）
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) 
# cap.set(cv2.CAP_PROP_EXPOSURE, -5.0) # 値は環境による

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
aruco_params = aruco.DetectorParameters()

aruco_params.adaptiveThreshWinSizeMin = 3
aruco_params.adaptiveThreshWinSizeMax = 23
aruco_params.minMarkerPerimeterRate = 0.03

detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# ==============================
# イベント関数
# ==============================
def trigger_absorb():
    client_event.send_message("/event/absorb", 1)
    time.sleep(0.02)
    client_event.send_message("/event/absorb", 0)

def trigger_new_lake():
    client_event_new_lake.send_message("/event/new_lake", 1)
    time.sleep(0.02)
    client_event_new_lake.send_message("/event/new_lake", 0)

# ==============================
# メインループ
# ==============================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ==============================
    # ピントの甘さをカバーするシャープネス処理
    # ==============================
    # 輪郭を強調するための「カーネル（計算式）」を作ります
    kernel = np.array([[-1, -1, -1],
                        [-1,  9, -1],
                        [-1, -1, -1]])
    # 白黒画像にフィルターをかけます
    gray = cv2.filter2D(gray, -1, kernel)
    
    corners, ids, _ = detector.detectMarkers(gray)

    # 今のフレームで「見えている」候補ID
    detected_ids_now = set()
    if ids is not None:
        for marker_id in ids.flatten():
            if marker_id in LAKES:
                detected_ids_now.add(int(marker_id))

    # ==============================
    # 1. 出現判定 (Stable Frames)
    # ==============================
    
    # 認識されたものはカウントアップ
    for mid in detected_ids_now:
        seen_counter[mid] += 1
        # 見えているなら消失カウントはリセット
        missing_counter[mid] = 0
    
    # 認識されなかったものは出現カウントリセット
    for mid in list(seen_counter.keys()):
        if mid not in detected_ids_now:
            seen_counter[mid] = 0

    # 新たに追加するリスト
    to_add = []
    
    for mid in detected_ids_now:
        if mid not in active_ids_set:
            if seen_counter[mid] >= STABLE_FRAMES:
                to_add.append(mid)

    # ==============================
    # 2. 消失判定 (Patience) 
    # ==============================
    
    to_remove = []

    # 今アクティブな湖についてチェック
    for mid in list(active_ids_set):
        if mid not in detected_ids_now:
            # 見えなくなったら消失カウントを増やす
            missing_counter[mid] += 1
            # 猶予を超えたら削除リスト入り
            if missing_counter[mid] > REM_PATIENCE:
                to_remove.append(mid)
        else:
            # 見えていれば消失カウントはゼロ
            missing_counter[mid] = 0

    # ==============================
    # 3. 状態更新
    # ==============================

    added_flag = False

    # 追加処理
    for mid in to_add:
        active_ids_set.add(mid)
        active_ids_order.append(mid)
        added_flag = True

    # 削除処理
    for mid in to_remove:
        if mid in active_ids_set:
            active_ids_set.remove(mid)
        if mid in active_ids_order:
            active_ids_order.remove(mid)
        # カウンタ類も掃除
        seen_counter[mid] = 0
        missing_counter[mid] = 0
    
    # 今回のフレームで「確定で消えた」湖があり、かつ、まだ他の湖が残っている場合
    if len(to_remove) > 0 and len(active_ids_set) > 0:
        
        # 1. 減った後の合計面積ですぐに比較対象を計算
        total_area = sum(LAKES[i]["area"] for i in active_ids_set)
        left_comp = find_comparison(total_area)
        
        # 2. OSCですぐに新しい目標値を送る
        client_left_radius.send_message("/circle/left/target_radius", left_comp["radius"])
        client_left_label.send_message("/circle/left/label", left_comp["name"])

        # 3. 右側の円（追加用）は「なし」にする
        # （減った時は右から足されるわけではないので、右は空っぽにする）
        client_right_radius.send_message("/circle/right/radius", 0)
        client_ui_last_lake.send_message("/ui/last_lake_text", " ")

        # 4. 「吸収イベント」を発火させて、TD側のタイマーを動かす
        # 左の円が「再計算されたサイズ」へアニメーションします
        trigger_absorb()
        
        # 連続発火を防ぐため少し待つ
        time.sleep(0.1)

    # ==============================
    # 4. OSC送信処理
    # ==============================

    # --- 名前一覧 ---
    names = [LAKES[i]["name"] for i in active_ids_order]
    active_text = f'【 { "＋".join(names)} 】' if names else ""
    client_ui_active.send_message("/ui/active_lakes_text", active_text)

    # --- 左円（合計比較） ---
    if active_ids_set:
        total_area = sum(LAKES[i]["area"] for i in active_ids_set)
        
        left_comp = find_comparison(total_area)

        if left_comp:
            client_left_radius.send_message("/circle/left/target_radius", left_comp["radius"])
            client_left_label.send_message("/circle/left/label", left_comp["name"])
    else:
        # 湖がゼロになったらクリア
        client_left_label.send_message("/circle/left/label", "")
        client_left_radius.send_message("/circle/left/target_radius", 0)
        client_ui_last_lake.send_message("/ui/last_lake_text", " ")
        client_right_radius.send_message("/circle/right/radius", 0)
    
    # アクティブ状態送信
    is_active = 1 if active_ids_set else 0
    client_state_active.send_message("/state/active", is_active)

    # --- 右円 & イベント発火 ---
    now = time.time()
    
    # 新規追加があった場合のみ実行
    if added_flag and (now - last_event_time > EVENT_COOLDOWN):
        # 一番最後に追加された湖を取得
        # (to_addリストの最後を使う)
        last_id = to_add[-1]
        
        area = LAKES[last_id]["area"]
        right_comp = find_comparison(area)

        client_right_radius.send_message("/circle/right/radius", right_comp["radius"])
        
        # 詳しい情報を表示
        info_text = f'{LAKES[last_id]["name"]}'
        if "yomi" in LAKES[last_id]:
            info_text += f'({LAKES[last_id]["yomi"]})'
        info_text += f'\n面積：{area:.1f} km²'
        if "pref" in LAKES[last_id]:
            info_text += f'\n都道府県: {LAKES[last_id]["pref"]}'
            
        client_ui_last_lake.send_message("/ui/last_lake_text", info_text)

        trigger_new_lake()
        
        # 1つ以上あれば吸収演出
        if len(active_ids_set) >= 1:
            trigger_absorb()

        last_event_time = now
        time.sleep(0.1) # 連続防止

    # ==============================
    # 終了
    # ==============================
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()