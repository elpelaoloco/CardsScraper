import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open

from src.utils.save_results import save_dict_as_json


class TestSaveResults:
    
    def test_save_dict_as_json_empty_data(self):
        data = {}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                save_dict_as_json(data, 'test.json')
                
        mock_file.assert_called_once_with('test.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with([], mock_file.return_value.__enter__.return_value, ensure_ascii=False, indent=4)
    
    def test_save_dict_as_json_with_data(self):
        data = {
            'store1': {
                'pokemon': [
                    {'name': 'Pikachu', 'price': 100},
                    {'name': 'Charizard', 'price': 500}
                ],
                'magic': [
                    {'name': 'Lightning Bolt', 'price': 50}
                ]
            },
            'store2': {
                'yugioh': [
                    {'name': 'Blue Eyes', 'price': 200}
                ]
            }
        }
        
        expected_product_list = [
            {'name': 'Pikachu', 'price': 100},
            {'name': 'Charizard', 'price': 500},
            {'name': 'Lightning Bolt', 'price': 50},
            {'name': 'Blue Eyes', 'price': 200}
        ]
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                save_dict_as_json(data, 'test.json')
                
        mock_json_dump.assert_called_once_with(expected_product_list, mock_file.return_value.__enter__.return_value, ensure_ascii=False, indent=4)
    
    def test_save_dict_as_json_with_empty_categories(self):
        data = {
            'store1': {
                'pokemon': [],
                'magic': [{'name': 'Card1', 'price': 10}]
            },
            'store2': {
                'yugioh': []
            }
        }
        
        expected_product_list = [
            {'name': 'Card1', 'price': 10}
        ]
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                save_dict_as_json(data, 'output.json')
                
        mock_json_dump.assert_called_once_with(expected_product_list, mock_file.return_value.__enter__.return_value, ensure_ascii=False, indent=4)
    
    def test_save_dict_as_json_real_file(self):
        data = {
            'test_store': {
                'test_game': [
                    {'name': 'Test Card', 'price': 42}
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            save_dict_as_json(data, tmp_path)
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
                
            assert result == [{'name': 'Test Card', 'price': 42}]
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)