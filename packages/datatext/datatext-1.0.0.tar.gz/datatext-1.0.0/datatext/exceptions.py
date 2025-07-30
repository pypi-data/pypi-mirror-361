"""
DataText 例外クラス
"""


class DataTextError(Exception):
    """基本的なDataTextエラー"""
    pass


class TableNotFoundError(DataTextError):
    """テーブルが見つからない場合のエラー"""
    pass


class InvalidDataError(DataTextError):
    """無効なデータの場合のエラー"""
    pass


class QueryError(DataTextError):
    """クエリエラー"""
    pass