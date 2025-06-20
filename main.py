import logging
import sys
from app_extractor import config
from app_extractor.exceptions import PipelineError
from app_extractor.data_fetcher import MySqlFetcher
from app_extractor.file_writer import CsvWriter
from app_extractor.uploader import GoogleDriveUploader
from app_extractor.pipeline import SalesDataPipeline

def setup_logging():
    """アプリケーション全体の基本ロギング設定を行う。"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("pipeline.log", 'a', 'utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    """
    アプリケーションのエントリーポイント。
    依存オブジェクトを生成し、パイプラインに注入して実行する。
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("アプリケーションを起動します。")

    try:
        # 1. 各専門家（依存オブジェクト）を生成する
        fetcher = MySqlFetcher(db_config=config.DB_CONFIG, query=config.SQL_QUERY)
        writer = CsvWriter(output_dir=config.OUTPUT_DIR)
        uploader = GoogleDriveUploader(
            token_file=config.GOOGLE_TOKEN_FILE,
            creds_file=config.GOOGLE_CREDENTIALS_FILE,
            scopes=config.GOOGLE_DRIVE_API_SCOPES
        )

        # 2. 生成した専門家たちを司令塔（パイプライン）に注入する
        pipeline = SalesDataPipeline(fetcher=fetcher, writer=writer, uploader=uploader)

        # 3. パイプラインを実行する
        pipeline.run(
            csv_prefix=config.CSV_PREFIX,
            gdrive_folder_id=config.GOOGLE_DRIVE_FOLDER_ID
        )

        logger.info("アプリケーションは正常に終了しました。")

    except PipelineError as e:
        # 我々が定義したカスタムエラーを捕捉する
        logger.critical(f"パイプライン実行中に制御されたエラーが発生しました: {e}", exc_info=True)
        sys.exit(1) # エラー終了
    except Exception as e:
        # 予期せぬその他のエラーを捕捉する
        logger.critical(f"予期せぬ致命的なエラーが発生しました: {e}", exc_info=True)
        sys.exit(1) # エラー終了


if __name__ == '__main__':
    main()