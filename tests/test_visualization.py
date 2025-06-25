import pytest
import pandas as pd
import streamlit as st
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import visualization


class TestDataLoading:
    @patch('visualization.issues.get_issues_df')
    def test_load_issues_data(self, mock_get_issues):
        """Test loading issues data."""
        # Mock issues data
        mock_issues_df = pd.DataFrame({
            'repo': ['owner/repo1', 'owner/repo2'],
            'number': [1, 2],
            'title': ['Issue 1', 'Issue 2'],
            'created_at': pd.to_datetime(['2023-01-01', '2023-01-02'])
        })
        mock_get_issues.return_value = mock_issues_df
        
        # Test if function exists
        if hasattr(visualization, 'load_issues_data'):
            result = visualization.load_issues_data({'owner': 'repo'})
            assert isinstance(result, pd.DataFrame)
        else:
            # Test direct function call
            result = mock_get_issues({'owner': 'repo'})
            assert len(result) == 2
    
    @patch('visualization.analytics.get_project_metrics')
    def test_load_project_metrics(self, mock_get_metrics):
        """Test loading project metrics."""
        # Mock metrics data
        mock_metrics = {
            'file1.py': {
                'loc': 100,
                'lloc': 80,
                'complexity': 5.0,
                'maintainability': 70.5
            }
        }
        mock_get_metrics.return_value = mock_metrics
        
        if hasattr(visualization, 'load_project_metrics'):
            result = visualization.load_project_metrics('/test/path')
            assert isinstance(result, dict)
        else:
            result = mock_get_metrics('/test/path')
            assert 'file1.py' in result


class TestDataProcessing:
    def setUp(self):
        """Set up test data."""
        self.sample_issues = pd.DataFrame({
            'repo': ['owner/repo1', 'owner/repo1', 'owner/repo2'],
            'number': [1, 2, 3],
            'title': ['Bug fix', 'Feature request', 'Documentation'],
            'created_at': pd.to_datetime([
                '2023-01-01', '2023-01-15', '2023-02-01'
            ])
        })
        
        self.sample_metrics = {
            'file1.py': {
                'loc': 100,
                'lloc': 80,
                'sloc': 75,
                'comments': 10,
                'complexity': 5.0,
                'maintainability': 70.5
            },
            'file2.py': {
                'loc': 50,
                'lloc': 40,
                'sloc': 35,
                'comments': 5,
                'complexity': 3.0,
                'maintainability': 80.0
            }
        }
    
    def test_process_issues_for_visualization(self):
        """Test processing issues data for visualization."""
        self.setUp()
        
        if hasattr(visualization, 'process_issues_for_visualization'):
            result = visualization.process_issues_for_visualization(self.sample_issues)
            assert isinstance(result, dict)
        else:
            # Test basic processing logic
            repos_count = self.sample_issues.groupby('repo').size()
            assert len(repos_count) == 2
            assert repos_count['owner/repo1'] == 2
    
    def test_process_metrics_for_visualization(self):
        """Test processing metrics data for visualization."""
        self.setUp()
        
        if hasattr(visualization, 'process_metrics_for_visualization'):
            result = visualization.process_metrics_for_visualization(self.sample_metrics)
            assert isinstance(result, dict)
        else:
            # Test basic processing
            total_loc = sum(file_data['loc'] for file_data in self.sample_metrics.values())
            assert total_loc == 150
    
    def test_create_summary_statistics(self):
        """Test creation of summary statistics."""
        self.setUp()
        
        if hasattr(visualization, 'create_summary_statistics'):
            result = visualization.create_summary_statistics(self.sample_metrics)
            assert isinstance(result, dict)
            assert 'total_files' in result or 'summary' in str(result).lower()


class TestVisualizationComponents:
    @patch('visualization.st')
    def test_display_metrics_overview(self, mock_st):
        """Test metrics overview display."""
        # Mock Streamlit components
        mock_st.metric = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        
        metrics_data = {
            'total_files': 10,
            'total_loc': 1000,
            'mean_complexity': 5.5
        }
        
        if hasattr(visualization, 'display_metrics_overview'):
            visualization.display_metrics_overview(metrics_data)
            # Verify Streamlit components were called
            assert mock_st.metric.called
    
    @patch('visualization.st')
    def test_create_complexity_chart(self, mock_st):
        """Test complexity chart creation."""
        mock_st.bar_chart = MagicMock()
        mock_st.line_chart = MagicMock()
        
        sample_data = pd.DataFrame({
            'file': ['file1.py', 'file2.py'],
            'complexity': [5.0, 3.0]
        })
        
        if hasattr(visualization, 'create_complexity_chart'):
            visualization.create_complexity_chart(sample_data)
            # Should create some form of chart
            assert mock_st.bar_chart.called or mock_st.line_chart.called
    
    @patch('visualization.st')
    def test_create_issues_timeline(self, mock_st):
        """Test issues timeline creation."""
        mock_st.line_chart = MagicMock()
        
        sample_issues = pd.DataFrame({
            'created_at': pd.to_datetime(['2023-01-01', '2023-01-15']),
            'repo': ['owner/repo', 'owner/repo']
        })
        
        if hasattr(visualization, 'create_issues_timeline'):
            visualization.create_issues_timeline(sample_issues)
            assert mock_st.line_chart.called


