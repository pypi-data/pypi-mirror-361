#!/usr/bin/env python3
"""
DataText ライブラリの基本テストスイート
"""

import sys
import os
import tempfile
import shutil

# ライブラリのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datatext import DataText, DataTextError, TableNotFoundError, InvalidDataError

def test_basic_operations():
    """基本操作のテスト"""
    print("🧪 基本操作テスト")
    
    # 一時ファイルを使用
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
    
    try:
        db = DataText(test_file)
        
        # テーブル作成
        db.create_table('test_table', {
            'id': 'int',
            'name': 'str',
            'value': 'float'
        })
        
        # データ挿入
        db.insert('test_table', {'id': 1, 'name': 'test1', 'value': 10.5})
        db.insert('test_table', {'id': 2, 'name': 'test2', 'value': 20.0})
        
        # データ検索
        results = db.select('test_table').execute()
        assert len(results) == 2
        
        # 条件検索
        results = db.select('test_table').where('id', '=', 1).execute()
        assert len(results) == 1
        assert results[0]['name'] == 'test1'
        
        # データ更新
        updated = db.update('test_table', {'value': 15.0}, lambda r: r['id'] == 1)
        assert updated == 1
        
        # データ削除
        deleted = db.delete('test_table', lambda r: r['id'] == 2)
        assert deleted == 1
        
        # 残りのデータを確認
        results = db.select('test_table').execute()
        assert len(results) == 1
        assert results[0]['value'] == 15.0
        
        print("✅ 基本操作テスト成功")
        
    finally:
        # 一時ファイルを削除
        os.unlink(test_file)

def test_error_handling():
    """エラーハンドリングのテスト"""
    print("🧪 エラーハンドリングテスト")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
    
    try:
        db = DataText(test_file)
        
        # 存在しないテーブルへのアクセス
        try:
            db.select('nonexistent_table').execute()
            assert False, "例外が発生するべき"
        except TableNotFoundError:
            print("✅ 存在しないテーブルエラー検出")
        
        # 無効なテーブル作成
        try:
            db.create_table('', {})
            assert False, "例外が発生するべき"
        except InvalidDataError:
            print("✅ 無効なテーブル作成エラー検出")
        
        print("✅ エラーハンドリングテスト成功")
        
    finally:
        os.unlink(test_file)

def test_data_types():
    """データ型のテスト"""
    print("🧪 データ型テスト")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
    
    try:
        db = DataText(test_file)
        
        # 様々なデータ型のテーブル作成
        db.create_table('type_test', {
            'id': 'int',
            'name': 'str',
            'price': 'float',
            'active': 'bool',
            'created': 'datetime'
        })
        
        # データ挿入
        db.insert('type_test', {
            'id': 1,
            'name': 'テスト商品',
            'price': 99.99,
            'active': True,
            'created': '2024-01-01 12:00:00'
        })
        
        # データ取得して型を確認
        result = db.select('type_test').first()
        assert isinstance(result['id'], int)
        assert isinstance(result['name'], str)
        assert isinstance(result['price'], float)
        assert isinstance(result['active'], bool)
        
        print("✅ データ型テスト成功")
        
    finally:
        os.unlink(test_file)

def test_file_persistence():
    """ファイル永続化のテスト"""
    print("🧪 ファイル永続化テスト")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
    
    try:
        # 最初のインスタンス
        db1 = DataText(test_file)
        db1.create_table('persist_test', {'id': 'int', 'name': 'str'})
        db1.insert('persist_test', {'id': 1, 'name': 'テスト'})
        
        # 新しいインスタンスでファイルを読み込み
        db2 = DataText(test_file)
        results = db2.select('persist_test').execute()
        
        assert len(results) == 1
        assert results[0]['name'] == 'テスト'
        
        print("✅ ファイル永続化テスト成功")
        
    finally:
        os.unlink(test_file)

def run_all_tests():
    """すべてのテストを実行"""
    print("🚀 DataText ライブラリテストスイート")
    print("="*50)
    
    try:
        test_basic_operations()
        test_error_handling()
        test_data_types()
        test_file_persistence()
        
        print("\n🎉 すべてのテストが成功しました！")
        print("DataText ライブラリは正常に動作しています。")
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()