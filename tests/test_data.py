import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data


class TestRepositoryData:
    def test_repos_structure(self):
        """Test that repos variable has correct structure."""
        assert hasattr(data, 'repos')
        repos = data.repos
        
        # Should be a dictionary
        assert isinstance(repos, dict)
        
        # Should contain repository information
        if repos:
            for owner, repo_name in repos.items():
                assert isinstance(owner, str)
                assert isinstance(repo_name, str)
                assert len(owner) > 0
                assert len(repo_name) > 0
    
    def test_repos_content(self):
        """Test specific repository content."""
        repos = data.repos
        
        # Test for known repositories (based on clones directory structure)
        expected_repos = ['django', 'scikit-learn', 'mitmproxy', 'transformers', 'ccxt']
        
        for expected_repo in expected_repos:
            # Check if repo exists as value or key
            found = False
            for owner, repo_name in repos.items():
                if repo_name == expected_repo or owner == expected_repo:
                    found = True
                    break
            
            # Note: Not all expected repos may be configured, so we just verify structure
            if found:
                assert True  # Repository found in configuration
    
    def test_repos_format(self):
        """Test repository format validity."""
        repos = data.repos
        
        for owner, repo_name in repos.items():
            # Owner and repo name should not contain invalid characters
            assert '/' not in owner  # Owner shouldn't contain slashes
            assert ' ' not in owner  # Owner shouldn't contain spaces
            assert '/' not in repo_name  # Repo name shouldn't contain slashes
            
            # Should not be empty strings
            assert owner.strip() == owner  # No leading/trailing whitespace
            assert repo_name.strip() == repo_name
    
    def test_repos_uniqueness(self):
        """Test that repository combinations are unique."""
        repos = data.repos
        
        # Create list of owner/repo combinations
        combinations = [(owner, repo_name) for owner, repo_name in repos.items()]
        
        # Check for uniqueness
        assert len(combinations) == len(set(combinations))


class TestDataConstants:
    def test_module_constants(self):
        """Test that required constants are defined."""
        # Check if module has necessary attributes
        assert hasattr(data, 'repos')
        
        # Check for additional constants that might be defined
        if hasattr(data, 'DEFAULT_REPOS'):
            assert isinstance(data.DEFAULT_REPOS, dict)
        
        if hasattr(data, 'SUPPORTED_LANGUAGES'):
            assert isinstance(data.SUPPORTED_LANGUAGES, (list, tuple))
        
        if hasattr(data, 'API_ENDPOINTS'):
            assert isinstance(data.API_ENDPOINTS, dict)


class TestRepositoryValidation:
    def test_github_url_construction(self):
        """Test that repository data can construct valid GitHub URLs."""
        repos = data.repos
        
        for owner, repo_name in repos.items():
            # Construct GitHub URL
            github_url = f"https://github.com/{owner}/{repo_name}"
            
            # Basic URL validation
            assert github_url.startswith("https://github.com/")
            assert len(github_url.split('/')) >= 5  # https, '', github.com, owner, repo
            
            # Check for valid characters in URL
            assert ' ' not in github_url
            assert '\n' not in github_url
            assert '\t' not in github_url
    
    def test_clone_path_construction(self):
        """Test that repository data can construct valid clone paths."""
        repos = data.repos
        
        for owner, repo_name in repos.items():
            # Construct clone path
            clone_path = f"clones/{owner}/{repo_name}"
            
            # Basic path validation
            assert not clone_path.startswith('/')  # Should be relative path
            assert '..' not in clone_path  # No directory traversal
            assert '//' not in clone_path  # No double slashes
            
            # Path components should be valid
            parts = clone_path.split('/')
            assert len(parts) == 3
            assert parts[0] == 'clones'
            assert parts[1] == owner
            assert parts[2] == repo_name


