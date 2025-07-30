#!/usr/bin/env python3
"""
SoundNotifier - Cross-platform sound notification system.

Provides audio notifications when human input is required during
automated workflows. Works on macOS, Linux, and Windows.
"""

import sys
import os
from typing import Optional, Dict, Any
from enum import Enum


class NotificationType(Enum):
    """Types of notifications with different urgency levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"
    BLOCKED = "blocked"


class SoundNotifier:
    """
    Cross-platform sound notification system.
    
    Provides multiple notification methods:
    1. ASCII bell character (universal fallback)
    2. Chime library (optional, better sounds)
    3. Platform-specific solutions (future enhancement)
    """
    
    def __init__(self, enabled: bool = True, use_chime: bool = False, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the sound notifier.
        
        Args:
            enabled: Whether sound notifications are enabled
            use_chime: Whether to use the chime library if available
            config: Optional configuration dictionary
        """
        self.enabled = enabled
        self.use_chime = use_chime
        self.chime_available = False
        self.config = config or {}
        
        # Try to import chime if requested
        if use_chime:
            try:
                import chime
                chime.theme(self.config.get('chime_theme', 'material'))
                self.chime_available = True
                self._chime = chime
            except ImportError:
                self.chime_available = False
                self._chime = None
    
    def notify(self, notification_type: NotificationType = NotificationType.INFO,
               message: Optional[str] = None) -> None:
        """
        Play a notification sound.
        
        Args:
            notification_type: Type of notification to play
            message: Optional message to log with the notification
        """
        if not self.enabled:
            return
        
        # Log the notification if in debug mode
        if os.environ.get('HOOK_DEBUG') and message:
            print(f"[NOTIFICATION] {notification_type.value}: {message}", 
                  file=sys.stderr)
        
        # Play sound based on available method
        if self.use_chime and self.chime_available:
            self._play_chime_sound(notification_type)
        else:
            self._play_bell_sound(notification_type)
    
    def _play_chime_sound(self, notification_type: NotificationType) -> None:
        """Play sound using the chime library."""
        try:
            if notification_type == NotificationType.CRITICAL:
                self._chime.error()
            elif notification_type == NotificationType.WARNING:
                self._chime.warning()
            elif notification_type == NotificationType.SUCCESS:
                self._chime.success()
            elif notification_type == NotificationType.BLOCKED:
                # Use warning sound for blocked operations
                self._chime.warning()
            else:
                self._chime.info()
        except Exception:
            # Fallback to bell if chime fails
            self._play_bell_sound(notification_type)
    
    def _play_bell_sound(self, notification_type: NotificationType) -> None:
        """Play sound using ASCII bell character."""
        # Different patterns for different notification types
        if notification_type == NotificationType.CRITICAL:
            # Three bells for critical
            for _ in range(3):
                print('\a', end='', file=sys.stderr, flush=True)
        elif notification_type in [NotificationType.WARNING, NotificationType.BLOCKED]:
            # Two bells for warning/blocked
            for _ in range(2):
                print('\a', end='', file=sys.stderr, flush=True)
        else:
            # Single bell for info/success
            print('\a', end='', file=sys.stderr, flush=True)
    
    def enable(self) -> None:
        """Enable sound notifications."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable sound notifications."""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.enabled
    
    def test_sound(self) -> None:
        """Test all notification sounds."""
        if not self.enabled:
            print("Sound notifications are disabled", file=sys.stderr)
            return
        
        print("Testing notification sounds...", file=sys.stderr)
        for notification_type in NotificationType:
            print(f"Playing {notification_type.value} sound...", file=sys.stderr)
            self.notify(notification_type)
            # Small delay between sounds
            import time
            time.sleep(0.5)


# Global instance for convenience
_notifier = None


def get_notifier() -> SoundNotifier:
    """Get or create the global notifier instance."""
    global _notifier
    if _notifier is None:
        # Load configuration from environment or defaults
        enabled = os.environ.get('SOUND_NOTIFICATIONS', 'true').lower() == 'true'
        use_chime = os.environ.get('USE_CHIME', 'false').lower() == 'true'
        _notifier = SoundNotifier(enabled=enabled, use_chime=use_chime)
    return _notifier


def notify(notification_type: NotificationType = NotificationType.INFO,
           message: Optional[str] = None) -> None:
    """
    Convenience function to send a notification.
    
    Args:
        notification_type: Type of notification to play
        message: Optional message to log with the notification
    """
    get_notifier().notify(notification_type, message)


# Convenience functions for specific notification types
def notify_blocked(message: Optional[str] = None) -> None:
    """Notify when an operation is blocked."""
    notify(NotificationType.BLOCKED, message)


def notify_warning(message: Optional[str] = None) -> None:
    """Notify with a warning sound."""
    notify(NotificationType.WARNING, message)


def notify_critical(message: Optional[str] = None) -> None:
    """Notify with a critical sound."""
    notify(NotificationType.CRITICAL, message)


def notify_success(message: Optional[str] = None) -> None:
    """Notify with a success sound."""
    notify(NotificationType.SUCCESS, message)


def notify_info(message: Optional[str] = None) -> None:
    """Notify with an info sound."""
    notify(NotificationType.INFO, message)


if __name__ == '__main__':
    # Test the notifier when run directly
    print("Sound Notifier Test", file=sys.stderr)
    print("-" * 40, file=sys.stderr)
    
    notifier = SoundNotifier(enabled=True, use_chime=False)
    notifier.test_sound()