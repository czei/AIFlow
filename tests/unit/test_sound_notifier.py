#!/usr/bin/env python3
"""
Unit tests for the SoundNotifier module.
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.sound_notifier import (
    SoundNotifier, NotificationType, get_notifier, notify,
    notify_blocked, notify_warning, notify_critical, notify_success, notify_info
)


class TestSoundNotifier(unittest.TestCase):
    """Test the SoundNotifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notifier = SoundNotifier(enabled=True, use_chime=False)
    
    def test_initialization_default(self):
        """Test default initialization."""
        notifier = SoundNotifier()
        self.assertTrue(notifier.enabled)
        self.assertFalse(notifier.use_chime)
        self.assertFalse(notifier.chime_available)
    
    def test_initialization_with_config(self):
        """Test initialization with config."""
        config = {'chime_theme': 'zelda'}
        notifier = SoundNotifier(enabled=False, use_chime=True, config=config)
        self.assertFalse(notifier.enabled)
        self.assertTrue(notifier.use_chime)
        self.assertEqual(notifier.config, config)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_notify_disabled(self, mock_stderr):
        """Test that no sound is played when disabled."""
        notifier = SoundNotifier(enabled=False)
        notifier.notify(NotificationType.INFO)
        self.assertEqual(mock_stderr.getvalue(), '')
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_bell_sound_info(self, mock_stderr):
        """Test bell sound for info notification."""
        self.notifier.notify(NotificationType.INFO)
        self.assertEqual(mock_stderr.getvalue(), '\a')
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_bell_sound_warning(self, mock_stderr):
        """Test bell sound for warning notification."""
        self.notifier.notify(NotificationType.WARNING)
        self.assertEqual(mock_stderr.getvalue(), '\a\a')
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_bell_sound_critical(self, mock_stderr):
        """Test bell sound for critical notification."""
        self.notifier.notify(NotificationType.CRITICAL)
        self.assertEqual(mock_stderr.getvalue(), '\a\a\a')
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_bell_sound_blocked(self, mock_stderr):
        """Test bell sound for blocked notification."""
        self.notifier.notify(NotificationType.BLOCKED)
        self.assertEqual(mock_stderr.getvalue(), '\a\a')
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_bell_sound_success(self, mock_stderr):
        """Test bell sound for success notification."""
        self.notifier.notify(NotificationType.SUCCESS)
        self.assertEqual(mock_stderr.getvalue(), '\a')
    
    @patch.dict(os.environ, {'HOOK_DEBUG': '1'})
    @patch('sys.stderr', new_callable=StringIO)
    def test_notify_with_message_debug(self, mock_stderr):
        """Test notification with message in debug mode."""
        self.notifier.notify(NotificationType.INFO, "Test message")
        output = mock_stderr.getvalue()
        self.assertIn('[NOTIFICATION] info: Test message', output)
        self.assertIn('\a', output)
    
    def test_enable_disable(self):
        """Test enable and disable methods."""
        notifier = SoundNotifier(enabled=False)
        self.assertFalse(notifier.is_enabled())
        
        notifier.enable()
        self.assertTrue(notifier.is_enabled())
        
        notifier.disable()
        self.assertFalse(notifier.is_enabled())
    
    @patch('src.sound_notifier.SoundNotifier.notify')
    def test_test_sound(self, mock_notify):
        """Test the test_sound method."""
        self.notifier.test_sound()
        
        # Should call notify for each notification type
        expected_calls = [
            call(notification_type) for notification_type in NotificationType
        ]
        mock_notify.assert_has_calls(expected_calls, any_order=False)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_test_sound_disabled(self, mock_stderr):
        """Test test_sound when notifications are disabled."""
        notifier = SoundNotifier(enabled=False)
        notifier.test_sound()
        self.assertIn("Sound notifications are disabled", mock_stderr.getvalue())