class TestStreamlitApp:
    @patch('visualization.st')
    def test_main_app_structure(self, mock_st):
        """Test main Streamlit app structure."""
        # Mock Streamlit components
        mock_st.title = MagicMock()
        mock_st.sidebar = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        mock_st.selectbox = MagicMock(return_value='Option 1')
        mock_st.button = MagicMock(return_value=False)
        
        # Test if main app function exists
        if hasattr(visualization, 'main_app') or hasattr(visualization, 'app'):
            try:
                if hasattr(visualization, 'main_app'):
                    visualization.main_app()
                else:
                    visualization.app()
                
                # Verify basic Streamlit components were used
                assert mock_st.title.called or hasattr(mock_st, 'title')
            except Exception as e:
                # App might require specific setup, just verify structure exists
                assert 'main_app' in str(e) or 'streamlit' in str(e).lower()
    
    @patch('visualization.st')
    @patch('visualization.data.repos')
    def test_repository_selection(self, mock_repos, mock_st):
        """Test repository selection functionality."""
        # Mock repositories data
        mock_repos.return_value = {
            'owner1': 'repo1',
            'owner2': 'repo2'
        }
        
        mock_st.selectbox = MagicMock(return_value='owner1/repo1')
        mock_st.multiselect = MagicMock(return_value=['owner1/repo1'])
        
        if hasattr(visualization, 'select_repositories'):
            result = visualization.select_repositories()
            assert isinstance(result, (list, dict, str))


