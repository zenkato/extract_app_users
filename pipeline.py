import os
import logging
from data_fetcher import MySqlFetcher
from file_writer import CsvWriter
from uploader import GoogleDriveUploader

class SalesDataPipeline:
    """
    データ処理のワークフロー全体を指揮するオーケストレータークラス。
    具体的な実装は専門家クラスに委譲する。
    """
    def __init__(self, fetcher: MySqlFetcher, writer: CsvWriter, uploader: GoogleDriveUploader):
        """
        依存性を注入（DI）：各専門家クラスのインスタンスをコンストラクタで受け取る。
        """
        self.fetcher = fetcher
        self.writer = writer
        self.uploader = uploader
        self.logger = logging.getLogger(__name__) # ロガーを取得

    def _cleanup_file(self, file_path: str) -> None:
        """指定された一時ファイルを安全に削除する。"""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.logger.info(f"一時ファイル '{file_path}' を削除しました。")
            except OSError as e:
                self.logger.error(f"ファイル '{file_path}' の削除中にエラーが発生しました: {e}")

    def run(self, csv_prefix: str, gdrive_folder_id: str) -> None:
        """
        パイプラインのメイン処理を実行する。
        データの流れ： fetcher -> writer -> uploader
        """
        self.logger.info("--- データパイプライン処理を開始します ---")
        output_file_path = None
        try:
            # 1. 取得 (Fetcherに依頼)
            self.logger.info("データの取得を開始します...")
            dataframe = self.fetcher.fetch()
            if dataframe.empty:
                self.logger.warning("取得データが0件のため、処理を正常に終了します。")
                return
            self.logger.info(f"{len(dataframe)}件のデータを取得しました。")

            # 2. 書き込み (Writerに依頼)
            self.logger.info("CSVファイルへの書き込みを開始します...")
            output_file_path = self.writer.write(dataframe, csv_prefix)
            self.logger.info(f"CSVファイル '{output_file_path}' の書き込みが完了しました。")

            # 3. 送信 (Uploaderに依頼)
            self.logger.info("Google Driveへのアップロードを開始します...")
            file_id = self.uploader.upload(output_file_path, gdrive_folder_id)
            self.logger.info(f"ファイルのアップロードが完了しました。 File ID: {file_id}")

        finally:
            # 4. 後片付け
            self.logger.info("クリーンアップ処理を開始します...")
            self._cleanup_file(output_file_path)
            self.logger.info("--- データパイプライン処理を終了します ---")