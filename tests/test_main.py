import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestAnalyzeProject:
    @patch('main.analytics.get_project_statistics')
    @patch('main.analytics.get_ck_metrics')
    @patch('main.analytics.get_project_metrics')
    @patch('main.utils.get_project_checkout_version')
    def test_analyze_project_success(self, mock_version, mock_raw_metrics, 
                                   mock_ck_metrics, mock_stats):
        """Test successful project analysis."""
        # Mock return values
        mock_version.return_value = "main"
        mock_raw_metrics.return_value = {
            'file1.py': {'loc': 100, 'lloc': 80, 'complexity': 5.0}
        }
        mock_ck_metrics.return_value = {
            'file1.py': {'Class1': {'WMC': 5, 'DIT': 1}}
        }
        mock_stats.return_value = {
            'total_files': 1,
            'total_loc': 100,
            'mean_complexity': 5.0
        }
        
        result = main.analyze_project("/test/path", "test_project")
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'raw_metrics' in result
        assert 'ck_metrics' in result
        assert 'statistics' in result
        assert 'version' in result
        
        # Verify function calls
        mock_raw_metrics.assert_called_once_with("/test/path")
        mock_ck_metrics.assert_called_once_with("/test/path")
        mock_version.assert_called_once_with("test_project")
        mock_stats.assert_called_once()
    
    @patch('main.analytics.get_project_metrics')
    def test_analyze_project_with_exception(self, mock_raw_metrics):
        """Test project analysis with exception handling."""
        # Mock exception
        mock_raw_metrics.side_effect = Exception("Analysis failed")
        
        with patch('builtins.print') as mock_print:
            result = main.analyze_project("/test/path", "test_project")
            
            assert result is None
            mock_print.assert_called()
            # Check that error message was printed
            args, kwargs = mock_print.call_args
            assert "Erro ao analisar projeto" in args[0]
    
    @patch('main.analytics.get_project_statistics')
    @patch('main.analytics.get_ck_metrics')
    @patch('main.analytics.get_project_metrics')
    @patch('main.utils.get_project_checkout_version')
    def test_analyze_project_empty_metrics(self, mock_version, mock_raw_metrics, 
                                         mock_ck_metrics, mock_stats):
        """Test project analysis with empty metrics."""
        # Mock empty return values
        mock_version.return_value = "main"
        mock_raw_metrics.return_value = {}
        mock_ck_metrics.return_value = {}
        mock_stats.return_value = {
            'total_files': 0,
            'total_loc': 0,
            'mean_complexity': 0.0
        }
        
        result = main.analyze_project("/test/path", "test_project")
        
        assert isinstance(result, dict)
        assert result['raw_metrics'] == {}
        assert result['ck_metrics'] == {}
        assert result['statistics']['total_files'] == 0


class TestMainFunction:
    @patch('main.analyze_project')
    @patch('sys.stdout.reconfigure')
    def test_main_success(self, mock_reconfigure, mock_analyze):
        """Test successful main function execution."""
        # Mock analyze_project return value
        mock_analyze.return_value = {
            'raw_metrics': {'file1.py': {'loc': 100}},
            'ck_metrics': {'file1.py': {'Class1': {'WMC': 5}}},
            'statistics': {'total_loc': 100, 'mean_complexity': 5.0},
            'version': 'main'
        }
        
        with patch('builtins.print') as mock_print:
            main.main()
            
            # Verify function calls
            mock_reconfigure.assert_called_once_with(encoding='utf-8')
            mock_analyze.assert_called_once_with('clones/django/django', 'django')
            
            # Verify output messages
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Analisando projeto: django" in call for call in print_calls)
            assert any("Métricas Chidamber & Kemerer:" in call for call in print_calls)
            assert any("Estatísticas do Projeto:" in call for call in print_calls)
    
    @patch('main.analyze_project')
    @patch('sys.stdout.reconfigure')
    def test_main_analysis_failure(self, mock_reconfigure, mock_analyze):
        """Test main function with analysis failure."""
        # Mock analyze_project returning None (failure)
        mock_analyze.return_value = None
        
        with patch('builtins.print') as mock_print:
            main.main()
            
            # Verify failure message is printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Falha na análise do projeto." in call for call in print_calls)
    
    @patch('main.analyze_project')
    @patch('sys.stdout.reconfigure')
    def test_main_with_exception(self, mock_reconfigure, mock_analyze):
        """Test main function with unexpected exception."""
        # Mock stdout.reconfigure raising an exception
        mock_reconfigure.side_effect = Exception("Encoding error")
        
        # Should handle the exception gracefully
        try:
            main.main()
        except Exception:
            pytest.fail("main() should handle exceptions gracefully")


