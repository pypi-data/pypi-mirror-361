"""
DataText コアクラス
プレーンテキストファイルベースのシンプルDB
"""

import os
import datetime
import re
from typing import Dict, List, Any, Optional, Union
from .query import Query
from .exceptions import DataTextError, TableNotFoundError, InvalidDataError


class DataText:
    """メインのDataTextクラス"""
    
    def __init__(self, filename: str):
        """
        DataTextインスタンスを初期化
        
        Args:
            filename: データベースファイルのパス
        """
        self.filename = filename
        self.tables = {}
        self._load_file()
    
    def _load_file(self):
        """ファイルからデータを読み込み"""
        if not os.path.exists(self.filename):
            return
            
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read()
                self._parse_content(content)
        except Exception as e:
            raise DataTextError(f"ファイル読み込みエラー: {e}")
    
    def _parse_content(self, content: str):
        """ファイル内容をパース"""
        lines = content.strip().split('\n')
        current_table = None
        current_schema = None
        
        for line in lines:
            line = line.strip()
            
            # コメント行や空行をスキップ
            if not line or line.startswith('#'):
                continue
                
            # テーブル定義行
            if line.startswith('@table '):
                current_table = line.split(' ', 1)[1].strip()
                self.tables[current_table] = {'schema': {}, 'data': []}
                current_schema = None
                continue
            
            # スキーマ定義行
            if current_table and '|' in line and ':' in line:
                # スキーマ定義かデータかを判定
                if all(':' in part for part in line.split('|')):
                    # スキーマ定義
                    schema_parts = line.split('|')
                    for part in schema_parts:
                        if ':' in part:
                            field_name, field_type = part.split(':', 1)
                            self.tables[current_table]['schema'][field_name.strip()] = field_type.strip()
                    current_schema = self.tables[current_table]['schema']
                    continue
            
            # データ行
            if current_table and current_schema and '|' in line:
                data_parts = line.split('|')
                if len(data_parts) == len(current_schema):
                    record = {}
                    for i, (field_name, field_type) in enumerate(current_schema.items()):
                        value = data_parts[i].strip()
                        record[field_name] = self._convert_value(value, field_type)
                    self.tables[current_table]['data'].append(record)
    
    def _convert_value(self, value: str, field_type: str) -> Any:
        """値を適切な型に変換"""
        if value == '' or value.lower() == 'null':
            return None
            
        try:
            if field_type == 'int':
                return int(value)
            elif field_type == 'float':
                return float(value)
            elif field_type == 'bool':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif field_type == 'datetime':
                return datetime.datetime.fromisoformat(value.replace(' ', 'T'))
            else:  # str
                return value
        except (ValueError, TypeError) as e:
            raise InvalidDataError(f"値変換エラー: {value} を {field_type} に変換できません")
    
    def _format_value(self, value: Any, field_type: str) -> str:
        """値をファイル保存用の文字列に変換"""
        if value is None:
            return ''
        
        if field_type == 'datetime' and isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        elif field_type == 'bool':
            return 'true' if value else 'false'
        else:
            return str(value)
    
    def create_table(self, table_name: str, schema: Dict[str, str]) -> 'DataText':
        """
        新しいテーブルを作成
        
        Args:
            table_name: テーブル名
            schema: フィールド名と型の辞書
            
        Returns:
            self (メソッドチェーン用)
        """
        if not table_name or not schema:
            raise InvalidDataError("テーブル名とスキーマは必須です")
        
        self.tables[table_name] = {
            'schema': schema.copy(),
            'data': []
        }
        
        self._save_file()
        return self
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> 'DataText':
        """
        データを挿入
        
        Args:
            table_name: テーブル名
            data: 挿入するデータ
            
        Returns:
            self (メソッドチェーン用)
        """
        if table_name not in self.tables:
            raise TableNotFoundError(f"テーブル '{table_name}' が見つかりません")
        
        schema = self.tables[table_name]['schema']
        
        # スキーマに対してデータを検証
        for field_name, field_type in schema.items():
            if field_name not in data:
                data[field_name] = None
        
        # 余分なフィールドを除去
        validated_data = {k: v for k, v in data.items() if k in schema}
        
        self.tables[table_name]['data'].append(validated_data)
        self._save_file()
        return self
    
    def select(self, table_name: str, fields: Optional[List[str]] = None) -> Query:
        """
        SELECT クエリを開始
        
        Args:
            table_name: テーブル名
            fields: 選択するフィールド (None の場合は全フィールド)
            
        Returns:
            Query オブジェクト
        """
        if table_name not in self.tables:
            raise TableNotFoundError(f"テーブル '{table_name}' が見つかりません")
        
        return Query(self, table_name, fields)
    
    def update(self, table_name: str, data: Dict[str, Any], where_clause: Optional[callable] = None) -> int:
        """
        データを更新
        
        Args:
            table_name: テーブル名
            data: 更新データ
            where_clause: 更新条件 (関数)
            
        Returns:
            更新された行数
        """
        if table_name not in self.tables:
            raise TableNotFoundError(f"テーブル '{table_name}' が見つかりません")
        
        schema = self.tables[table_name]['schema']
        table_data = self.tables[table_name]['data']
        updated_count = 0
        
        for record in table_data:
            if where_clause is None or where_clause(record):
                for field, value in data.items():
                    if field in schema:
                        record[field] = value
                updated_count += 1
        
        if updated_count > 0:
            self._save_file()
        
        return updated_count
    
    def delete(self, table_name: str, where_clause: Optional[callable] = None) -> int:
        """
        データを削除
        
        Args:
            table_name: テーブル名
            where_clause: 削除条件 (関数)
            
        Returns:
            削除された行数
        """
        if table_name not in self.tables:
            raise TableNotFoundError(f"テーブル '{table_name}' が見つかりません")
        
        table_data = self.tables[table_name]['data']
        original_count = len(table_data)
        
        if where_clause is None:
            # 全削除
            self.tables[table_name]['data'] = []
        else:
            # 条件削除
            self.tables[table_name]['data'] = [
                record for record in table_data 
                if not where_clause(record)
            ]
        
        deleted_count = original_count - len(self.tables[table_name]['data'])
        
        if deleted_count > 0:
            self._save_file()
        
        return deleted_count
    
    def drop_table(self, table_name: str) -> 'DataText':
        """
        テーブルを削除
        
        Args:
            table_name: テーブル名
            
        Returns:
            self (メソッドチェーン用)
        """
        if table_name not in self.tables:
            raise TableNotFoundError(f"テーブル '{table_name}' が見つかりません")
        
        del self.tables[table_name]
        self._save_file()
        return self
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        テーブル情報を取得
        
        Args:
            table_name: テーブル名
            
        Returns:
            テーブル情報
        """
        if table_name not in self.tables:
            raise TableNotFoundError(f"テーブル '{table_name}' が見つかりません")
        
        table = self.tables[table_name]
        return {
            'name': table_name,
            'schema': table['schema'].copy(),
            'record_count': len(table['data'])
        }
    
    def list_tables(self) -> List[str]:
        """
        すべてのテーブル名を取得
        
        Returns:
            テーブル名のリスト
        """
        return list(self.tables.keys())
    
    def _save_file(self):
        """データをファイルに保存"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write("# datatext database file\n")
                f.write("# generated by datatext library\n\n")
                
                for table_name, table_data in self.tables.items():
                    f.write(f"@table {table_name}\n")
                    
                    # スキーマ行
                    schema_parts = []
                    for field_name, field_type in table_data['schema'].items():
                        schema_parts.append(f"{field_name}:{field_type}")
                    f.write("|".join(schema_parts) + "\n")
                    
                    # データ行
                    for record in table_data['data']:
                        data_parts = []
                        for field_name, field_type in table_data['schema'].items():
                            value = record.get(field_name)
                            formatted_value = self._format_value(value, field_type)
                            data_parts.append(formatted_value)
                        f.write("|".join(data_parts) + "\n")
                    
                    f.write("\n")  # テーブル間の空行
        
        except Exception as e:
            raise DataTextError(f"ファイル保存エラー: {e}")