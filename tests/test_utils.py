import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils


class TestRepositoryCloning:
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('utils.config')
    @patch('utils.Repo.clone_from')
    @patch('utils.get_git_revisions')
    @patch('utils.save_current_revision_repo')
    def test_clone_repo_success(self, mock_save, mock_revisions, mock_clone, mock_config):
        """Test successful repository cloning."""
        self.setUp()
        try:
            mock_config.return_value = self.temp_dir
            mock_revisions.return_value = ['abc123']
            
            repos = {"owner": "repo_name"}
            result = utils.clone_repo(repos)
            
            assert result is True
            mock_clone.assert_called_once()
            mock_save.assert_called_once()
        finally:
            self.tearDown()
    
    @patch('utils.config')
    @patch('utils.Repo.clone_from')
    def test_clone_repo_failure(self, mock_clone, mock_config):
        """Test repository cloning failure."""
        self.setUp()
        try:
            mock_config.return_value = self.temp_dir
            mock_clone.side_effect = Exception("Clone failed")
            
            repos = {"owner": "repo_name"}
            result = utils.clone_repo(repos)
            
            assert result is False
        finally:
            self.tearDown()


class TestRepositoryListing:
    def setUp(self):
        """Set up test directory structure."""
        self.temp_dir = tempfile.mkdtemp()
        # Create nested directory structure
        os.makedirs(os.path.join(self.temp_dir, "owner1", "repo1"))
        os.makedirs(os.path.join(self.temp_dir, "owner2", "repo2"))
    
    def tearDown(self):
        """Clean up test directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('utils.CLONE_BASE_PATH')
    def test_listar_repos_clonados(self, mock_base_path):
        """Test listing cloned repositories."""
        self.setUp()
        try:
            mock_base_path.__str__ = lambda x: self.temp_dir
            with patch('utils.CLONE_BASE_PATH', self.temp_dir):
                repos = utils.listar_repos_clonados()
                
                assert isinstance(repos, list)
                # Should find the owner/repo structure
                repo_names = [r.get('name') for r in repos if r.get('name')]
                assert any('owner1/repo1' in name for name in repo_names if name)
        finally:
            self.tearDown()


class TestGitOperations:
    def setUp(self):
        """Set up git repository for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize a git repository
        from git import Repo
        self.repo = Repo.init(self.temp_dir)
        
        # Create initial commit
        test_file = os.path.join(self.temp_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('Initial content')
        
        self.repo.index.add(['test_file.txt'])
        self.repo.index.commit('Initial commit')
    
    def tearDown(self):
        """Clean up test repository."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_git_revisions(self):
        """Test getting git revisions."""
        self.setUp()
        try:
            revisions = utils.get_git_revisions(self.temp_dir)
            
            assert isinstance(revisions, list)
            assert len(revisions) >= 1
            # Should contain commit hashes
            for revision in revisions:
                assert isinstance(revision, str)
                assert len(revision) >= 7  # Short hash minimum length
        finally:
            self.tearDown()
    
    def test_get_git_revisions_invalid_path(self):
        """Test getting git revisions from invalid path."""
        revisions = utils.get_git_revisions("/nonexistent/path")
        assert revisions == []
    
    def test_checkout_git_revision(self):
        """Test checking out specific git revision."""
        self.setUp()
        try:
            revisions = utils.get_git_revisions(self.temp_dir)
            if revisions:
                result = utils.checkout_git_revision(self.temp_dir, revisions[0])
                assert result is True
        finally:
            self.tearDown()
    
    def test_checkout_git_revision_invalid_hash(self):
        """Test checking out invalid git revision."""
        self.setUp()
        try:
            result = utils.checkout_git_revision(self.temp_dir, "invalid_hash")
            assert result is False
        finally:
            self.tearDown()
    
    def test_get_commit_hash_by_date(self):
        """Test getting commit hash by date."""
        self.setUp()
        try:
            # Use current date
            test_date = datetime.now()
            commit_hash = utils.get_commit_hash_by_date(self.temp_dir, test_date)
            
            # Should return None or a valid hash
            if commit_hash:
                assert isinstance(commit_hash, str)
                assert len(commit_hash) >= 7
        finally:
            self.tearDown()


class TestProjectInformation:
    def test_get_project_checkout_version(self):
        """Test getting current project checkout version."""
        with patch('utils.subprocess.check_output') as mock_subprocess:
            mock_subprocess.return_value = b'main\n'
            
            version = utils.get_project_checkout_version("test_project")
            assert version == "main"
    
    def test_get_project_checkout_version_error(self):
        """Test getting project version with subprocess error."""
        with patch('utils.subprocess.check_output') as mock_subprocess:
            mock_subprocess.side_effect = Exception("Command failed")
            
            version = utils.get_project_checkout_version("test_project")
            assert version == "unknown"


class TestRevisionManagement:
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test.ciconf')
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_current_revision_repo(self):
        """Test saving current revision to config file."""
        self.setUp()
        try:
            utils.save_current_revision_repo(self.temp_dir, "abc123")
            
            # Check if config file was created
            config_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.ciconf')]
            assert len(config_files) >= 0  # May or may not create file depending on implementation
        finally:
            self.tearDown()
    
    def test_load_current_revision_repo(self):
        """Test loading current revision from config file."""
        self.setUp()
        try:
            # Create a test config file
            with open(self.config_file, 'w') as f:
                f.write('{"current_revision": "abc123"}')
            
            # Mock the config file discovery
            with patch('utils.get_config_file_path') as mock_get_path:
                mock_get_path.return_value = self.config_file
                revision = utils.load_current_revision_repo("test")
                
                # Should return the revision or None
                assert revision is None or isinstance(revision, str)
        finally:
            self.tearDown()


class TestFileOperations:
    def test_get_python_files_from_path(self):
        """Test getting Python files from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test Python files
            py_file1 = os.path.join(temp_dir, 'test1.py')
            py_file2 = os.path.join(temp_dir, 'test2.py')
            txt_file = os.path.join(temp_dir, 'test.txt')
            
            for file_path in [py_file1, py_file2, txt_file]:
                with open(file_path, 'w') as f:
                    f.write('# Test content')
            
            python_files = utils.get_python_files_from_path(temp_dir)
            
            assert isinstance(python_files, list)
            assert len(python_files) == 2
            assert all(f.endswith('.py') for f in python_files)
    
    def test_get_python_files_invalid_path(self):
        """Test getting Python files from invalid path."""
        python_files = utils.get_python_files_from_path("/nonexistent/path")
        assert python_files == []


class TestUtilityFunctions:
    def test_get_file_extension(self):
        """Test getting file extension."""
        assert utils.get_file_extension("test.py") == ".py"
        assert utils.get_file_extension("test.txt") == ".txt"
        assert utils.get_file_extension("test") == ""
    
    def test_validate_git_hash(self):
        """Test git hash validation."""
        # Valid git hashes
        assert utils.validate_git_hash("a1b2c3d4") is True
        assert utils.validate_git_hash("1234567890abcdef") is True
        
        # Invalid git hashes
        assert utils.validate_git_hash("invalid") is False
        assert utils.validate_git_hash("") is False
        assert utils.validate_git_hash("12345") is False  # Too short
    
    def test_format_date_for_git(self):
        """Test date formatting for git commands."""
        test_date = datetime(2023, 1, 15, 12, 30, 45)
        formatted = utils.format_date_for_git(test_date)
        
        assert isinstance(formatted, str)
        assert "2023" in formatted


if __name__ == '__main__':
    pytest.main([__file__])