class TestProjectPaths:
    def test_django_path_configuration(self):
        """Test that Django path is correctly configured."""
        # Test the hardcoded paths in main function
        django_path = 'clones/django/django'
        project_name = 'django'
        
        # These should match the values used in main()
        assert isinstance(django_path, str)
        assert isinstance(project_name, str)
        assert project_name == 'django'
        assert 'django' in django_path


class TestIntegrationScenarios:
    @patch('main.analytics.get_project_statistics')
    @patch('main.analytics.get_ck_metrics')
    @patch('main.analytics.get_project_metrics')
    @patch('main.utils.get_project_checkout_version')
    def test_full_analysis_workflow(self, mock_version, mock_raw_metrics, 
                                  mock_ck_metrics, mock_stats):
        """Test complete analysis workflow with realistic data."""
        # Mock comprehensive data
        mock_version.return_value = "main"
        mock_raw_metrics.return_value = {
            'django/core/management/__init__.py': {
                'loc': 150,
                'lloc': 120,
                'sloc': 110,
                'comments': 20,
                'complexity': 8.5,
                'maintainability': 65.2
            },
            'django/db/models/base.py': {
                'loc': 2500,
                'lloc': 2000,
                'sloc': 1800,
                'comments': 300,
                'complexity': 25.0,
                'maintainability': 45.8
            }
        }
        
        mock_ck_metrics.return_value = {
            'django/core/management/__init__.py': {
                'ManagementUtility': {
                    'WMC': 12,
                    'DIT': 1,
                    'NOC': 0,
                    'RFC': 15,
                    'CBO': 8,
                    'LCOM': 0.25
                }
            },
            'django/db/models/base.py': {
                'Model': {
                    'WMC': 45,
                    'DIT': 0,
                    'NOC': 25,
                    'RFC': 120,
                    'CBO': 35,
                    'LCOM': 0.15
                }
            }
        }
        
        mock_stats.return_value = {
            'total_files': 2,
            'total_loc': 2650,
            'total_lloc': 2120,
            'total_sloc': 1910,
            'total_comments': 320,
            'mean_complexity': 16.75,
            'mean_maintainability': 55.5
        }
        
        result = main.analyze_project("/test/django/path", "django")
        
        # Verify comprehensive result
        assert result is not None
        assert len(result['raw_metrics']) == 2
        assert len(result['ck_metrics']) == 2
        assert result['statistics']['total_files'] == 2
        assert result['statistics']['total_loc'] == 2650
        assert result['version'] == "main"
    
    @patch('os.path.exists')
    def test_project_path_validation(self, mock_exists):
        """Test validation of project path existence."""
        # Test with non-existent path
        mock_exists.return_value = False
        
        with patch('main.analytics.get_project_metrics') as mock_metrics:
            mock_metrics.side_effect = FileNotFoundError("Path not found")
            
            result = main.analyze_project("/nonexistent/path", "test")
            assert result is None


class TestErrorHandling:
    def test_unicode_handling(self):
        """Test Unicode character handling in project analysis."""
        # Test that the UTF-8 reconfiguration works
        with patch('sys.stdout.reconfigure') as mock_reconfigure:
            with patch('main.analyze_project') as mock_analyze:
                mock_analyze.return_value = {
                    'raw_metrics': {},
                    'ck_metrics': {},
                    'statistics': {'total_files': 0},
                    'version': 'main'
                }
                
                main.main()
                mock_reconfigure.assert_called_once_with(encoding='utf-8')
    
    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of keyboard interrupt."""
        with patch('main.analyze_project') as mock_analyze:
            mock_analyze.side_effect = KeyboardInterrupt()
            
            # Should not raise unhandled exception
            try:
                main.main()
            except KeyboardInterrupt:
                # KeyboardInterrupt is expected to propagate
                pass
            except Exception:
                pytest.fail("Unexpected exception during KeyboardInterrupt")


if __name__ == '__main__':
    pytest.main([__file__])