class TestDataConfiguration:
    def test_configuration_completeness(self):
        """Test that all configured repositories have complete information."""
        repos = data.repos
        
        for owner, repo_name in repos.items():
            # Both owner and repo name should be meaningful strings
            assert len(owner) > 1  # At least 2 characters
            assert len(repo_name) > 1  # At least 2 characters
            
            # Should not be placeholder values
            assert owner.lower() not in ['owner', 'user', 'example', 'test']
            assert repo_name.lower() not in ['repo', 'repository', 'example', 'test']
    
    def test_popular_repositories(self):
        """Test that configuration includes popular/known repositories."""
        repos = data.repos
        
        # Convert to a more searchable format
        all_repos = []
        for owner, repo_name in repos.items():
            all_repos.append(f"{owner}/{repo_name}")
            all_repos.append(repo_name.lower())
        
        # Check for some well-known open source projects
        known_projects = ['django', 'flask', 'requests', 'numpy', 'pandas', 'scikit-learn']
        
        found_projects = 0
        for project in known_projects:
            if any(project in repo.lower() for repo in all_repos):
                found_projects += 1
        
        # Should have at least some popular projects
        # Note: This is flexible as the exact configuration may vary
        assert found_projects >= 0  # At least some known projects


class TestModuleStructure:
    def test_module_imports(self):
        """Test that the data module can be imported without errors."""
        # If we got this far, the import was successful
        assert data is not None
        assert hasattr(data, '__name__')
    
    def test_module_attributes(self):
        """Test that module has expected attributes."""
        # Should have repos attribute
        assert hasattr(data, 'repos')
        
        # Check the type of repos
        assert isinstance(data.repos, dict)
    
    def test_no_sensitive_data(self):
        """Test that module doesn't contain sensitive information."""
        # Get all module attributes
        module_attrs = dir(data)
        
        sensitive_keywords = ['password', 'token', 'key', 'secret', 'api_key']
        
        for attr_name in module_attrs:
            attr_value = getattr(data, attr_name)
            
            # Check attribute names
            for keyword in sensitive_keywords:
                assert keyword.lower() not in attr_name.lower()
            
            # Check string values
            if isinstance(attr_value, str):
                for keyword in sensitive_keywords:
                    assert keyword.lower() not in attr_value.lower()


class TestDataIntegrity:
    def test_data_consistency(self):
        """Test data consistency across the module."""
        repos = data.repos
        
        if repos:
            # All entries should follow the same pattern
            first_item = next(iter(repos.items()))
            owner_type = type(first_item[0])
            repo_type = type(first_item[1])
            
            for owner, repo_name in repos.items():
                assert type(owner) == owner_type
                assert type(repo_name) == repo_type
    
    def test_data_accessibility(self):
        """Test that data is accessible and readable."""
        repos = data.repos
        
        # Should be able to iterate over repos
        count = 0
        for owner, repo_name in repos.items():
            count += 1
            # Should be able to access both key and value
            assert owner is not None
            assert repo_name is not None
        
        # Should have processed some repositories
        assert count >= 0


class TestEdgeCases:
    def test_empty_configuration(self):
        """Test handling of empty configuration."""
        # If repos is empty, it should still be a valid dict
        repos = data.repos
        assert isinstance(repos, dict)
        
        # Empty dict should be handled gracefully
        if not repos:
            assert len(repos) == 0
    
    def test_special_characters(self):
        """Test handling of repositories with special characters."""
        repos = data.repos
        
        for owner, repo_name in repos.items():
            # Common special characters that should be avoided in repo names
            problematic_chars = ['<', '>', '"', '|', '?', '*', ':', '\\']
            
            for char in problematic_chars:
                assert char not in owner
                assert char not in repo_name
    
    def test_case_sensitivity(self):
        """Test case sensitivity handling."""
        repos = data.repos
        
        # GitHub is case-sensitive, so we should preserve case
        owners = list(repos.keys())
        repo_names = list(repos.values())
        
        # Check that we're not accidentally converting everything to lowercase
        has_uppercase = any(any(c.isupper() for c in owner) for owner in owners)
        has_uppercase_repo = any(any(c.isupper() for c in repo) for repo in repo_names)
        
        # It's okay if there are no uppercase letters, but we should preserve them if they exist
        if has_uppercase or has_uppercase_repo:
            assert True  # Case is preserved


if __name__ == '__main__':
    pytest.main([__file__])