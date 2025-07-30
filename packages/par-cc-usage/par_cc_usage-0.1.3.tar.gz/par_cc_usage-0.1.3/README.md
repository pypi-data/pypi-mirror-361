# PAR CC Usage

Claude Code usage tracking tool with real-time monitoring and analysis.

[![PyPI](https://img.shields.io/pypi/v/par-cc-usage)](https://pypi.org/project/par-cc-usage/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/par-cc-usage.svg)](https://pypi.org/project/par-cc-usage/)  
![Runs on Linux | MacOS | Windows](https://img.shields.io/badge/runs%20on-Linux%20%7C%20MacOS%20%7C%20Windows-blue)
![Arch x86-63 | ARM | AppleSilicon](https://img.shields.io/badge/arch-x86--64%20%7C%20ARM%20%7C%20AppleSilicon-blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/par-cc-usage)
![PyPI - License](https://img.shields.io/pypi/l/par-cc-usage)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/probello3)

![PAR CC Usage Monitor](https://raw.githubusercontent.com/paulrobello/par_cc_usage/main/Screenshot.png)
*Real-time monitoring interface showing token usage, burn rate analytics, tool usage tracking, and project activity*

## Table of Contents

- [Features](#features)
  - [📊 Real-Time Monitoring](#-real-time-monitoring)
  - [🔥 Advanced Burn Rate Analytics](#-advanced-burn-rate-analytics)
  - [⚙️ Intelligent Block Management](#️-intelligent-block-management)
  - [🎯 Smart Features](#-smart-features)
  - [📁 File System Support](#-file-system-support)
  - [🌐 Configuration & Customization](#-configuration--customization)
  - [🔔 Notification System](#-notification-system)
  - [🛠️ Developer Tools](#️-developer-tools)
- [Installation](#installation)
- [Usage](#usage)
  - [Monitor Token Usage](#monitor-token-usage)
  - [List Usage Data](#list-usage-data)
  - [Configuration Management](#configuration-management)
  - [Cache Management](#cache-management)
  - [Webhook Notifications](#webhook-notifications)
  - [JSONL Analysis](#jsonl-analysis)
  - [Debug Commands](#debug-commands)
- [Configuration](#configuration)
  - [Directory Structure](#directory-structure)
  - [Legacy Migration](#legacy-migration)
  - [Config File Example](#config-file-example)
  - [Environment Variables](#environment-variables)
- [Display Features](#display-features)
  - [Unified Block System](#unified-block-system)
  - [Current Billing Block Identification](#current-billing-block-identification)
  - [Manual Override](#manual-override)
  - [Compact Interface](#compact-interface)
  - [Optional Session Details](#optional-session-details)
  - [Project Aggregation Mode](#project-aggregation-mode-default)
  - [Smart Token Limit Management](#smart-token-limit-management)
  - [Model Display Names and Token Multipliers](#model-display-names-and-token-multipliers)
  - [Time Format Options](#time-format-options)
  - [Project Name Customization](#project-name-customization)
  - [Webhook Notifications](#webhook-notifications-1)
- [File Locations](#file-locations)
  - [XDG Base Directory Specification](#xdg-base-directory-specification)
  - [Configuration Files](#configuration-files)
  - [Legacy File Migration](#legacy-file-migration)
  - [Environment Variable Override](#environment-variable-override)
- [Development](#development)

## Features

### 📊 Real-Time Monitoring
- **Live token tracking**: Monitor usage across all Claude Code projects in real-time
- **5-hour billing blocks**: Unified block system that accurately reflects Claude's billing structure
- **Multi-session support**: When multiple sessions are active, they share billing blocks intelligently
- **Visual progress indicators**: Real-time progress bars for current billing period

### 🔥 Advanced Burn Rate Analytics
- **Per-minute tracking**: Granular burn rate display (tokens/minute) for precise monitoring
- **Estimated completion**: Projects total usage for full 5-hour block based on current rate
- **ETA with clock time**: Shows both duration and actual time when limit will be reached
- **Smart color coding**: Visual indicators based on usage levels (green/orange/red)

### ⚙️ Intelligent Block Management
- **Smart strategy**: Intelligent algorithm that automatically selects optimal billing blocks
- **Manual override**: CLI option to set custom block start times for testing or corrections
- **Automatic detection**: Smart detection of session boundaries and billing periods
- **Gap handling**: Proper handling of inactivity periods longer than 5 hours

### 🎯 Smart Features
- **Auto-adjusting limits**: Automatically increases token limits when exceeded and saves to config
- **Deduplication**: Prevents double-counting using message and request IDs
- **Model name simplification**: Clean display names (Opus, Sonnet) for better readability
- **Session sorting**: Newest-first ordering for active sessions
- **Per-model token tracking**: Accurate token attribution with proper multipliers (Opus 5x, others 1x)

### 📁 File System Support
- **Multi-directory monitoring**: Supports both legacy (`~/.claude/projects`) and new paths
- **Efficient caching**: File position tracking to avoid re-processing entire files
- **Cache management**: Optional cache disabling for full file reprocessing
- **JSONL analysis**: Deep analysis of Claude Code data structures
- **XDG Base Directory compliance**: Uses standard Unix/Linux directory conventions
- **Legacy migration**: Automatically migrates existing config files to XDG locations

### 🌐 Configuration & Customization
- **XDG directory compliance**: Config, cache, and data files stored in standard locations
- **Automatic migration**: Legacy config files automatically moved to XDG locations
- **Timezone support**: Full timezone handling with configurable display formats
- **Time formats**: 12-hour or 24-hour time display options
- **Project name cleanup**: Strip common path prefixes for cleaner display
- **Flexible output**: Table, JSON, and CSV export formats

### 🔔 Notification System
- **Discord integration**: Webhook notifications for billing block completion
- **Smart filtering**: Only notifies for blocks with actual activity
- **Cooldown protection**: Configurable minimum time between notifications
- **Rich information**: Detailed usage statistics in notifications

### 🛠️ Developer Tools
- **Debug commands**: Comprehensive debugging tools for block calculation and timing
- **Activity analysis**: Historical activity pattern analysis
- **JSONL analyzer**: Built-in `jsonl_analyzer.py` tool for examining Claude Code data files
- **Webhook testing**: Built-in Discord and Slack webhook testing

## Installation

### Option 1: Install from PyPI (Recommended)

Using [uv](https://docs.astral.sh/uv/) (fastest):
```bash
uv tool install par-cc-usage
```

Using pip:
```bash
pip install par-cc-usage
```

After installation, you can run the tool directly:
```bash
pccu monitor
```

### Option 2: Development Installation

Clone the repository and install in development mode:

```bash
# Clone the repository
git clone https://github.com/paulrobello/par_cc_usage.git
cd par_cc_usage

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

Run the tool in development mode:
```bash
# Using uv
uv run pccu monitor

# Or using make (if available)
make run

# Or directly with Python
python -m par_cc_usage.main monitor
```

### Prerequisites

- Python 3.12 or higher
- Claude Code must be installed and have generated usage data
- [uv](https://docs.astral.sh/uv/) (recommended) or pip for installation

## Usage

### Monitor Token Usage

Monitor token usage in real-time with comprehensive options:

```bash
# Basic monitoring (5-second interval, compact display)
pccu monitor

# Enhanced monitoring with session details
pccu monitor --show-sessions

# High-frequency monitoring with custom settings
pccu monitor --interval 2 --token-limit 1000000 --show-sessions

# Monitor with custom configuration
pccu monitor --config production-config.yaml

# Testing and debugging scenarios
pccu monitor --no-cache --block-start 18:00  # Fresh scan + custom block timing
pccu monitor --block-start 14:30 --show-sessions  # Override block start time

# Production monitoring examples
pccu monitor --interval 10 --token-limit 500000  # Conservative monitoring
pccu monitor --show-sessions --config team-config.yaml  # Team dashboard
```

#### Monitor Display Features
- **Real-time updates**: Live token consumption tracking
- **Burn rate analytics**: Tokens/minute with ETA to limit (e.g., "1.2K/m ETA: 2.3h (10:45 PM)")
- **Block progress**: Visual 5-hour billing block progress with time remaining
- **Model breakdown**: Per-model token usage (Opus, Sonnet)
- **Session details**: Individual session tracking when `--show-sessions` is used

### List Usage Data

Generate usage reports:

```bash
# List all usage data (table format)
pccu list

# Output as JSON
pccu list --format json

# Output as CSV
pccu list --format csv

# Sort by different fields
pccu list --sort-by tokens
pccu list --sort-by session
pccu list --sort-by project
pccu list --sort-by time
pccu list --sort-by model

# Save to file
pccu list --output usage-report.json --format json
```

### Configuration Management

```bash
# Initialize configuration file
pccu init

# Set token limit
pccu set-limit 500000

# Use custom config file
pccu init --config my-config.yaml
```

### Cache Management

```bash
# Clear file monitoring cache
pccu clear-cache

# Clear cache with custom config
pccu clear-cache --config my-config.yaml
```

### Webhook Notifications

```bash
# Test webhook configuration (Discord and/or Slack)
pccu test-webhook

# Test with custom config file
pccu test-webhook --config my-config.yaml
```

### JSONL Analysis

The `jsonl_analyzer.py` tool helps analyze Claude Code's JSONL data files, which can be quite large with complex nested structures. This tool is essential for understanding the data format when debugging token counting issues or exploring Claude's usage patterns.

This tool is integrated into the main `pccu` CLI but can also be run standalone:

```bash
# Via the main CLI (recommended)
pccu analyze ~/.claude/projects/-Users-username-project/session-id.jsonl

# Or run standalone
uv run python -m par_cc_usage.jsonl_analyzer ~/.claude/projects/-Users-username-project/session-id.jsonl

# Analyze first N lines (useful for large files)
pccu analyze path/to/file.jsonl --max-lines 10

# Customize string truncation length for better readability
pccu analyze path/to/file.jsonl --max-length 50

# Output as JSON for programmatic processing
pccu analyze path/to/file.jsonl --json

# Example: Analyze current project's most recent session
pccu analyze ~/.claude/projects/-Users-probello-Repos-par-cc-usage/*.jsonl --max-lines 20
```

#### JSONL Analyzer Features:
- **Field discovery**: Automatically identifies all fields present in the JSONL data
- **Type information**: Shows data types for each field (string, number, object, array)
- **Smart truncation**: Long strings and arrays are truncated for readability
- **Streaming processing**: Handles large files efficiently without loading everything into memory
- **Usage analysis**: Helps identify token usage patterns and message structures

### Debug Commands

Comprehensive troubleshooting tools for billing block calculations and session timing:

```bash
# Block Analysis
pccu debug-blocks                    # Show all active billing blocks
pccu debug-blocks --show-inactive    # Include completed/inactive blocks

# Unified Block Calculation
pccu debug-unified                   # Step-by-step unified block selection trace
pccu debug-unified -e 18             # Validate against expected hour (24-hour format)
pccu debug-unified --expected-hour 14 # Alternative syntax for validation

# Activity Pattern Analysis
pccu debug-activity                  # Recent activity patterns (last 6 hours)
pccu debug-activity --hours 12      # Extended activity analysis (12 hours)
pccu debug-activity -e 18 --hours 8 # Validate expected start time with custom window

# Advanced Debugging Scenarios
pccu debug-blocks --show-inactive | grep "2025-07-08"  # Filter by specific date
pccu debug-unified --config debug.yaml -e 13           # Use debug configuration with validation
```

#### Debug Output Features
- **Block timing verification**: Confirms correct 5-hour block boundaries
- **Strategy explanation**: Shows why specific blocks were selected
- **Token calculation validation**: Verifies deduplication and aggregation
- **Activity timeline**: Chronological view of session activity
- **Configuration validation**: Confirms settings are applied correctly
- **Expected time validation**: Validates unified block calculations against expected results (24-hour format)

## Configuration

The tool supports configuration via YAML files and environment variables. Configuration files are stored in XDG Base Directory compliant locations:

### Directory Structure

- **Config**: `~/.config/par_cc_usage/config.yaml` (respects `XDG_CONFIG_HOME`)
- **Cache**: `~/.cache/par_cc_usage/` (respects `XDG_CACHE_HOME`)
- **Data**: `~/.local/share/par_cc_usage/` (respects `XDG_DATA_HOME`)

### Legacy Migration

If you have an existing `./config.yaml` file in your working directory, it will be automatically migrated to the XDG config location (`~/.config/par_cc_usage/config.yaml`) when you first run the tool.

**Migration behavior:**
- Checks for legacy config files in current directory and home directory
- Automatically copies to XDG location if XDG config doesn't exist
- Preserves all existing settings during migration
- No manual intervention required

### Config File Example

The configuration file is located at `~/.config/par_cc_usage/config.yaml`:

```yaml
projects_dir: ~/.claude/projects
polling_interval: 5
timezone: America/Los_Angeles
token_limit: 500000
cache_dir: ~/.cache/par_cc_usage  # XDG cache directory (automatically set)
disable_cache: false  # Set to true to disable file monitoring cache
recent_activity_window_hours: 5  # Hours to consider as 'recent' activity for smart strategy (matches billing cycle)
display:
  show_progress_bars: true
  show_active_sessions: false  # Default: hidden for compact display
  update_in_place: true
  refresh_interval: 1
  time_format: 24h  # Time format: '12h' for 12-hour, '24h' for 24-hour
  project_name_prefixes:  # Strip prefixes from project names for cleaner display
    - "-Users-"
    - "-home-"
  aggregate_by_project: true  # Aggregate token usage by project instead of individual sessions (default)
notifications:
  discord_webhook_url: https://discord.com/api/webhooks/your-webhook-url
  slack_webhook_url: https://hooks.slack.com/services/your-webhook-url
  notify_on_block_completion: true  # Send notification when 5-hour block completes
  cooldown_minutes: 5  # Minimum minutes between notifications
```

### Environment Variables

- `PAR_CC_USAGE_PROJECTS_DIR`: Override projects directory
- `PAR_CC_USAGE_POLLING_INTERVAL`: Set polling interval
- `PAR_CC_USAGE_TIMEZONE`: Set timezone
- `PAR_CC_USAGE_TOKEN_LIMIT`: Set token limit
- `PAR_CC_USAGE_CACHE_DIR`: Override cache directory (defaults to XDG cache directory)
- `PAR_CC_USAGE_DISABLE_CACHE`: Disable file monitoring cache ('true', '1', 'yes', 'on' for true)
- `PAR_CC_USAGE_RECENT_ACTIVITY_WINDOW_HOURS`: Hours to consider as 'recent' activity for smart strategy (default: 5)
- `PAR_CC_USAGE_SHOW_PROGRESS_BARS`: Show progress bars
- `PAR_CC_USAGE_SHOW_ACTIVE_SESSIONS`: Show active sessions
- `PAR_CC_USAGE_UPDATE_IN_PLACE`: Update display in place
- `PAR_CC_USAGE_REFRESH_INTERVAL`: Display refresh interval
- `PAR_CC_USAGE_TIME_FORMAT`: Time format ('12h' or '24h')
- `PAR_CC_USAGE_PROJECT_NAME_PREFIXES`: Comma-separated list of prefixes to strip from project names
- `PAR_CC_USAGE_AGGREGATE_BY_PROJECT`: Aggregate token usage by project instead of sessions ('true', '1', 'yes', 'on' for true)
- `PAR_CC_USAGE_DISCORD_WEBHOOK_URL`: Discord webhook URL for notifications
- `PAR_CC_USAGE_SLACK_WEBHOOK_URL`: Slack webhook URL for notifications
- `PAR_CC_USAGE_NOTIFY_ON_BLOCK_COMPLETION`: Send block completion notifications ('true', '1', 'yes', 'on' for true)
- `PAR_CC_USAGE_COOLDOWN_MINUTES`: Minimum minutes between notifications

## Display Features

### Unified Block System
When multiple Claude Code sessions are active simultaneously, they all share a single 5-hour billing block. The system intelligently determines which block timing to display based on your work patterns.

**Important**: Token counts and session displays are filtered to show only sessions with activity that overlaps with the unified block time window. This ensures the displayed totals accurately reflect what will be billed for the current 5-hour period. Sessions are included if they have any activity within the billing window, regardless of when they started.

#### Current Billing Block Identification
The system uses a **simple approach** to identify the current billing block:

**Algorithm:**
1. **Identifies active blocks** across all projects and sessions
2. **Returns the most recent active block** chronologically

**Block Activity Criteria:**
A block is considered "active" if both conditions are met:
- **Recent activity**: Time since last activity < 5 hours
- **Within block window**: Current time < block's theoretical end time (start + 5 hours)

**Key Benefits:**
- **Simple and reliable**: No complex filtering or edge case logic
- **Simple logic**: Uses straightforward rules to identify the current billing block
- **Predictable behavior**: Always selects the most recent block that has recent activity

**Example Scenario:**
- Session A: Started at 2:00 PM, last activity at 3:18 PM ✓ (active - within 5 hours)
- Session B: Started at 3:00 PM, last activity at 5:12 PM ✓ (active - within 5 hours)  
- **Result**: Current billing block starts at 3:00 PM (most recent active block)

#### Manual Override
For testing or debugging, you can override the unified block start time:

```bash
# Override unified block to start at 2:00 PM (14:00 in 24-hour format)
pccu monitor --block-start 14

# Override with timezone consideration (hour is interpreted in your configured timezone)
pccu monitor --block-start 18 --show-sessions
```

**Important**: The `--block-start` hour (0-23) is interpreted in your configured timezone and automatically converted to UTC for internal processing.

### Compact Interface
The default display shows only essential information:
- **Header**: Active projects and sessions count
- **Block Progress**: 5-hour block progress with time remaining
- **Token Usage**: Per-model token counts with burn rate metrics
  - **Burn Rate**: Displays tokens consumed per minute (e.g., "1.2K/m")
  - **Estimated Total**: Projects total usage for the full 5-hour block based on current burn rate
  - **ETA**: Shows estimated time until token limit is reached with actual clock time (e.g., "2.3h (10:45 PM)" or "45m (08:30 AM)"). ETA can extend beyond the current block into the next billing cycle

### Optional Session Details
Use `--show-sessions` or set `show_active_sessions: true` in config to view:
- Individual session information
- Project and session IDs
- Model types (Opus, Sonnet)
- Token usage per session
- Sessions sorted by newest activity first

**Session Filtering**: The sessions table displays only sessions with activity that overlaps with the current 5-hour billing window. This ensures accurate billing representation - sessions are shown if they have any activity within the unified block time window, regardless of when they started.

### Project Aggregation Mode (Default)
Project aggregation is enabled by default, showing token usage aggregated by project instead of individual sessions:
- **Project View**: Shows token usage aggregated by project instead of individual sessions
- **Simplified Table**: Removes session ID column for cleaner display
- **Same Filtering**: Uses the same unified block time window filtering as session mode
- **Model Tracking**: Shows all models used across all sessions within each project
- **Activity Sorting**: Projects sorted by their most recent activity time

**To disable project aggregation and show individual sessions:**
```yaml
display:
  aggregate_by_project: false  # Show individual sessions instead of projects
```

**Environment Variable:**
```bash
export PAR_CC_USAGE_AGGREGATE_BY_PROJECT=false
```

### Smart Token Limit Management
- **Auto-adjustment**: When current usage exceeds the configured limit, the limit is automatically increased and saved to the config file
- **Visual indicators**: Progress bars turn red when exceeding the original limit
- **Real-time updates**: Limits update immediately during monitoring

### Model Display Names and Token Multipliers
Model identifiers are simplified for better readability and include cost-based multipliers:
- `claude-opus-*` → **Opus** (5x multiplier - reflects higher cost)
- `claude-sonnet-*` → **Sonnet** (1x multiplier - baseline cost)
- Unknown/other models → **Unknown** (1x multiplier - baseline cost)

**Note**: Claude Code primarily uses Opus and Sonnet models. Any other model names (including Haiku) are normalized to "Unknown".

**Token Multiplier System:**
- **Opus tokens are multiplied by 5x** to reflect their significantly higher cost
- **All other models use 1x** (no multiplier) as the baseline
- **Per-model tracking**: Each token block maintains accurate per-model token counts with multipliers applied
- **Total calculation**: The total token count equals the sum of all individual model tokens

### Time Format Options
Configure time display format through `display.time_format` setting:
- **24h format** (default): Shows time as `14:30` and `2024-07-08 14:30:45 PDT`
- **12h format**: Shows time as `2:30 PM` and `2024-07-08 2:30:45 PM PDT`

The time format applies to:
- Real-time monitor display (header and block progress)
- List command output (time ranges)
- Block time ranges in all display modes

### Project Name Customization
Configure project name display through `display.project_name_prefixes` setting:
- **Strip common prefixes**: Remove repetitive path prefixes from project names
- **Preserve project structure**: Maintains the actual project name including dashes
- **Configurable prefixes**: Customize which prefixes to strip

**Examples:**
- Claude directory: `-Users-probello-Repos-my-awesome-project`
- With prefix `"-Users-probello-Repos-"`: Shows as `my-awesome-project`
- Without prefix stripping: Shows as `-Users-probello-Repos-my-awesome-project`

**Configuration:**
```yaml
display:
  project_name_prefixes:
    - "-Users-probello-Repos-"  # Strip your repos path
    - "-home-user-"             # Strip alternative home paths
```

**Environment Variable:**
```bash
export PAR_CC_USAGE_PROJECT_NAME_PREFIXES="-Users-probello-Repos-,-home-user-"
```

### Webhook Notifications

PAR CC Usage can send webhook notifications to Discord and/or Slack when 5-hour billing blocks complete, helping you stay aware of your usage patterns and costs.

#### Discord Setup

1. **Create Discord Webhook**: 
   - Go to your Discord server settings
   - Navigate to Integrations > Webhooks
   - Create a new webhook and copy the URL

2. **Configure Discord Webhook**:
   ```yaml
   notifications:
     discord_webhook_url: https://discord.com/api/webhooks/your-webhook-url
     notify_on_block_completion: true
     cooldown_minutes: 5
   ```

   Or via environment variable:
   ```bash
   export PAR_CC_USAGE_DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your-webhook-url"
   ```

#### Slack Setup

1. **Create Slack Webhook**:
   - Go to your Slack workspace settings
   - Navigate to Apps > Incoming Webhooks
   - Create a new webhook and copy the URL

2. **Configure Slack Webhook**:
   ```yaml
   notifications:
     slack_webhook_url: https://hooks.slack.com/services/your-webhook-url
     notify_on_block_completion: true
     cooldown_minutes: 5
   ```

   Or via environment variable:
   ```bash
   export PAR_CC_USAGE_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/your-webhook-url"
   ```

#### Multiple Webhooks

You can configure both Discord and Slack webhooks simultaneously:

```yaml
notifications:
  discord_webhook_url: https://discord.com/api/webhooks/your-discord-webhook
  slack_webhook_url: https://hooks.slack.com/services/your-slack-webhook
  notify_on_block_completion: true
  cooldown_minutes: 5
```

#### Test Configuration

```bash
# Test all configured webhooks
pccu test-webhook
```

#### Notification Features

- **Block Completion Alerts**: Notifications sent when a 5-hour block completes
- **Activity Filtering**: Only sends notifications for blocks that had activity (token usage > 0)
- **One-Time Sending**: Each block completion notification is sent only once
- **Cooldown Protection**: Configurable minimum time between notifications (default: 5 minutes)
- **Rich Information**: Includes token usage, duration, limit status, and time ranges
- **Smart Coloring**: Visual indicators based on token limit usage (green/orange/red)

#### Notification Content

Each notification includes:
- **Block Duration**: How long the block lasted
- **Token Usage**: Active and total token counts
- **Limit Status**: Percentage of configured limit used
- **Time Range**: Start and end times in your configured timezone
- **Visual Indicators**: Color-coded based on usage levels

#### Configuration Options

- `discord_webhook_url`: Discord webhook URL (optional - for Discord notifications)
- `slack_webhook_url`: Slack webhook URL (optional - for Slack notifications)
- `notify_on_block_completion`: Enable/disable block completion notifications (default: true)
- `cooldown_minutes`: Minimum minutes between notifications (default: 5)

## File Locations

### XDG Base Directory Specification

PAR CC Usage follows the XDG Base Directory Specification for proper file organization:

| Directory | Default Location | Environment Variable | Purpose |
|-----------|------------------|---------------------|----------|
| Config | `~/.config/par_cc_usage/` | `XDG_CONFIG_HOME` | Configuration files |
| Cache | `~/.cache/par_cc_usage/` | `XDG_CACHE_HOME` | File monitoring cache |
| Data | `~/.local/share/par_cc_usage/` | `XDG_DATA_HOME` | Application data |

### Configuration Files

- **Main config**: `~/.config/par_cc_usage/config.yaml`
- **Cache file**: `~/.cache/par_cc_usage/file_states.json`

### Legacy File Migration

The tool automatically migrates configuration files from legacy locations:

- `./config.yaml` (current working directory)
- `~/.par_cc_usage/config.yaml` (home directory)

Migration happens automatically on first run if:
1. Legacy config file exists
2. XDG config file doesn't exist
3. File is copied to `~/.config/par_cc_usage/config.yaml`

### Environment Variable Override

You can override XDG directories using standard environment variables:

```bash
# Override config directory
export XDG_CONFIG_HOME="/custom/config/path"

# Override cache directory  
export XDG_CACHE_HOME="/custom/cache/path"

# Override data directory
export XDG_DATA_HOME="/custom/data/path"
```

## Development

```bash
# Format and lint
make checkall

# Run development mode
make dev
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
