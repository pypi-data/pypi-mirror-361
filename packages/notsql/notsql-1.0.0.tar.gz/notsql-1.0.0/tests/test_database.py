"""
データベースのテスト
"""

import unittest
import tempfile
import shutil
import os
from notsql.database import NotsqlDB


class TestDatabase(unittest.TestCase):
    """データベースのテストクラス"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = NotsqlDB('test_db', self.temp_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)
    
    def test_collection_creation(self):
        """コレクション作成のテスト"""
        collection = self.db.collection('users')
        self.assertIsNotNone(collection)
        self.assertEqual(collection.name, 'users')
        
        # 同じ名前のコレクションを再取得
        collection2 = self.db.collection('users')
        self.assertIs(collection, collection2)
    
    def test_list_collections(self):
        """コレクション一覧のテスト"""
        # 最初は空
        collections = self.db.list_collections()
        self.assertEqual(len(collections), 0)
        
        # コレクションを作成してデータを挿入
        users = self.db.collection('users')
        users.insert_one({'name': 'Alice'})
        
        products = self.db.collection('products')
        products.insert_one({'name': 'Product1'})
        
        # コレクション一覧を確認
        collections = self.db.list_collections()
        self.assertEqual(len(collections), 2)
        self.assertIn('users', collections)
        self.assertIn('products', collections)
    
    def test_drop_collection(self):
        """コレクション削除のテスト"""
        # コレクション作成
        users = self.db.collection('users')
        users.insert_one({'name': 'Alice'})
        
        # コレクションが存在することを確認
        self.assertIn('users', self.db.list_collections())
        
        # コレクション削除
        success = self.db.drop_collection('users')
        self.assertTrue(success)
        
        # コレクションが削除されたことを確認
        self.assertNotIn('users', self.db.list_collections())
        
        # 存在しないコレクションの削除
        success = self.db.drop_collection('nonexistent')
        self.assertFalse(success)
    
    def test_database_stats(self):
        """データベース統計情報のテスト"""
        # データを挿入
        users = self.db.collection('users')
        users.insert_one({'name': 'Alice'})
        users.insert_one({'name': 'Bob'})
        users.create_index('name')
        
        products = self.db.collection('products')
        products.insert_one({'name': 'Product1'})
        
        # 統計情報を取得
        stats = self.db.get_stats()
        
        self.assertEqual(stats['db_name'], 'test_db')
        self.assertEqual(stats['collections']['users']['count'], 2)
        self.assertEqual(stats['collections']['products']['count'], 1)
        self.assertIn('name', stats['collections']['users']['indexes'])
    
    def test_multiple_databases(self):
        """複数データベースのテスト"""
        # 別のデータベースを作成
        db2 = NotsqlDB('test_db2', self.temp_dir)
        
        # それぞれのデータベースにデータを挿入
        self.db.collection('users').insert_one({'name': 'Alice'})
        db2.collection('users').insert_one({'name': 'Bob'})
        
        # データが分離されていることを確認
        self.assertEqual(self.db.collection('users').count_documents(), 1)
        self.assertEqual(db2.collection('users').count_documents(), 1)
        
        alice = self.db.collection('users').find_one({'name': 'Alice'})
        bob = db2.collection('users').find_one({'name': 'Bob'})
        
        self.assertIsNotNone(alice)
        self.assertIsNotNone(bob)
        self.assertIsNone(self.db.collection('users').find_one({'name': 'Bob'}))
        self.assertIsNone(db2.collection('users').find_one({'name': 'Alice'}))
    
    def test_integration_example(self):
        """統合テスト例"""
        # ユーザーコレクション
        users = self.db.collection('users')
        users.create_index('email', unique=True)
        
        # ユーザー挿入
        user_id = users.insert_one({
            'name': 'Alice',
            'email': 'alice@example.com',
            'age': 30,
            'tags': ['developer', 'python']
        })
        
        # 投稿コレクション
        posts = self.db.collection('posts')
        posts.create_index('author_id')
        
        # 投稿挿入
        post_id = posts.insert_one({
            'title': 'Hello World',
            'content': 'This is my first post',
            'author_id': user_id,
            'tags': ['hello', 'world']
        })
        
        # 複雑な検索
        # 30歳以上のユーザーを検索
        mature_users = users.find({'age': {'$gte': 30}})
        self.assertEqual(len(mature_users), 1)
        
        # 特定のタグを持つユーザーを検索
        python_users = users.find({'tags': {'$in': ['python']}})
        self.assertEqual(len(python_users), 1)
        
        # 投稿を検索
        user_posts = posts.find({'author_id': user_id})
        self.assertEqual(len(user_posts), 1)
        
        # 統計情報
        stats = self.db.get_stats()
        self.assertEqual(stats['collections']['users']['count'], 1)
        self.assertEqual(stats['collections']['posts']['count'], 1)


if __name__ == '__main__':
    unittest.main()