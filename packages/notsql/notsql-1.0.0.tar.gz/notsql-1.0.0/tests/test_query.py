"""
クエリパーサーのテスト
"""

import unittest
from notsql.query import Query


class TestQuery(unittest.TestCase):
    """クエリパーサーのテストクラス"""
    
    def test_simple_equality(self):
        """単純な等価比較のテスト"""
        query = Query({'name': 'Alice'})
        
        # マッチするドキュメント
        doc1 = {'name': 'Alice', 'age': 30}
        self.assertTrue(query.matches(doc1))
        
        # マッチしないドキュメント
        doc2 = {'name': 'Bob', 'age': 25}
        self.assertFalse(query.matches(doc2))
    
    def test_nested_field(self):
        """ネストしたフィールドのテスト"""
        query = Query({'user.name': 'Alice'})
        
        # マッチするドキュメント
        doc1 = {'user': {'name': 'Alice', 'age': 30}}
        self.assertTrue(query.matches(doc1))
        
        # マッチしないドキュメント
        doc2 = {'user': {'name': 'Bob', 'age': 25}}
        self.assertFalse(query.matches(doc2))
    
    def test_comparison_operators(self):
        """比較オペレーターのテスト"""
        # $gt テスト
        query = Query({'age': {'$gt': 25}})
        self.assertTrue(query.matches({'age': 30}))
        self.assertFalse(query.matches({'age': 20}))
        
        # $gte テスト
        query = Query({'age': {'$gte': 25}})
        self.assertTrue(query.matches({'age': 25}))
        self.assertTrue(query.matches({'age': 30}))
        self.assertFalse(query.matches({'age': 20}))
        
        # $lt テスト
        query = Query({'age': {'$lt': 25}})
        self.assertTrue(query.matches({'age': 20}))
        self.assertFalse(query.matches({'age': 30}))
        
        # $lte テスト
        query = Query({'age': {'$lte': 25}})
        self.assertTrue(query.matches({'age': 25}))
        self.assertTrue(query.matches({'age': 20}))
        self.assertFalse(query.matches({'age': 30}))
        
        # $ne テスト
        query = Query({'age': {'$ne': 25}})
        self.assertTrue(query.matches({'age': 30}))
        self.assertFalse(query.matches({'age': 25}))
    
    def test_in_operators(self):
        """in/ninオペレーターのテスト"""
        # $in テスト
        query = Query({'age': {'$in': [25, 30, 35]}})
        self.assertTrue(query.matches({'age': 30}))
        self.assertFalse(query.matches({'age': 20}))
        
        # $nin テスト
        query = Query({'age': {'$nin': [25, 30, 35]}})
        self.assertTrue(query.matches({'age': 20}))
        self.assertFalse(query.matches({'age': 30}))
    
    def test_logical_operators(self):
        """論理オペレーターのテスト"""
        # $and テスト
        query = Query({'$and': [{'age': {'$gt': 20}}, {'name': 'Alice'}]})
        self.assertTrue(query.matches({'name': 'Alice', 'age': 30}))
        self.assertFalse(query.matches({'name': 'Bob', 'age': 30}))
        
        # $or テスト
        query = Query({'$or': [{'age': {'$gt': 40}}, {'name': 'Alice'}]})
        self.assertTrue(query.matches({'name': 'Alice', 'age': 30}))
        self.assertTrue(query.matches({'name': 'Bob', 'age': 45}))
        self.assertFalse(query.matches({'name': 'Bob', 'age': 30}))
    
    def test_regex_operator(self):
        """正規表現オペレーターのテスト"""
        query = Query({'name': {'$regex': r'^A.*'}})
        self.assertTrue(query.matches({'name': 'Alice'}))
        self.assertTrue(query.matches({'name': 'Adam'}))
        self.assertFalse(query.matches({'name': 'Bob'}))
        
        # オプション付きテスト
        query = Query({'name': {'$regex': r'^alice', '$options': 'i'}})
        self.assertTrue(query.matches({'name': 'Alice'}))
        self.assertTrue(query.matches({'name': 'alice'}))
        self.assertFalse(query.matches({'name': 'Bob'}))
    
    def test_exists_operator(self):
        """existsオペレーターのテスト"""
        query = Query({'age': {'$exists': True}})
        self.assertTrue(query.matches({'name': 'Alice', 'age': 30}))
        self.assertFalse(query.matches({'name': 'Alice'}))
        
        query = Query({'age': {'$exists': False}})
        self.assertTrue(query.matches({'name': 'Alice'}))
        self.assertFalse(query.matches({'name': 'Alice', 'age': 30}))
    
    def test_type_operator(self):
        """typeオペレーターのテスト"""
        query = Query({'age': {'$type': 'int'}})
        self.assertTrue(query.matches({'age': 30}))
        self.assertFalse(query.matches({'age': '30'}))
        
        query = Query({'name': {'$type': 'string'}})
        self.assertTrue(query.matches({'name': 'Alice'}))
        self.assertFalse(query.matches({'name': 30}))
    
    def test_array_operators(self):
        """配列オペレーターのテスト"""
        # $size テスト
        query = Query({'tags': {'$size': 3}})
        self.assertTrue(query.matches({'tags': ['a', 'b', 'c']}))
        self.assertFalse(query.matches({'tags': ['a', 'b']}))
        
        # $all テスト
        query = Query({'tags': {'$all': ['a', 'b']}})
        self.assertTrue(query.matches({'tags': ['a', 'b', 'c']}))
        self.assertFalse(query.matches({'tags': ['a', 'c']}))
        
        # $elemMatch テスト
        query = Query({'items': {'$elemMatch': {'price': {'$gt': 100}}}})
        self.assertTrue(query.matches({'items': [{'price': 50}, {'price': 150}]}))
        self.assertFalse(query.matches({'items': [{'price': 50}, {'price': 75}]}))


if __name__ == '__main__':
    unittest.main()