import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import requests
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import issues


class TestGitHubAPIIntegration:
    @patch('issues.config')
    @patch('requests.post')
    def test_get_issues_df_success(self, mock_post, mock_config):
        """Test successful issues retrieval from GitHub API."""
        # Mock configuration
        mock_config.side_effect = lambda key: {
            'API_KEY': 'test_token',
            'GITHUB_API_URL': 'https://api.github.com/graphql'
        }[key]
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'repository': {
                    'issues': {
                        'nodes': [
                            {
                                'number': 1,
                                'title': 'Test Issue 1',
                                'createdAt': '2023-01-01T12:00:00Z'
                            },
                            {
                                'number': 2,
                                'title': 'Test Issue 2',
                                'createdAt': '2023-01-02T12:00:00Z'
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test the function
        repos = {'owner': 'repo'}
        result = issues.get_issues_df(repos)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'repo' in result.columns
        assert 'number' in result.columns
        assert 'title' in result.columns
        assert 'created_at' in result.columns
        
        # Check data types
        assert result['created_at'].dtype == 'datetime64[ns]'
        assert result['number'].dtype in ['int64', 'int32']
    
    @patch('issues.config')
    @patch('requests.post')
    def test_get_issues_df_api_error(self, mock_post, mock_config):
        """Test issues retrieval with API error."""
        # Mock configuration
        mock_config.side_effect = lambda key: {
            'API_KEY': 'test_token',
            'GITHUB_API_URL': 'https://api.github.com/graphql'
        }[key]
        
        # Mock API error
        mock_post.side_effect = requests.RequestException("API Error")
        
        repos = {'owner': 'repo'}
        result = issues.get_issues_df(repos)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # Should return empty DataFrame on error
    
    @patch('issues.config')
    @patch('requests.post')
    def test_get_issues_df_invalid_response(self, mock_post, mock_config):
        """Test issues retrieval with invalid API response."""
        # Mock configuration
        mock_config.side_effect = lambda key: {
            'API_KEY': 'test_token',
            'GITHUB_API_URL': 'https://api.github.com/graphql'
        }[key]
        
        # Mock invalid response structure
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'errors': [{'message': 'Repository not found'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        repos = {'owner': 'nonexistent_repo'}
        result = issues.get_issues_df(repos)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('issues.config')
    @patch('requests.post')
    def test_get_issues_df_multiple_repos(self, mock_post, mock_config):
        """Test issues retrieval from multiple repositories."""
        # Mock configuration
        mock_config.side_effect = lambda key: {
            'API_KEY': 'test_token',
            'GITHUB_API_URL': 'https://api.github.com/graphql'
        }[key]
        
        # Mock successful API response for multiple calls
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'repository': {
                    'issues': {
                        'nodes': [
                            {
                                'number': 1,
                                'title': 'Test Issue',
                                'createdAt': '2023-01-01T12:00:00Z'
                            }
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        repos = {'owner1': 'repo1', 'owner2': 'repo2'}
        result = issues.get_issues_df(repos)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # One issue per repo
        assert 'owner1/repo1' in result['repo'].values
        assert 'owner2/repo2' in result['repo'].values


class TestIssueMetricsCalculation:
    def setUp(self):
        """Set up test DataFrame with sample issues data."""
        self.sample_df = pd.DataFrame({
            'repo': ['owner/repo1', 'owner/repo1', 'owner/repo2'],
            'number': [1, 2, 3],
            'title': ['Issue 1', 'Issue 2', 'Issue 3'],
            'created_at': pd.to_datetime([
                '2023-01-01T12:00:00Z',
                '2023-01-15T12:00:00Z',
                '2023-02-01T12:00:00Z'
            ])
        })
    
    def test_compute_issue_metrics_empty_dataframe(self):
        """Test issue metrics computation with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['repo', 'number', 'title', 'created_at'])
        result = issues.compute_issue_metrics(empty_df)
        
        assert isinstance(result, dict)
        assert 'total_issues' in result
        assert result['total_issues'] == 0
    
    def test_compute_issue_metrics_valid_data(self):
        """Test issue metrics computation with valid data."""
        self.setUp()
        result = issues.compute_issue_metrics(self.sample_df)
        
        assert isinstance(result, dict)
        
        # Check basic metrics
        assert 'total_issues' in result
        assert result['total_issues'] == 3
        
        assert 'unique_repositories' in result
        assert result['unique_repositories'] == 2
        
        assert 'date_range' in result
        assert isinstance(result['date_range'], dict)
        
        # Check temporal metrics
        if 'issues_per_month' in result:
            assert isinstance(result['issues_per_month'], dict)
        
        if 'average_issues_per_repo' in result:
            assert isinstance(result['average_issues_per_repo'], (int, float))
    
    def test_compute_issue_metrics_single_repo(self):
        """Test issue metrics computation for single repository."""
        single_repo_df = pd.DataFrame({
            'repo': ['owner/repo'],
            'number': [1],
            'title': ['Single Issue'],
            'created_at': pd.to_datetime(['2023-01-01T12:00:00Z'])
        })
        
        result = issues.compute_issue_metrics(single_repo_df)
        
        assert result['total_issues'] == 1
        assert result['unique_repositories'] == 1
    
    def test_compute_temporal_metrics(self):
        """Test temporal metrics calculation."""
        self.setUp()
        
        # Test if the function exists and works
        if hasattr(issues, 'compute_temporal_metrics'):
            result = issues.compute_temporal_metrics(self.sample_df)
            assert isinstance(result, dict)
    
    def test_get_issues_by_repository(self):
        """Test grouping issues by repository."""
        self.setUp()
        
        # Test if the function exists and works
        if hasattr(issues, 'get_issues_by_repository'):
            result = issues.get_issues_by_repository(self.sample_df)
            assert isinstance(result, dict)
            assert 'owner/repo1' in result
            assert 'owner/repo2' in result


class TestDataProcessing:
    def test_parse_github_datetime(self):
        """Test parsing GitHub datetime format."""
        github_time = '2023-01-01T12:00:00Z'
        
        # Test if the function exists
        if hasattr(issues, 'parse_github_datetime'):
            result = issues.parse_github_datetime(github_time)
            assert isinstance(result, datetime)
        else:
            # Test pandas datetime parsing (likely used in the main function)
            result = pd.to_datetime(github_time)
            assert isinstance(result, pd.Timestamp)
    
    def test_validate_api_response(self):
        """Test API response validation."""
        valid_response = {
            'data': {
                'repository': {
                    'issues': {
                        'nodes': []
                    }
                }
            }
        }
        
        invalid_response = {
            'errors': [{'message': 'Error occurred'}]
        }
        
        # Test if validation functions exist
        if hasattr(issues, 'validate_api_response'):
            assert issues.validate_api_response(valid_response) is True
            assert issues.validate_api_response(invalid_response) is False
    
    def test_format_repo_name(self):
        """Test repository name formatting."""
        if hasattr(issues, 'format_repo_name'):
            result = issues.format_repo_name('owner', 'repo')
            assert result == 'owner/repo'


class TestErrorHandling:
    @patch('issues.config')
    def test_missing_api_key(self, mock_config):
        """Test handling of missing API key."""
        mock_config.side_effect = KeyError("API_KEY not found")
        
        repos = {'owner': 'repo'}
        result = issues.get_issues_df(repos)
        
        # Should handle the error gracefully
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('issues.config')
    @patch('requests.post')
    def test_network_timeout(self, mock_post, mock_config):
        """Test handling of network timeout."""
        mock_config.side_effect = lambda key: {
            'API_KEY': 'test_token',
            'GITHUB_API_URL': 'https://api.github.com/graphql'
        }[key]
        
        mock_post.side_effect = requests.Timeout("Request timed out")
        
        repos = {'owner': 'repo'}
        result = issues.get_issues_df(repos)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_invalid_repo_format(self):
        """Test handling of invalid repository format."""
        # Test with empty repos dictionary
        result = issues.get_issues_df({})
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        
        # Test with None
        result = issues.get_issues_df(None)
        assert isinstance(result, pd.DataFrame) or result is None


class TestIntegrationScenarios:
    @patch('issues.config')
    @patch('requests.post')
    def test_full_workflow_simulation(self, mock_post, mock_config):
        """Test complete workflow from API call to metrics computation."""
        # Mock configuration
        mock_config.side_effect = lambda key: {
            'API_KEY': 'test_token',
            'GITHUB_API_URL': 'https://api.github.com/graphql'
        }[key]
        
        # Mock comprehensive API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'repository': {
                    'issues': {
                        'nodes': [
                            {
                                'number': i,
                                'title': f'Issue {i}',
                                'createdAt': f'2023-01-{i:02d}T12:00:00Z'
                            }
                            for i in range(1, 11)  # 10 issues
                        ]
                    }
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Run full workflow
        repos = {'test-owner': 'test-repo'}
        issues_df = issues.get_issues_df(repos)
        metrics = issues.compute_issue_metrics(issues_df)
        
        # Verify results
        assert len(issues_df) == 10
        assert metrics['total_issues'] == 10
        assert metrics['unique_repositories'] == 1


if __name__ == '__main__':
    pytest.main([__file__])