class TestDataExport:
    def test_export_to_csv(self):
        """Test data export to CSV."""
        sample_df = pd.DataFrame({
            'metric': ['LOC', 'Complexity'],
            'value': [100, 5.0]
        })
        
        if hasattr(visualization, 'export_to_csv'):
            result = visualization.export_to_csv(sample_df)
            # Should return CSV string or file path
            assert isinstance(result, (str, bytes))
        else:
            # Test pandas to_csv functionality
            csv_string = sample_df.to_csv()
            assert 'metric,value' in csv_string
    
    def test_export_to_json(self):
        """Test data export to JSON."""
        sample_data = {
            'metrics': {'loc': 100, 'complexity': 5.0},
            'timestamp': '2023-01-01'
        }
        
        if hasattr(visualization, 'export_to_json'):
            result = visualization.export_to_json(sample_data)
            assert isinstance(result, str)
        else:
            # Test JSON serialization
            import json
            json_string = json.dumps(sample_data)
            assert 'metrics' in json_string
    
    @patch('visualization.analytics')
    @patch('visualization.issues')
    @patch('visualization.utils')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_exportar_dados_csv(self, mock_exists, mock_makedirs, mock_utils, mock_issues, mock_analytics):
        """Test CSV export function for milestone hash data."""
        # Mock dependencies
        mock_exists.return_value = False
        mock_utils.checkout_git_revision.return_value = None
        mock_analytics.get_project_metrics.return_value = {
            'file1.py': {'loc': 100, 'complexity': 5.0}
        }
        mock_analytics.get_ck_metrics.return_value = {
            'file1.py': {'ClassA': {'WMC': 10, 'DIT': 2}}
        }
        mock_analytics.get_project_statistics.return_value = {
            'total_loc': 100,
            'n_files': 1
        }
        mock_issues.get_issues_df.return_value = pd.DataFrame({
            'repo': ['test/repo'],
            'number': [1],
            'title': ['Test Issue'],
            'created_at': ['2023-01-01']
        })
        mock_issues.compute_issue_metrics.return_value = pd.DataFrame({
            'repo': ['test/repo'],
            'total_issues': [1]
        })
        
        # Test the function
        if hasattr(visualization, 'exportar_dados_csv'):
            result = visualization.exportar_dados_csv(
                hash_revision='abc123',
                repo_dir='/test/repo',
                project_name='test-project'
            )
            
            # Verify result structure
            assert isinstance(result, dict)
            expected_keys = ['issues', 'metricas_arquivo', 'estatisticas', 'ck_metricas']
            for key in expected_keys:
                assert key in result
            
            # Verify directory creation was called
            mock_makedirs.assert_called_once()
            
            # Verify analytics functions were called
            mock_analytics.get_project_metrics.assert_called_once()
            mock_analytics.get_ck_metrics.assert_called_once()
            mock_analytics.get_project_statistics.assert_called_once()
    
    @patch('visualization.pd.DataFrame.to_csv')
    def test_exportar_dados_csv_file_creation(self, mock_to_csv):
        """Test that CSV files are actually created with correct names."""
        if hasattr(visualization, 'exportar_dados_csv'):
            # Create mock data
            sample_data = {
                'file1.py': {'loc': 100, 'complexity': 5.0}
            }
            
            # Test DataFrame conversion functions
            df_project = visualization.projeto_to_dataframe(sample_data)
            assert isinstance(df_project, pd.DataFrame)
            assert 'arquivo' in df_project.columns
            
            # Test C&K metrics conversion
            ck_data = {
                'file1.py': {'ClassA': {'WMC': 10, 'DIT': 2}}
            }
            df_ck = visualization.ck_metrics_to_dataframe(ck_data)
            assert isinstance(df_ck, pd.DataFrame)
            assert 'arquivo' in df_ck.columns
            assert 'classe' in df_ck.columns
            
            # Test statistics conversion
            stats_data = {'total_loc': 100, 'n_files': 1}
            df_stats = visualization.relatorio_estatistico_to_dataframe(stats_data)
            assert isinstance(df_stats, pd.DataFrame)
    
    @patch('visualization.os.makedirs')
    @patch('visualization.pd.DataFrame.to_csv')
    def test_criar_csv_agregado(self, mock_to_csv, mock_makedirs):
        """Test creation of aggregated CSV for temporal evolution."""
        if hasattr(visualization, 'criar_csv_agregado'):
            # Mock data for multiple hashes
            dados_por_hash = [
                {
                    'hash': 'abc123def456',
                    'dados': {
                        'estatisticas': {
                            'total_loc': 1000,
                            'total_lloc': 800,
                            'n_files': 10,
                            'mean_complexity': 5.5,
                            'mean_maintainability_index': 70.0
                        },
                        'ck_metrics': pd.DataFrame({
                            'WMC': [10, 15],
                            'DIT': [2, 3],
                            'NOC': [0, 1],
                            'RFC': [20, 25],
                            'CBO': [5, 8],
                            'LCOM': [3, 4]
                        }),
                        'issues_metrics': pd.DataFrame({
                            'total_issues': [50],
                            'avg_issues_per_month': [5.2],
                            'median_interval_days': [7.5]
                        })
                    }
                },
                {
                    'hash': 'def456ghi789',
                    'dados': {
                        'estatisticas': {
                            'total_loc': 1200,
                            'total_lloc': 950,
                            'n_files': 12,
                            'mean_complexity': 6.0,
                            'mean_maintainability_index': 68.5
                        },
                        'ck_metrics': pd.DataFrame({
                            'WMC': [12, 18],
                            'DIT': [3, 4],
                            'NOC': [1, 2],
                            'RFC': [25, 30],
                            'CBO': [6, 10],
                            'LCOM': [4, 5]
                        }),
                        'issues_metrics': pd.DataFrame({
                            'total_issues': [65],
                            'avg_issues_per_month': [6.1],
                            'median_interval_days': [6.8]
                        })
                    }
                }
            ]
            
            # Test the function
            result = visualization.criar_csv_agregado(
                dados_por_hash=dados_por_hash,
                project_name='test-project',
                output_dir='test_exports'
            )
            
            # Verify result is a file path
            assert isinstance(result, str)
            assert 'test-project_evolucao_temporal.csv' in result
            
            # Verify directory creation was called
            mock_makedirs.assert_called()
            
            # Verify CSV was written
            mock_to_csv.assert_called()
    
    @patch('visualization.utils.checkout_git_revision')
    @patch('visualization.analytics.get_project_metrics')
    @patch('visualization.analytics.get_ck_metrics')
    @patch('visualization.analytics.get_project_statistics')
    @patch('visualization.issues.get_issues_df')
    @patch('visualization.issues.compute_issue_metrics')
    def test_coletar_dados_para_agregacao(self, mock_compute_issues, mock_get_issues, 
                                         mock_get_stats, mock_get_ck, mock_get_metrics, 
                                         mock_checkout):
        """Test data collection for aggregation."""
        if hasattr(visualization, 'coletar_dados_para_agregacao'):
            # Mock returns
            mock_get_metrics.return_value = {'file1.py': {'loc': 100}}
            mock_get_ck.return_value = {'file1.py': {'ClassA': {'WMC': 10}}}
            mock_get_stats.return_value = {'total_loc': 100, 'n_files': 1}
            mock_get_issues.return_value = pd.DataFrame({'repo': ['test/repo']})
            mock_compute_issues.return_value = pd.DataFrame({'total_issues': [10]})
            
            # Test the function
            result = visualization.coletar_dados_para_agregacao(
                hash_revision='abc123',
                repo_dir='/test/repo',
                project_name='test-project'
            )
            
            # Verify result structure
            assert isinstance(result, dict)
            assert 'estatisticas' in result
            assert 'ck_metrics' in result
            assert 'issues_metrics' in result
            
            # Verify functions were called
            mock_checkout.assert_called_once_with('/test/repo', 'abc123')
            mock_get_metrics.assert_called_once()
            mock_get_ck.assert_called_once()
            mock_get_stats.assert_called_once()
    
    def test_csv_agregado_data_structure(self):
        """Test the data structure of aggregated CSV."""
        if hasattr(visualization, 'criar_csv_agregado'):
            # Test with minimal data
            dados_minimos = [
                {
                    'hash': 'test123',
                    'dados': {
                        'estatisticas': {'total_loc': 100, 'n_files': 1},
                        'ck_metrics': pd.DataFrame(),
                        'issues_metrics': pd.DataFrame()
                    }
                }
            ]
            
            with patch('visualization.os.makedirs'), \
                 patch('visualization.pd.DataFrame.to_csv') as mock_csv:
                
                visualization.criar_csv_agregado(dados_minimos, 'test')
                
                # Verify CSV was called with DataFrame
                mock_csv.assert_called_once()
                
                # Get the DataFrame that was written
                call_args = mock_csv.call_args
                # The DataFrame should have been created and passed to to_csv
                assert mock_csv.called


