class PipelineError(Exception):
    """このパイプライン処理における基底エラークラス。"""
    pass

class DataFetchError(PipelineError):
    """データ取得に関するエラー。"""
    pass

class FileWriteError(PipelineError):
    """ファイル書き込みに関するエラー。"""
    pass

class FileUploadError(PipelineError):
    """ファイルアップロードに関するエラー。"""
    pass

class ConfigurationError(PipelineError):
    """設定不備に関するエラー。"""
    pass