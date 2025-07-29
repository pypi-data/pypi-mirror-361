"""
コレクションのテスト
"""

import unittest
import tempfile
import shutil
import os
from notsql.collection import Collection


class TestCollection(unittest.TestCase):
    """コレクションのテストクラス"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.collection = Collection('test_collection', self.temp_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
    
    def test_insert_one(self):
        """単一ドキュメントの挿入テスト"""
        doc = {'name': 'Alice', 'age': 30}
        doc_id = self.collection.insert_one(doc)
        
        self.assertIsNotNone(doc_id)
        self.assertEqual(self.collection.count_documents(), 1)
        
        # 挿入されたドキュメントを取得
        result = self.collection.find_one({'name': 'Alice'})
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Alice')
        self.assertEqual(result['age'], 30)
        self.assertEqual(result['_id'], doc_id)
    
    def test_insert_many(self):
        """複数ドキュメントの挿入テスト"""
        docs = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        doc_ids = self.collection.insert_many(docs)
        
        self.assertEqual(len(doc_ids), 3)
        self.assertEqual(self.collection.count_documents(), 3)
    
    def test_find_one(self):
        """単一ドキュメントの検索テスト"""
        # データを挿入
        self.collection.insert_one({'name': 'Alice', 'age': 30})
        self.collection.insert_one({'name': 'Bob', 'age': 25})
        
        # 検索
        result = self.collection.find_one({'name': 'Alice'})
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Alice')
        
        # 存在しないドキュメント
        result = self.collection.find_one({'name': 'Charlie'})
        self.assertIsNone(result)
    
    def test_find_many(self):
        """複数ドキュメントの検索テスト"""
        # データを挿入
        docs = [
            {'name': 'Alice', 'age': 30, 'city': 'Tokyo'},
            {'name': 'Bob', 'age': 25, 'city': 'Tokyo'},
            {'name': 'Charlie', 'age': 35, 'city': 'Osaka'}
        ]
        self.collection.insert_many(docs)
        
        # 全ドキュメント検索
        results = self.collection.find()
        self.assertEqual(len(results), 3)
        
        # 条件付き検索
        results = self.collection.find({'city': 'Tokyo'})
        self.assertEqual(len(results), 2)
        
        # 複雑な条件
        results = self.collection.find({'age': {'$gt': 28}})
        self.assertEqual(len(results), 2)
    
    def test_update_one(self):
        """単一ドキュメントの更新テスト"""
        # データを挿入
        self.collection.insert_one({'name': 'Alice', 'age': 30})
        
        # 更新
        updated = self.collection.update_one(
            {'name': 'Alice'},
            {'$set': {'age': 31, 'city': 'Tokyo'}}
        )
        self.assertTrue(updated)
        
        # 更新結果を確認
        result = self.collection.find_one({'name': 'Alice'})
        self.assertEqual(result['age'], 31)
        self.assertEqual(result['city'], 'Tokyo')
    
    def test_update_many(self):
        """複数ドキュメントの更新テスト"""
        # データを挿入
        docs = [
            {'name': 'Alice', 'age': 30, 'city': 'Tokyo'},
            {'name': 'Bob', 'age': 25, 'city': 'Tokyo'},
            {'name': 'Charlie', 'age': 35, 'city': 'Osaka'}
        ]
        self.collection.insert_many(docs)
        
        # 更新
        updated_count = self.collection.update_many(
            {'city': 'Tokyo'},
            {'$set': {'country': 'Japan'}}
        )
        self.assertEqual(updated_count, 2)
        
        # 更新結果を確認
        results = self.collection.find({'country': 'Japan'})
        self.assertEqual(len(results), 2)
    
    def test_delete_one(self):
        """単一ドキュメントの削除テスト"""
        # データを挿入
        self.collection.insert_one({'name': 'Alice', 'age': 30})
        self.collection.insert_one({'name': 'Bob', 'age': 25})
        
        # 削除
        deleted = self.collection.delete_one({'name': 'Alice'})
        self.assertTrue(deleted)
        self.assertEqual(self.collection.count_documents(), 1)
        
        # 削除結果を確認
        result = self.collection.find_one({'name': 'Alice'})
        self.assertIsNone(result)
    
    def test_delete_many(self):
        """複数ドキュメントの削除テスト"""
        # データを挿入
        docs = [
            {'name': 'Alice', 'age': 30, 'city': 'Tokyo'},
            {'name': 'Bob', 'age': 25, 'city': 'Tokyo'},
            {'name': 'Charlie', 'age': 35, 'city': 'Osaka'}
        ]
        self.collection.insert_many(docs)
        
        # 削除
        deleted_count = self.collection.delete_many({'city': 'Tokyo'})
        self.assertEqual(deleted_count, 2)
        self.assertEqual(self.collection.count_documents(), 1)
        
        # 削除結果を確認
        results = self.collection.find({'city': 'Tokyo'})
        self.assertEqual(len(results), 0)
    
    def test_update_operators(self):
        """更新オペレーターのテスト"""
        # データを挿入
        self.collection.insert_one({'name': 'Alice', 'age': 30, 'scores': [85, 90]})
        
        # $inc テスト
        self.collection.update_one({'name': 'Alice'}, {'$inc': {'age': 1}})
        result = self.collection.find_one({'name': 'Alice'})
        self.assertEqual(result['age'], 31)
        
        # $push テスト
        self.collection.update_one({'name': 'Alice'}, {'$push': {'scores': 95}})
        result = self.collection.find_one({'name': 'Alice'})
        self.assertEqual(result['scores'], [85, 90, 95])
        
        # $pull テスト
        self.collection.update_one({'name': 'Alice'}, {'$pull': {'scores': 90}})
        result = self.collection.find_one({'name': 'Alice'})
        self.assertEqual(result['scores'], [85, 95])
        
        # $unset テスト
        self.collection.update_one({'name': 'Alice'}, {'$unset': {'age': 1}})
        result = self.collection.find_one({'name': 'Alice'})
        self.assertNotIn('age', result)
    
    def test_sorting(self):
        """ソートのテスト"""
        # データを挿入
        docs = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        self.collection.insert_many(docs)
        
        # 昇順ソート
        results = self.collection.find({}, sort={'age': 1})
        ages = [doc['age'] for doc in results]
        self.assertEqual(ages, [25, 30, 35])
        
        # 降順ソート
        results = self.collection.find({}, sort={'age': -1})
        ages = [doc['age'] for doc in results]
        self.assertEqual(ages, [35, 30, 25])
    
    def test_limit_and_skip(self):
        """リミットとスキップのテスト"""
        # データを挿入
        docs = [{'name': f'User{i}', 'age': 20 + i} for i in range(10)]
        self.collection.insert_many(docs)
        
        # リミットテスト
        results = self.collection.find({}, limit=5)
        self.assertEqual(len(results), 5)
        
        # スキップテスト
        results = self.collection.find({}, skip=3, limit=5)
        self.assertEqual(len(results), 5)
    
    def test_index_creation(self):
        """インデックス作成のテスト"""
        # インデックス作成
        success = self.collection.create_index('name')
        self.assertTrue(success)
        
        # インデックスリストの確認
        indexes = self.collection.list_indexes()
        self.assertIn('name', indexes)
        
        # 重複インデックス作成
        success = self.collection.create_index('name')
        self.assertFalse(success)
        
        # ユニークインデックス作成
        success = self.collection.create_index('email', unique=True)
        self.assertTrue(success)
    
    def test_unique_index_constraint(self):
        """ユニークインデックス制約のテスト"""
        # ユニークインデックス作成
        self.collection.create_index('email', unique=True)
        
        # 最初の挿入は成功
        self.collection.insert_one({'name': 'Alice', 'email': 'alice@example.com'})
        
        # 重複する値での挿入は失敗
        with self.assertRaises(ValueError):
            self.collection.insert_one({'name': 'Bob', 'email': 'alice@example.com'})


if __name__ == '__main__':
    unittest.main()