"""
datatext - プレーンテキストファイルで動作するシンプルDB

Usage:
    from datatext import DataText
    
    # データベース接続
    db = DataText('mydata.txt')
    
    # テーブル作成
    db.create_table('users', {
        'id': 'int',
        'name': 'str',
        'email': 'str',
        'created_at': 'datetime'
    })
    
    # データ挿入
    db.insert('users', {
        'id': 1,
        'name': '田中太郎',
        'email': 'tanaka@example.com',
        'created_at': '2024-01-01 10:00:00'
    })
    
    # データ検索
    results = db.select('users').where('name', '=', '田中太郎').execute()
"""

from .core import DataText
from .query import Query
from .exceptions import DataTextError, TableNotFoundError, InvalidDataError

__version__ = '1.0.p'
__author__ = 'tikisan'
__email__ = 's2501082@sendai-nct.jp'

__all__ = ['DataText', 'Query', 'DataTextError', 'TableNotFoundError', 'InvalidDataError']