import math

SCALE = 0.009  # ← TD用のスケール係数（調整用）

# COMPARISON_PLACES = [
#     # --- very small (建物・単位) ---
#     {
#         "id": "tokyo_dome",
#         "name": "東京ドーム",
#         "yomi": "とうきょうどーむ",
#         "area": 0.0467,
#         "type": "building"
#     },
#     # --- parks ---
#     {
#         "id": "yoyogi_park",
#         "name": "代々木公園",
#         "yomi": "よよぎこうえん",
#         "area": 0.54,
#         "type": "park"
#     },
#     {
#         "id": "shinjuku_gyoen",
#         "name": "新宿御苑",
#         "yomi": "しんじゅくぎょえん",
#         "area": 0.58,
#         "type": "park"
#     },

#     # --- religious sites ---
#     {
#         "id": "izumo_taisha",
#         "name": "出雲大社（境内）",
#         "yomi": "いずもたいしゃ",
#         "area": 0.27,
#         "type": "religious"
#     },
#     {
#         "id": "ise_jingu",
#         "name": "伊勢神宮（内宮+外宮）",
#         "yomi": "いせじんぐう",
#         "area": 5.50,
#         "type": "religious"
#     },
#     # --- wards (東京23区) ---
#     {
#         "id": "shibuya",
#         "name": "渋谷区",
#         "yomi": "しぶやく",
#         "area": 15.11,
#         "type": "ward"
#     },
#     {
#         "id": "haneda_airport",
#         "name": "羽田空港",
#         "yomi": "はねだくうこう",
#         "area": 15.20,
#         "type": "airport"
#     },
#     {
#         "id": "shinjuku",
#         "name": "新宿区",
#         "yomi": "しんじゅくく",
#         "area": 18.22,
#         "type": "ward"
#     },
#     {
#         "id": "yamanote_line_inside",
#         "name": "山手線の内側",
#         "yomi": "やまのてのうちがわ",
#         "area": 63.00,
#         "type": "landmark"
#     },
#     # --- cities ---
#     {
#         "id": "kawasaki",
#         "name": "川崎市",
#         "yomi": "かわさきし",
#         "area": 144.35,
#         "type": "city"
#     },
#     {
#         "id": "shodoshima",
#         "name": "小豆島",
#         "yomi": "しょうどしま",
#         "area": 153.30,
#         "type": "island"
#     },
#     {
#         "id": "miyakojima",
#         "name": "宮古島",
#         "yomi": "みやこじま",
#         "area": 158.87,
#         "type": "island"
#     },
#     {
#         "id": "osaka_city",
#         "name": "大阪市",
#         "yomi": "おおさかし",
#         "area": 225.0,
#         "type": "city"
#     },
#     {
#         "id": "nagoya",
#         "name": "名古屋市",
#         "yomi": "なごやし",
#         "area": 326.0,
#         "type": "city"
#     },
#     {
#         "id": "fukuoka",
#         "name": "福岡市",
#         "yomi": "ふくおかし",
#         "area": 343.39,
#         "type": "city"
#     },
#     {
#         "id": "yokohama",
#         "name": "横浜市",
#         "yomi": "よこはまし",
#         "area": 437.0,
#         "type": "city"
#     },
#     {
#         "id": "awajishima",
#         "name": "淡路島",
#         "yomi": "あわじしま",
#         "area": 592.17,
#         "type": "island"
#     },
#     {
#         "id": "sadogashima",
#         "name": "佐渡島",
#         "yomi": "さどがしま",
#         "area": 854.76,
#         "type": "island"
#     },
#     {
#         "id": "mt_fuji_base",
#         "name": "富士山（山麓含む）",
#         "yomi": "ふじさん",
#         "area": 902.00,
#         "type": "landmark"
#     },
#     {
#         "id": "hiroshima",
#         "name": "広島市",
#         "yomi": "ひろしまし",
#         "area": 906.69,
#         "type": "city"
#     },
#     {
#         "id": "sapporo",
#         "name": "札幌市",
#         "yomi": "さっぽろし",
#         "area": 1121.0,
#         "type": "city"
#     },
#     # --- prefectures ---
#     {
#         "id": "tokyo_pref",
#         "name": "東京都",
#         "yomi": "とうきょうと",
#         "area": 2194.0,
#         "type": "prefecture"
#     },
#     {
#         "id": "kanagawa",
#         "name": "神奈川県",
#         "yomi": "かながわけん",
#         "area": 2415.0,
#         "type": "prefecture"
#     },
#     {
#         "id": "saitama",
#         "name": "埼玉県",
#         "yomi": "さいたまけん",
#         "area": 3797.8,
#         "type": "prefecture"
#     },
#     {
#     "id": "chiba",
#     "name": "千葉県",
#     "yomi": "ちばけん",
#     "area": 5157.6,
#     "type": "prefecture"
#     }
# ]

def area_to_radius(area):
    """
    面積 → 円の半径（正規化済み）
    """
    return math.sqrt(area) * SCALE

def find_comparison(area_km2):
    # 1km2 = 1,000,000 m2
    # 1畳 = 約1.62 m2
    area_m2 = area_km2 * 1000000
    tatami_count = area_m2 / 1.62
    
    # 桁区切りのカンマを入れた文字列
    display_text = f"{int(tatami_count):,} 畳"
    
    # 半径（radius）は、TD側で円の大きさとしてそのまま使うので、
    # 面積の平方根にスケールをかけたものを返します
    import math
    draw_radius = math.sqrt(area_km2) * 0.015 # 0.1はTDの画面サイズに合わせた係数
    
    return {
        "name": display_text,
        "radius": draw_radius
    }