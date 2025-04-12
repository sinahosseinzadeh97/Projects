"""
Reverse lookup module for tracing product identifiers to upstream data.

This module provides functionality for looking up products by their identifiers
(ASIN, SKU, UPC) and tracing them to their upstream data sources.
"""

import os
import sqlite3
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import threading

class ThreadSafeSQLiteConnection:
    """
    Thread-safe SQLite connection manager.
    
    This class ensures that each thread gets its own SQLite connection,
    which is necessary because SQLite connections cannot be shared across threads.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the connection manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.local = threading.local()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a thread-local SQLite connection.
        
        Returns:
            sqlite3.Connection: Thread-local SQLite connection
        """
        if not hasattr(self.local, 'connection'):
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # Create a new connection for this thread
            self.local.connection = sqlite3.connect(self.db_path)
            self.local.connection.row_factory = sqlite3.Row
        
        return self.local.connection
    
    def close(self) -> None:
        """
        Close the thread-local connection if it exists.
        """
        if hasattr(self.local, 'connection'):
            self.local.connection.close()
            delattr(self.local, 'connection')

class ReverseLookupTool:
    """
    Tool for reverse lookup of product identifiers.
    
    This class provides functionality for looking up products by their identifiers
    (ASIN, SKU, UPC) and tracing them to their upstream data sources.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the reverse lookup tool.
        
        Args:
            db_path (str, optional): Path to the SQLite database file
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'products.db')
        
        self.db_path = db_path
        self.conn_manager = ThreadSafeSQLiteConnection(db_path)
        
        # Initialize database
        self._init_db()
    
    def initialize_database(self) -> None:
        """
        Initialize the database schema if it doesn't exist.
        This is a public method that the application calls.
        """
        # Call the internal _init_db method
        self._init_db()
    
    def _init_db(self) -> None:
        """
        Initialize the database schema if it doesn't exist.
        """
        conn = self.conn_manager.get_connection()
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            asin TEXT,
            sku TEXT,
            upc TEXT,
            title TEXT,
            description TEXT,
            category TEXT,
            price REAL,
            features TEXT,
            keywords TEXT,
            relevance_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create sources table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY,
            source_id TEXT,
            name TEXT,
            type TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create product_sources table (many-to-many relationship)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_sources (
            product_id INTEGER,
            source_id INTEGER,
            version TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (product_id, source_id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (source_id) REFERENCES sources (id)
        )
        ''')
        
        # Create related_products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS related_products (
            product_id INTEGER,
            related_product_id INTEGER,
            relationship_type TEXT,
            PRIMARY KEY (product_id, related_product_id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (related_product_id) REFERENCES products (id)
        )
        ''')
        
        # Create product_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        conn.commit()
    
    def import_products(self, products: List[Dict[str, Any]]) -> int:
        """
        Import products into the database.
        
        Args:
            products (list): List of product dictionaries
            
        Returns:
            int: Number of products imported
        """
        conn = self.conn_manager.get_connection()
        cursor = conn.cursor()
        
        count = 0
        
        for product in products:
            # Extract product data
            product_id = product.get('id', '')
            asin = product.get('asin', '')
            sku = product.get('sku', '')
            upc = product.get('upc', '')
            title = product.get('title', '')
            description = product.get('description', '')
            category = product.get('category', '')
            price = product.get('price', 0.0)
            features = json.dumps(product.get('features', ''))
            keywords = json.dumps(product.get('keywords', []))
            relevance_score = product.get('relevance_score', 0.0)
            
            # Insert product
            cursor.execute('''
            INSERT OR REPLACE INTO products
            (product_id, asin, sku, upc, title, description, category, price, features, keywords, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, asin, sku, upc, title, description, category, price, features, keywords, relevance_score))
            
            # Get product ID
            product_db_id = cursor.lastrowid
            
            # Insert source if available
            source = product.get('source', {})
            if source:
                source_id = source.get('id', '')
                source_name = source.get('name', '')
                source_type = source.get('type', '')
                source_url = source.get('url', '')
                
                cursor.execute('''
                INSERT OR REPLACE INTO sources
                (source_id, name, type, url)
                VALUES (?, ?, ?, ?)
                ''', (source_id, source_name, source_type, source_url))
                
                source_db_id = cursor.lastrowid
                
                # Link product to source
                cursor.execute('''
                INSERT OR REPLACE INTO product_sources
                (product_id, source_id, version)
                VALUES (?, ?, ?)
                ''', (product_db_id, source_db_id, source.get('version', '1.0')))
            
            # Insert related products if available
            related_products = product.get('related_products', [])
            for related in related_products:
                related_id = related.get('id', '')
                relationship_type = related.get('type', 'related')
                
                # Check if related product exists
                cursor.execute('SELECT id FROM products WHERE product_id = ?', (related_id,))
                result = cursor.fetchone()
                
                if result:
                    related_db_id = result[0]
                    
                    # Link products
                    cursor.execute('''
                    INSERT OR REPLACE INTO related_products
                    (product_id, related_product_id, relationship_type)
                    VALUES (?, ?, ?)
                    ''', (product_db_id, related_db_id, relationship_type))
            
            count += 1
        
        conn.commit()
        return count
    
    def lookup_by_asin(self, asin: str) -> Dict[str, Any]:
        """
        Look up a product by ASIN.
        
        Args:
            asin (str): ASIN to look up
            
        Returns:
            dict: Product data with upstream sources
        """
        return self._lookup_by_identifier('asin', asin)
    
    def lookup_by_sku(self, sku: str) -> Dict[str, Any]:
        """
        Look up a product by SKU.
        
        Args:
            sku (str): SKU to look up
            
        Returns:
            dict: Product data with upstream sources
        """
        return self._lookup_by_identifier('sku', sku)
    
    def lookup_by_upc(self, upc: str) -> Dict[str, Any]:
        """
        Look up a product by UPC.
        
        Args:
            upc (str): UPC to look up
            
        Returns:
            dict: Product data with upstream sources
        """
        return self._lookup_by_identifier('upc', upc)
    
    def _lookup_by_identifier(self, id_type: str, id_value: str) -> Dict[str, Any]:
        """
        Look up a product by identifier.
        
        Args:
            id_type (str): Type of identifier (asin, sku, upc)
            id_value (str): Identifier value
            
        Returns:
            dict: Product data with upstream sources
        """
        conn = self.conn_manager.get_connection()
        cursor = conn.cursor()
        
        # Get product
        cursor.execute(f'SELECT * FROM products WHERE {id_type} = ?', (id_value,))
        product_row = cursor.fetchone()
        
        if not product_row:
            return {}
        
        # Convert to dictionary
        product = dict(product_row)
        
        # Parse JSON fields
        product['features'] = json.loads(product['features']) if product['features'] else ''
        product['keywords'] = json.loads(product['keywords']) if product['keywords'] else []
        
        # Get sources
        cursor.execute('''
        SELECT s.* FROM sources s
        JOIN product_sources ps ON s.id = ps.source_id
        WHERE ps.product_id = ?
        ''', (product['id'],))
        
        sources = [dict(row) for row in cursor.fetchall()]
        product['sources'] = sources
        
        # Get related products
        cursor.execute('''
        SELECT p.*, rp.relationship_type FROM products p
        JOIN related_products rp ON p.id = rp.related_product_id
        WHERE rp.product_id = ?
        ''', (product['id'],))
        
        related_products = []
        for row in cursor.fetchall():
            related = dict(row)
            related['features'] = json.loads(related['features']) if related['features'] else ''
            related['keywords'] = json.loads(related['keywords']) if related['keywords'] else []
            related_products.append(related)
        
        product['related_products'] = related_products
        
        # Get history
        cursor.execute('''
        SELECT * FROM product_history
        WHERE product_id = ?
        ORDER BY timestamp DESC
        ''', (product['id'],))
        
        history = [dict(row) for row in cursor.fetchall()]
        product['history'] = history
        
        return product
    
    def search_products(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for products based on query parameters.
        
        Args:
            query (dict): Query parameters
            
        Returns:
            list: List of matching products
        """
        conn = self.conn_manager.get_connection()
        cursor = conn.cursor()
        
        # Build query
        sql = 'SELECT * FROM products WHERE 1=1'
        params = []
        
        # Add query conditions
        if 'category' in query and query['category']:
            sql += ' AND category = ?'
            params.append(query['category'])
        
        if 'min_price' in query:
            sql += ' AND price >= ?'
            params.append(query['min_price'])
        
        if 'max_price' in query:
            sql += ' AND price <= ?'
            params.append(query['max_price'])
        
        if 'search_term' in query and query['search_term']:
            sql += ' AND (title LIKE ? OR description LIKE ?)'
            search_term = f'%{query["search_term"]}%'
            params.extend([search_term, search_term])
        
        if 'min_relevance' in query:
            sql += ' AND relevance_score >= ?'
            params.append(query['min_relevance'])
        
        # Execute query
        cursor.execute(sql, params)
        
        # Convert to list of dictionaries
        products = []
        for row in cursor.fetchall():
            product = dict(row)
            product['features'] = json.loads(product['features']) if product['features'] else ''
            product['keywords'] = json.loads(product['keywords']) if product['keywords'] else []
            products.append(product)
        
        return products
    
    def export_to_csv(self, products: List[Dict[str, Any]], output_file: str) -> None:
        """
        Export products to a CSV file.
        
        Args:
            products (list): List of product dictionaries
            output_file (str): Path to the output CSV file
        """
        if not products:
            raise ValueError("No products to export")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Flatten nested structures for CSV export
        flattened_products = []
        for product in products:
            flat_product = product.copy()
            
            # Convert lists and dictionaries to strings
            for key, value in flat_product.items():
                if isinstance(value, (list, dict)):
                    flat_product[key] = json.dumps(value)
            
            flattened_products.append(flat_product)
        
        # Convert to DataFrame and export
        df = pd.DataFrame(flattened_products)
        df.to_csv(output_file, index=False)
        
        print(f"Exported {len(products)} products to {output_file}")
    
    def close(self) -> None:
        """
        Close the database connection.
        """
        self.conn_manager.close()
