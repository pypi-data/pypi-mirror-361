"""
Tests for auto-installation functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from syft_awake.auto_install import (
    get_syftbox_apps_path,
    is_syftbox_running,
    is_syftbox_app_installed,
    ensure_syftbox_app_installed,
    copy_local_app_to_syftbox,
    auto_install
)


class TestAutoInstall:
    """Test auto-installation functionality."""
    
    def test_get_syftbox_apps_path_not_found(self, tmp_path):
        """Test when SyftBox directory doesn't exist."""
        with patch('syft_awake.auto_install.Path.home') as mock_home:
            mock_home.return_value = tmp_path
            result = get_syftbox_apps_path()
            assert result is None
    
    def test_get_syftbox_apps_path_found(self, tmp_path):
        """Test when SyftBox directory exists."""
        syftbox_dir = tmp_path / "SyftBox"
        syftbox_dir.mkdir()
        apps_dir = syftbox_dir / "apps"
        
        with patch('syft_awake.auto_install.Path.home') as mock_home:
            mock_home.return_value = tmp_path
            result = get_syftbox_apps_path()
            assert result == apps_dir
    
    @patch('syft_core.Client')
    def test_is_syftbox_running_success(self, mock_client_class):
        """Test when SyftBox is running successfully."""
        mock_client = Mock()
        mock_client.email = "test@example.com"
        mock_client_class.load.return_value = mock_client
        
        result = is_syftbox_running()
        assert result is True
    
    @patch('syft_core.Client')
    def test_is_syftbox_running_failure(self, mock_client_class):
        """Test when SyftBox is not running."""
        mock_client_class.load.side_effect = Exception("Connection failed")
        
        result = is_syftbox_running()
        assert result is False
    
    def test_is_syftbox_app_installed_not_found(self, tmp_path):
        """Test when app is not installed."""
        with patch('syft_awake.auto_install.get_syftbox_apps_path') as mock_path:
            mock_path.return_value = tmp_path
            result = is_syftbox_app_installed()
            assert result is False
    
    def test_is_syftbox_app_installed_found(self, tmp_path):
        """Test when app is properly installed."""
        app_dir = tmp_path / "syft-awake"
        app_dir.mkdir()
        run_sh = app_dir / "run.sh"
        run_sh.write_text("#!/bin/bash\necho test")
        
        with patch('syft_awake.auto_install.get_syftbox_apps_path') as mock_path:
            mock_path.return_value = tmp_path
            result = is_syftbox_app_installed()
            assert result is True
    
    @patch('syft_awake.auto_install.is_syftbox_running')
    @patch('syft_awake.auto_install.get_syftbox_apps_path')
    def test_ensure_syftbox_app_installed_no_syftbox(self, mock_path, mock_running):
        """Test when SyftBox is not available."""
        mock_path.return_value = None
        
        result = ensure_syftbox_app_installed()
        assert result is False
    
    @patch('syft_awake.auto_install.is_syftbox_running')
    @patch('syft_awake.auto_install.get_syftbox_apps_path')
    def test_ensure_syftbox_app_installed_not_running(self, mock_path, mock_running):
        """Test when SyftBox is not running."""
        mock_path.return_value = Path("/tmp/apps")
        mock_running.return_value = False
        
        result = ensure_syftbox_app_installed()
        assert result is False
    
    @patch('syft_awake.auto_install.is_syftbox_app_installed')
    @patch('syft_awake.auto_install.is_syftbox_running')
    @patch('syft_awake.auto_install.get_syftbox_apps_path')
    def test_ensure_syftbox_app_installed_already_installed(
        self, mock_path, mock_running, mock_installed
    ):
        """Test when app is already installed."""
        mock_path.return_value = Path("/tmp/apps")
        mock_running.return_value = True
        mock_installed.return_value = True
        
        result = ensure_syftbox_app_installed()
        assert result is True
    
    @patch('syft_awake.auto_install.copy_local_app_to_syftbox')
    @patch('syft_awake.auto_install.is_syftbox_app_installed')
    @patch('syft_awake.auto_install.is_syftbox_running')
    @patch('syft_awake.auto_install.get_syftbox_apps_path')
    def test_ensure_syftbox_app_installed_copy_success(
        self, mock_path, mock_running, mock_installed, mock_copy
    ):
        """Test successful local app copy."""
        mock_path.return_value = Path("/tmp/apps")
        mock_running.return_value = True
        mock_installed.return_value = False
        mock_copy.return_value = True
        
        result = ensure_syftbox_app_installed()
        assert result is True
        mock_copy.assert_called_once()
    
    @patch('syft_awake.auto_install.ensure_syftbox_app_installed')
    def test_auto_install_success(self, mock_ensure):
        """Test successful auto-installation."""
        mock_ensure.return_value = True
        
        result = auto_install()
        assert result is True
        mock_ensure.assert_called_once_with(silent=True)
    
    @patch('syft_awake.auto_install.ensure_syftbox_app_installed')
    def test_auto_install_failure(self, mock_ensure):
        """Test auto-installation failure."""
        mock_ensure.side_effect = Exception("Installation failed")
        
        result = auto_install()
        assert result is False
    
    def test_copy_local_app_to_syftbox_no_syftbox(self, tmp_path):
        """Test copy when SyftBox not available."""
        with patch('syft_awake.auto_install.get_syftbox_apps_path') as mock_path:
            mock_path.return_value = None
            result = copy_local_app_to_syftbox()
            assert result is False
    
    def test_copy_local_app_to_syftbox_no_local_app(self, tmp_path):
        """Test copy when local app directory doesn't have run.sh."""
        with patch('syft_awake.auto_install.get_syftbox_apps_path') as mock_path:
            mock_path.return_value = tmp_path
            
            # Mock __file__ to point to a location without run.sh
            with patch('syft_awake.auto_install.__file__', str(tmp_path / "fake_auto_install.py")):
                result = copy_local_app_to_syftbox()
                assert result is False


if __name__ == "__main__":
    pytest.main([__file__])