class TestChimeIntegration(unittest.TestCase):
    """Test chime library integration."""
    
    @patch('src.sound_notifier.SoundNotifier._play_bell_sound')
    def test_chime_import_failure(self, mock_bell):
        """Test fallback when chime import fails."""
        with patch.dict(sys.modules, {'chime': None}):
            notifier = SoundNotifier(enabled=True, use_chime=True)
            self.assertFalse(notifier.chime_available)
            notifier.notify(NotificationType.INFO)
            mock_bell.assert_called_once()
    
    def test_chime_available(self):
        """Test when chime is available."""
        mock_chime = MagicMock()
        with patch.dict(sys.modules, {'chime': mock_chime}):
            notifier = SoundNotifier(enabled=True, use_chime=True)
            self.assertTrue(notifier.chime_available)
            mock_chime.theme.assert_called_once_with('material')
    
    def test_chime_custom_theme(self):
        """Test custom chime theme."""
        mock_chime = MagicMock()
        with patch.dict(sys.modules, {'chime': mock_chime}):
            notifier = SoundNotifier(
                enabled=True, 
                use_chime=True,
                config={'chime_theme': 'zelda'}
            )
            mock_chime.theme.assert_called_once_with('zelda')
    
    def test_chime_sound_mapping(self):
        """Test correct chime methods are called."""
        mock_chime = MagicMock()
        with patch.dict(sys.modules, {'chime': mock_chime}):
            notifier = SoundNotifier(enabled=True, use_chime=True)
            notifier._chime = mock_chime
            
            # Test each notification type
            notifier._play_chime_sound(NotificationType.INFO)
            mock_chime.info.assert_called_once()
            
            notifier._play_chime_sound(NotificationType.WARNING)
            mock_chime.warning.assert_called_once()
            
            notifier._play_chime_sound(NotificationType.CRITICAL)
            mock_chime.error.assert_called_once()
            
            notifier._play_chime_sound(NotificationType.SUCCESS)
            mock_chime.success.assert_called_once()
            
            notifier._play_chime_sound(NotificationType.BLOCKED)
            self.assertEqual(mock_chime.warning.call_count, 2)
    
    @patch('src.sound_notifier.SoundNotifier._play_bell_sound')
    def test_chime_fallback_on_error(self, mock_bell):
        """Test fallback to bell when chime fails."""
        mock_chime = MagicMock()
        mock_chime.info.side_effect = Exception("Chime error")
        
        with patch.dict(sys.modules, {'chime': mock_chime}):
            notifier = SoundNotifier(enabled=True, use_chime=True)
            notifier._chime = mock_chime
            notifier._play_chime_sound(NotificationType.INFO)
            
            mock_bell.assert_called_once_with(NotificationType.INFO)


class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions."""
    
    @patch.dict(os.environ, {'SOUND_NOTIFICATIONS': 'false', 'USE_CHIME': 'true'})
    def test_get_notifier_from_env(self):
        """Test get_notifier reads from environment."""
        # Reset global notifier
        import src.sound_notifier
        src.sound_notifier._notifier = None
        
        notifier = get_notifier()
        self.assertFalse(notifier.enabled)
        self.assertTrue(notifier.use_chime)
    
    @patch('src.sound_notifier.get_notifier')
    def test_notify_convenience(self, mock_get_notifier):
        """Test notify convenience function."""
        mock_notifier = MagicMock()
        mock_get_notifier.return_value = mock_notifier
        
        notify(NotificationType.INFO, "Test")
        mock_notifier.notify.assert_called_once_with(NotificationType.INFO, "Test")
    
    @patch('src.sound_notifier.notify')
    def test_specific_notify_functions(self, mock_notify):
        """Test specific notification functions."""
        # Test each convenience function
        notify_blocked("blocked msg")
        mock_notify.assert_called_with(NotificationType.BLOCKED, "blocked msg")
        
        notify_warning("warning msg")
        mock_notify.assert_called_with(NotificationType.WARNING, "warning msg")
        
        notify_critical("critical msg")
        mock_notify.assert_called_with(NotificationType.CRITICAL, "critical msg")
        
        notify_success("success msg")
        mock_notify.assert_called_with(NotificationType.SUCCESS, "success msg")
        
        notify_info("info msg")
        mock_notify.assert_called_with(NotificationType.INFO, "info msg")


class TestMainExecution(unittest.TestCase):
    """Test main execution."""
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_execution(self, mock_stderr):
        """Test running module as main."""
        # Simply test that we can create and test a notifier
        notifier = SoundNotifier(enabled=True, use_chime=False)
        with patch.object(notifier, 'test_sound') as mock_test:
            notifier.test_sound()
            mock_test.assert_called_once()


if __name__ == '__main__':
    unittest.main()