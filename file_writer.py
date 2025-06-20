import os
import pandas as pd
from datetime import datetime
from exceptions import FileWriteError

class CsvWriter:
    """DataFrameをCSVファイルとして書き出す責務を持つクラス。"""
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        # 出力ディレクトリが存在しない場合は作成する
        os.makedirs(self.output_dir, exist_ok=True)

    def write(self, df: pd.DataFrame, filename_prefix: str) -> str:
        """
        DataFrameを指定されたエンコーディングでCSVに書き込み、
        作成されたファイルのフルパスを返す。
        """
        try:
            today_str = datetime.now().strftime('%Y%m%d')
            filename = f'{filename_prefix}_{today_str}.csv'
            full_path = os.path.join(self.output_dir, filename)
            
            # Shift_JISで書き込む
            df.to_csv(full_path, index=False, encoding='shift_jis', errors='replace')
            
            return full_path
        except (IOError, OSError) as e:
            raise FileWriteError(f"CSVファイルの書き込みに失敗しました: {e}") from e