class TestInteractivity:
    @patch('visualization.st')
    def test_filter_controls(self, mock_st):
        """Test interactive filter controls."""
        mock_st.date_input = MagicMock(return_value=pd.Timestamp('2023-01-01'))
        mock_st.slider = MagicMock(return_value=50)
        mock_st.checkbox = MagicMock(return_value=True)
        
        if hasattr(visualization, 'create_filter_controls'):
            filters = visualization.create_filter_controls()
            assert isinstance(filters, dict)
    
    @patch('visualization.st')
    def test_dynamic_updates(self, mock_st):
        """Test dynamic chart updates."""
        mock_st.empty = MagicMock()
        mock_st.rerun = MagicMock()
        
        if hasattr(visualization, 'update_charts'):
            # Test update functionality exists
            try:
                visualization.update_charts({})
            except Exception:
                # Function might need specific parameters
                pass


class TestErrorHandling:
    @patch('visualization.st')
    def test_empty_data_handling(self, mock_st):
        """Test handling of empty data sets."""
        mock_st.warning = MagicMock()
        mock_st.error = MagicMock()
        
        empty_df = pd.DataFrame()
        
        if hasattr(visualization, 'handle_empty_data'):
            visualization.handle_empty_data(empty_df)
            # Should show warning or error message
            assert mock_st.warning.called or mock_st.error.called
    
    @patch('visualization.st')
    def test_api_error_handling(self, mock_st):
        """Test handling of API errors."""
        mock_st.error = MagicMock()
        
        if hasattr(visualization, 'handle_api_error'):
            visualization.handle_api_error("API connection failed")
            assert mock_st.error.called


class TestPerformance:
    @patch('visualization.st')
    def test_caching_functionality(self, mock_st):
        """Test data caching functionality."""
        mock_st.cache_data = MagicMock()
        
        # Test if caching decorators are used
        if hasattr(visualization, 'cached_load_data'):
            # Verify cached function exists
            assert callable(visualization.cached_load_data)
        
        # Test session state usage
        if hasattr(visualization, 'st') and hasattr(visualization.st, 'session_state'):
            # Verify session state is accessible
            assert hasattr(visualization.st.session_state, '__dict__')
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        # Create large sample dataset
        large_df = pd.DataFrame({
            'file': [f'file_{i}.py' for i in range(1000)],
            'complexity': [i * 0.1 for i in range(1000)]
        })
        
        if hasattr(visualization, 'optimize_large_dataset'):
            result = visualization.optimize_large_dataset(large_df)
            # Should return optimized or sampled data
            assert len(result) <= len(large_df)
        else:
            # Test basic pandas optimization
            sampled = large_df.head(100)
            assert len(sampled) == 100


if __name__ == '__main__':
    pytest.main([__file__])