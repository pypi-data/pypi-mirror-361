"""
Query クラス - SQL風クエリ機能
"""

from typing import List, Dict, Any, Optional, Union, Callable
from .exceptions import DataTextError


class Query:
    """SQL風クエリビルダー"""
    
    def __init__(self, db, table_name: str, fields: Optional[List[str]] = None):
        """
        Queryインスタンスを初期化
        
        Args:
            db: DataTextインスタンス
            table_name: テーブル名
            fields: 選択するフィールド
        """
        self.db = db
        self.table_name = table_name
        self.fields = fields
        self.where_conditions = []
        self.order_by_field = None
        self.order_by_desc = False
        self.limit_count = None
        self.offset_count = 0
    
    def where(self, field: str, operator: str, value: Any) -> 'Query':
        """
        WHERE条件を追加
        
        Args:
            field: フィールド名
            operator: 演算子 ('=', '!=', '>', '<', '>=', '<=', 'like', 'in')
            value: 比較値
            
        Returns:
            self (メソッドチェーン用)
        """
        self.where_conditions.append({
            'field': field,
            'operator': operator,
            'value': value
        })
        return self
    
    def where_func(self, func: Callable[[Dict[str, Any]], bool]) -> 'Query':
        """
        カスタム WHERE条件を追加
        
        Args:
            func: 条件関数
            
        Returns:
            self (メソッドチェーン用)
        """
        self.where_conditions.append({
            'type': 'function',
            'function': func
        })
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'Query':
        """
        ORDER BY を設定
        
        Args:
            field: ソートするフィールド
            desc: 降順の場合True
            
        Returns:
            self (メソッドチェーン用)
        """
        self.order_by_field = field
        self.order_by_desc = desc
        return self
    
    def limit(self, count: int) -> 'Query':
        """
        LIMIT を設定
        
        Args:
            count: 取得する行数
            
        Returns:
            self (メソッドチェーン用)
        """
        self.limit_count = count
        return self
    
    def offset(self, count: int) -> 'Query':
        """
        OFFSET を設定
        
        Args:
            count: スキップする行数
            
        Returns:
            self (メソッドチェーン用)
        """
        self.offset_count = count
        return self
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        クエリを実行
        
        Returns:
            検索結果のリスト
        """
        # テーブルデータを取得
        table_data = self.db.tables[self.table_name]['data']
        schema = self.db.tables[self.table_name]['schema']
        
        # WHERE条件でフィルタリング
        filtered_data = []
        for record in table_data:
            if self._matches_where_conditions(record):
                filtered_data.append(record)
        
        # ORDER BY でソート
        if self.order_by_field:
            try:
                filtered_data.sort(
                    key=lambda x: x.get(self.order_by_field),
                    reverse=self.order_by_desc
                )
            except TypeError:
                # 比較できない型が混在している場合
                pass
        
        # OFFSET と LIMIT を適用
        start_index = self.offset_count
        end_index = None
        if self.limit_count:
            end_index = start_index + self.limit_count
        
        result_data = filtered_data[start_index:end_index]
        
        # フィールド選択
        if self.fields:
            selected_data = []
            for record in result_data:
                selected_record = {}
                for field in self.fields:
                    if field in record:
                        selected_record[field] = record[field]
                selected_data.append(selected_record)
            return selected_data
        else:
            return result_data
    
    def count(self) -> int:
        """
        条件に一致する行数を取得
        
        Returns:
            行数
        """
        table_data = self.db.tables[self.table_name]['data']
        count = 0
        for record in table_data:
            if self._matches_where_conditions(record):
                count += 1
        return count
    
    def first(self) -> Optional[Dict[str, Any]]:
        """
        最初の1行を取得
        
        Returns:
            最初の行 (存在しない場合はNone)
        """
        results = self.limit(1).execute()
        return results[0] if results else None
    
    def _matches_where_conditions(self, record: Dict[str, Any]) -> bool:
        """
        レコードがWHERE条件に一致するかチェック
        
        Args:
            record: チェックするレコード
            
        Returns:
            一致する場合True
        """
        for condition in self.where_conditions:
            if condition.get('type') == 'function':
                if not condition['function'](record):
                    return False
            else:
                field = condition['field']
                operator = condition['operator']
                value = condition['value']
                
                if field not in record:
                    return False
                
                record_value = record[field]
                
                if not self._compare_values(record_value, operator, value):
                    return False
        
        return True
    
    def _compare_values(self, record_value: Any, operator: str, compare_value: Any) -> bool:
        """
        値を比較
        
        Args:
            record_value: レコードの値
            operator: 演算子
            compare_value: 比較値
            
        Returns:
            比較結果
        """
        try:
            if operator == '=':
                return record_value == compare_value
            elif operator == '!=':
                return record_value != compare_value
            elif operator == '>':
                return record_value > compare_value
            elif operator == '<':
                return record_value < compare_value
            elif operator == '>=':
                return record_value >= compare_value
            elif operator == '<=':
                return record_value <= compare_value
            elif operator == 'like':
                if isinstance(record_value, str) and isinstance(compare_value, str):
                    return compare_value.lower() in record_value.lower()
                return False
            elif operator == 'in':
                if isinstance(compare_value, (list, tuple)):
                    return record_value in compare_value
                return False
            else:
                return False
        except (TypeError, ValueError):
            return False