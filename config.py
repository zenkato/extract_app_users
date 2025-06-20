import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# --- 型チェックを容易にするための定数 ---
# os.getenvはNoneを返す可能性があるため、Noneでないことを前提とする場合は
# 以下のように変数に代入することで、型チェッカー(Mypy)が解析しやすくなる。
def get_env_var(var_name: str) -> str:
    """環境変数を取得する。存在しない場合は例外を発生させる。"""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"環境変数 '{var_name}' が設定されていません。")
    return value

# --- データベース設定 ---
DB_CONFIG = {
    'user': get_env_var("DB_USER"),
    'password': get_env_var("DB_PASSWORD"),
    'host': get_env_var("DB_HOST"),
    'database': get_env_var("DB_NAME"),
}

# --- Google API 設定 ---
GOOGLE_DRIVE_FOLDER_ID = get_env_var("GOOGLE_DRIVE_FOLDER_ID")
GOOGLE_CREDENTIALS_FILE = get_env_var("GOOGLE_CREDENTIALS_FILE")
GOOGLE_TOKEN_FILE = get_env_var("GOOGLE_TOKEN_FILE")
GOOGLE_DRIVE_API_SCOPES = ['https://www.googleapis.com/auth/drive.file']

# --- 出力ディレクトリ ---
OUTPUT_DIR = get_env_var("OUTPUT_DIR")

# --- 出力ファイル名の接頭辞 ---
CSV_PREFIX = "アプリユーザーリスト抽出"

# --- SQLクエリ ---
# この部分はロジックに近いが、巨大な文字列なので設定ファイルに置く
SQL_QUERY = """
SELECT
  sm.super_name AS "SM名",
  sc.name AS "号車名",
  sp.id AS "販売PID",
  sp.name AS "氏名",
  sp.app_first_login_date AS "初回ログイン日時",
  sp.last_login_at AS "最終利用日時",
  sp.open_date AS "開業日",
  CASE
    WHEN sp.is_active = 1 THEN '有効'
    WHEN sp.is_active = 0 THEN '無効'
  END AS "アカウント状態"
FROM sales_partners AS sp
JOIN sm ON sp.sm_id = sm.id
LEFT JOIN sales_cars AS sc ON sp.sales_car_id = sc.id
WHERE sp.app_first_login_date IS NOT NULL;
"""