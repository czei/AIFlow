# Sound Notifications Guide

## Overview

The AI Software Project Management System includes cross-platform sound notifications to alert users when their input is required during automated workflows. This feature helps ensure prompt responses and prevents workflow delays.

## Features

- **Cross-platform support**: Works on macOS, Linux, and Windows
- **Multiple notification types**: Info, Warning, Critical, Success, and Blocked
- **Configurable**: Enable/disable globally or for specific events
- **Fallback mechanism**: Uses ASCII bell by default, with optional enhanced sounds
- **Integration with hooks**: Automatically notifies during workflow blocks

## Configuration

Sound notifications are configured in `src/config.py` under the `NotificationConfig` class:

```python
# Master switch for all sound notifications
SOUND_ENABLED = True

# Use chime library for better sounds (optional)
USE_CHIME = False

# Specific notification triggers
NOTIFY_ON_BLOCKED = True      # When operations are blocked
NOTIFY_ON_HUMAN_INPUT = True  # When human input required
NOTIFY_ON_EMERGENCY = True    # Emergency overrides
NOTIFY_ON_WORKFLOW_PAUSE = True  # When workflow pauses
NOTIFY_ON_ERROR = False       # On errors (can be noisy)
```

### Environment Variables

You can also configure notifications using environment variables:

```bash
# Enable/disable all sound notifications
export SOUND_NOTIFICATIONS=true

# Use chime library if available
export USE_CHIME=false

# Enable debug logging for notifications
export HOOK_DEBUG=1
```

## Installation

### Basic Setup (ASCII Bell)

The basic notification system using ASCII bell (`\a`) requires no additional installation and works on all platforms.

### Enhanced Sounds (Optional)

For better sound quality and variety, install the `chime` package:

```bash
pip install chime
```

Then enable it in configuration:
```python
USE_CHIME = True
```

## When Notifications Occur

Sound notifications are triggered in the following scenarios:

### 1. Blocked Operations
When the workflow enforcement blocks a tool usage:
- **Sound**: 2 beeps (warning level)
- **Example**: Trying to write code during planning phase

### 2. Emergency Overrides
When an emergency override is detected:
- **Sound**: 3 beeps (critical level)
- **Example**: EMERGENCY: or HOTFIX: prefixed commands

### 3. Workflow Pauses
When workflow requires human review:
- **Sound**: 2 beeps (warning level)
- **Example**: Workflow step cannot proceed automatically

### 4. Human Input Required
When system needs user decision:
- **Sound**: 1 beep (info level)
- **Example**: Ambiguous situation requiring clarification

## Testing Sound Notifications

### Manual Test

Run the sound notifier directly to test all notification types:

```bash
python src/sound_notifier.py
```

This will play each notification type with a brief description.

### Unit Tests

Run the comprehensive test suite:

```bash
python -m pytest tests/unit/test_sound_notifier.py -v
```

## Troubleshooting

### No Sound on Terminal

Some terminal emulators disable or redirect the ASCII bell. To fix:

**macOS Terminal:**
- Terminal → Preferences → Profiles → Advanced
- Enable "Audible bell"

**iTerm2:**
- Preferences → Profiles → Terminal
- Enable "Silence bell"

**Linux (GNOME Terminal):**
- Edit → Preferences → Profiles → Sound
- Enable "Terminal bell"

**VS Code Terminal:**
- Settings → Search "bell"
- Disable "Terminal Integrated Enable Bell"

### Sound Too Quiet/Loud

The ASCII bell volume is controlled by your system settings:

**macOS:**
- System Preferences → Sound → Sound Effects
- Adjust "Alert volume"

**Linux:**
- System sound preferences vary by distribution
- Check your desktop environment's sound settings

### Disabling Notifications

To temporarily disable notifications:

```bash
export SOUND_NOTIFICATIONS=false
```

Or permanently in configuration:
```python
SOUND_ENABLED = False
```

## API Reference

### SoundNotifier Class

```python
from src.sound_notifier import SoundNotifier, NotificationType

# Create notifier
notifier = SoundNotifier(enabled=True, use_chime=False)

# Send notification
notifier.notify(NotificationType.WARNING, "Operation blocked")

# Test all sounds
notifier.test_sound()
```

### Convenience Functions

```python
from src.sound_notifier import notify_blocked, notify_warning

# Notify when operation is blocked
notify_blocked("Cannot write during planning phase")

# Send warning notification
notify_warning("Review required before proceeding")
```

### Hook Integration

The hook system automatically uses notifications:

```python
# In pre_tool_use.py
if not allow:
    # This automatically plays a notification sound
    print(ResponseBuilder.deny(message, suggestions))
```

## Best Practices

1. **Don't Overuse**: Too many notifications become noise
2. **Test Terminal**: Ensure your terminal supports bell sounds
3. **Consider Context**: Critical notifications for important events only
4. **Provide Options**: Always allow users to disable sounds
5. **Debug Mode**: Use HOOK_DEBUG=1 to see notification messages

## Future Enhancements

Potential improvements for the notification system:

1. **Platform-specific sounds**: Native system sounds for each OS
2. **Custom sound files**: Allow users to specify their own sounds
3. **Visual notifications**: Desktop notifications as alternative
4. **Sound themes**: Different sound sets for different preferences
5. **Volume control**: Per-notification type volume settings