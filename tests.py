import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import zlib
import visualizer

class TestVisualizer(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="""
    app_path: /home/kvarz/projects/config_homework/hw_2/visualizer.py
    repo_path: /home/kvarz/projects/yandex-projects/second-project
    graph_path: ./
    """)
    def test_read_config(self, mock_file):
        # Проверяем чтение конфигурации из файла
        config = visualizer.read_config('config.yaml')
        self.assertEqual(config['app_tool'], '/home/kvarz/projects/config_homework/hw_2/visualizer.py')
        self.assertEqual(config['repo_path'], '/home/kvarz/projects/yandex-projects/second-project')
        self.assertEqual(config['graph_path'], './')

    @patch("os.path.join", return_value='/mocked/path')
    @patch("builtins.open", new_callable=mock_open)
    @patch("zlib.decompress", return_value=b"tree 12345\x00mock_content")
    def test_parse_object_tree(self, mock_decompress, mock_file, mock_path):
        # Проверяем парсинг дерева
        mock_config = {'repo_path': '/mocked/repo'}
        result = visualizer.parse_object('abcdef', mock_config)
        self.assertEqual(result['label'], r'Type: tree\n Hash: abcdef[:6]')
        self.assertEqual(result['children'], [])

    @patch("os.path.join", return_value="/mocked/path")
    @patch("builtins.open", new_callable=mock_open, read_data=zlib.compress(b"tree 12345\nparent 67890\n\ncommit message"))
    @patch("zlib.decompress", return_value=zlib.compress(b"tree 12345\nparent 67890\n\ncommit message"))
    def test_parse_commit(self, mock_decompress, mock_file, mock_path):
  
        mock_config = {"repo_path": "/mocked/repo"}
        
        # Применяем функцию, которая должна распарсить сжатый объект
        result = visualizer.parse_commit(b"tree 12345\nparent 67890\n\ncommit message", mock_config)
        
        # Проверяем, что мы правильно разобрали данные коммита
        self.assertEqual(result["tree"], "12345")
        self.assertEqual(result["parents"], ["67890"])
        self.assertEqual(result["message"], "commit message")

    @patch("builtins.open", new_callable=mock_open, read_data="abcdef1234567890abcdef1234567890abcdef12")
    def test_get_last_commit(self, mock_file):
        # Проверяем получение последнего коммита
        mock_config = {'repo_path': '/mocked/repo'}
        last_commit = visualizer.get_last_commit(mock_config)
        self.assertEqual(last_commit, "abcdef1234567890abcdef1234567890abcdef12")

    @patch("builtins.open", new_callable=mock_open)
    @patch("visualizer.parse_object")
    def test_generate_plantuml(self, mock_parse, mock_file):
        # Проверяем генерацию PlantUML файла
        mock_parse.return_value = {
            'label': 'Type: commit\n Hash: abcdef',
            'children': [
                {'label': 'Type: tree\n Hash: 123456', 'children': []}
            ]
        }
        mock_config = {'repo_path': '/mocked/repo'}
        visualizer.generate_plantuml('graph.puml', mock_config)
        mock_file.assert_called_with('graph.puml', 'w')
        handle = mock_file()
        handle.write.assert_any_call('@startuml\n')
        handle.write.assert_any_call('"Type: commit\n Hash: abcdef" --> "Type: tree\n Hash: 123456"\n')
        handle.write.assert_any_call('@enduml')

if __name__ == '__main__':
    unittest.main()
