import mysql.connector
import pandas as pd
from typing import Dict, Any
from .exceptions import DataFetchError

class MySqlFetcher:
    """MySQLデータベースからデータを取得する責務を持つクラス。"""
    def __init__(self, db_config: Dict[str, Any], query: str):
        self.db_config = db_config
        self.query = query

    def fetch(self) -> pd.DataFrame:
        """
        データベースに接続し、クエリを実行して結果をDataFrameとして返す。
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(self.query)
            
            header = [i[0] for i in cursor.description]
            rows = cursor.fetchall()
            
            if not rows:
                return pd.DataFrame() # データがない場合は空のDataFrameを返す

            return pd.DataFrame(rows, columns=header)

        except mysql.connector.Error as e:
            # ライブラリ固有の例外を、我々のカスタム例外でラップして投げ直す
            raise DataFetchError(f"データベースからのデータ取得に失敗しました: {e}") from e
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()