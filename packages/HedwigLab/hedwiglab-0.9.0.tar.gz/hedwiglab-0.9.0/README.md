# Hedwig

Hedwig is a research note backup storage that synchronizes Notion content to Git repositories and generates AI summaries for team communication. It automates the workflow of tracking research progress, creating summaries, and distributing them through messaging platforms.

## Features

- **Notion Synchronization**: Automatically sync research notes from Notion to a Git repository
- **AI-Powered Summaries**: Generate intelligent summaries of research changes using LLMs
- **Team Overviews**: Create consolidated team overviews with MVP highlights
- **Multi-Platform Messaging**: Distribute summaries through various messaging platforms (currently Slack)
- **Automated Pipeline**: Run the complete workflow with a single command
- **Flexible Configuration**: Customize prompts, models, and behavior through configuration

## Installation

Install Hedwig using pip:

```bash
pip install -e /path/to/Hedwig
```

Or clone and install from source:

```bash
git clone https://github.com/ChangLabSNU/Hedwig
cd Hedwig
pip install -e .
```

## Quick Start

1. **Set up configuration**:
   ```bash
   cp config.yml.example config.yml
   # Edit config.yml with your settings
   ```

2. **Configure API keys and etc**:
   ```yaml
   # In config.yml
   api:
     notion:
       api_key: 'your-notion-api-key'
     llm:
       key: 'your-gemini-api-key'
   messaging:
     slack:
       token: 'your-slack-bot-token'
   ```

3. **Check system health** (recommended before first sync):
   ```bash
   hedwig health --config config.yml
   ```
   This verifies that all components are properly configured and accessible.

4. **Sync Notion content**:
   ```bash
   hedwig sync
   ```

5. **Run the pipeline**:
   ```bash
   hedwig pipeline
   ```

## Workflow Overview

Hedwig follows a two-stage process:

```
┌─────────────┐
│   STAGE 1   │
│ Data Update │
└─────────────┘
      │
      ▼
┌─────────────┐
│ hedwig sync │ ─── Fetches latest research notes from Notion
└─────────────┘     and commits them to Git repository
      │
      │ (Run periodically or on-demand)
      │
      ▼
┌─────────────┐
│   STAGE 2   │
│  Pipeline   │
└─────────────┘
      │
      ▼
┌──────────────────────────┐
│ hedwig pipeline          │ ─── Automated 3-step process:
└──────────────────────────┘
      │
      ├─► generate-change-summary ─── Analyzes Git commits and creates
      │                               AI summaries of recent changes
      │
      ├─► generate-overview ──────── Consolidates individual summaries
      │                              into team-focused overview
      │
      └─► post-summary ───────────── Posts to messaging platform
                                     (e.g., Slack Canvas)
```

**Important**: The `sync` command must be run before the pipeline to ensure the Git repository has the latest Notion content. The sync is NOT part of the pipeline and should be scheduled separately.

## Commands

### `hedwig health`
Checks the health of all Hedwig components and dependencies. **Recommended to run before first sync** to ensure proper setup.

```bash
hedwig health [--config CONFIG] [--quick] [--json] [--quiet]
```

**Options:**
- `--config`: Configuration file path (default: `config.yml`)
- `--quick`: Skip API connectivity tests for faster results
- `--json`: Output results in JSON format for monitoring tools
- `--quiet`: Suppress informational messages

**Health Checks Include:**
- Configuration file validity and required keys
- Git repository status and permissions
- Python package dependencies
- Filesystem permissions and disk space
- API connectivity (Notion, LLM, Slack) unless `--quick` is used

**Exit Codes:**
- `0`: All checks passed (HEALTHY)
- `1`: Some non-critical checks failed (DEGRADED)
- `2`: Critical checks failed (CRITICAL)

**Example Usage:**
```bash
# Full health check before first sync
hedwig health --config config.yml

# Quick check (skip API tests)
hedwig health --quick

# JSON output for monitoring
hedwig health --json | jq '.overall_status'
```

### `hedwig sync`
Synchronizes Notion pages to a Git repository.

```bash
hedwig sync [--config CONFIG] [--quiet] [--verbose]
```

**Options:**
- `--config`: Configuration file path (default: `config.yml`)
- `--quiet`: Suppress progress messages
- `--verbose`: Show detailed debug output

### `hedwig sync-userlist`
Manually syncs user list from Notion and saves to TSV file. This command is typically not needed in regular workflows as it's automatically triggered when unknown users are encountered.

```bash
hedwig sync-userlist [--config CONFIG] [--quiet]
```

**Options:**
- `--config`: Configuration file path (default: `config.yml`)
- `--quiet`: Suppress progress messages

**Output:**
Creates a TSV file at the path specified in `paths.userlist_file` containing:
- `user_id`: Notion user UUID
- `name`: User's display name

**Override Feature:**
If `paths.userlist_override_file` is configured and the file exists, users from this file will override or supplement the Notion user list. This is useful for:
- Correcting names that appear incorrectly in Notion
- Adding custom display names for specific users
- Including users that may not be in the Notion workspace

The override file should have the same TSV format as the output file.

**Note:** With auto-sync enabled (default), this command is automatically run when `generate-change-summary` encounters unknown user IDs.

### `hedwig generate-change-summary`
Analyzes recent Git commits and generates AI-powered summaries.

```bash
hedwig generate-change-summary [--config CONFIG] [--no-write]
```

**Options:**
- `--config`: Configuration file path (default: `config.yml`)
- `--no-write`: Print to stdout instead of saving to file

**Auto User Sync:**
When `change_summary.auto_sync_userlist` is set to `true` (default), the command will automatically run `sync-userlist` if it encounters user IDs not found in the user list. This ensures that new team members are automatically added to the user list. Set to `false` to disable this behavior.

### `hedwig generate-overview`
Creates team-focused overview summaries from individual change summaries.

```bash
hedwig generate-overview [--config CONFIG] [--no-write]
```

**Options:**
- `--config`: Configuration file path (default: `config.yml`)
- `--no-write`: Print to stdout instead of saving to file

### `hedwig post-summary`
Posts summaries to configured messaging platforms.

```bash
hedwig post-summary --summary-file FILE --overview-file FILE --title TITLE [--config CONFIG]
```

**Options:**
- `--summary-file`: Path to the markdown summary file
- `--overview-file`: Path to the overview message file
- `--title`: Title for the posted summary
- `--config`: Configuration file path (default: `config.yml`)

### `hedwig pipeline`
Runs the complete summarization pipeline automatically.

```bash
hedwig pipeline [--config CONFIG]
```

**Options:**
- `--config`: Configuration file path (default: `config.yml`)

**Note**: This command does NOT include syncing from Notion. Run `hedwig sync` separately before the pipeline to ensure the Git repository is up-to-date.

## Configuration

Hedwig uses a YAML configuration file. Copy `config.yml.example` to `config.yml` and customize:

### Essential Settings

```yaml
# Repository paths
paths:
  notes_repository: '/path/to/your/notes/repo'
  change_summary_output: '/path/to/summary/output'

# API Keys (can be set here OR as environment variables)
notion:
  api_key: 'your-notion-api-key'  # Alternative: export NOTION_API_KEY=...

api:
  llm:
    key: 'your-gemini-api-key'    # Alternative: export GEMINI_API_KEY=...
    url: 'https://generativelanguage.googleapis.com/v1beta/openai/'

messaging:
  slack:
    token: 'xoxb-your-bot-token'  # Alternative: export SLACK_TOKEN=...
```

### Key Configuration Options

- **Sync Settings**: Checkpoint tracking, timezone, lookback days
- **Summary Settings**: Model selection, prompt customization, diff length limits
- **Overview Settings**: Language selection, lab information, weekday configurations
- **Messaging Settings**: Platform selection, channel configuration
- **Pipeline Settings**: Title format customization

See `config.yml.example` for all available options with detailed comments.

## Automated Execution

Set up cron jobs for the two-stage process:

```bash
# Sync from Notion every hour during work hours
0 * * * * /usr/bin/hedwig sync --config /path/to/config.yml

# Run pipeline everyday except Sunday at 8:30 AM
30 8 * * 1-6 /usr/bin/hedwig pipeline --config /path/to/config.yml
```

## Messaging Platforms

### Slack Integration

Hedwig creates Canvas documents in Slack for rich formatting:

1. Create a Slack app with required permissions:
   - `channels:read`
   - `chat:write`
   - `canvases:write`
   - `canvases:read`

2. Install the app to your workspace

3. Configure in `config.yml`:
   ```yaml
   messaging:
     active: slack
     slack:
       token: 'xoxb-your-bot-token'
       channel_id: 'C12345678'
   ```

## Advanced Usage

### Custom Prompts

Customize LLM prompts for summaries:

```yaml
api:
  llm:
    diff_summary_prompt: |
      Your custom prompt for analyzing diffs...

    overview_prompt_template: |
      Your custom overview template with {summary_range} and {forthcoming_range}...
```

### Changing Language

Set overview language and customize instructions:

```yaml
overview:
  language: en  # Options: ko, en, ja, zh_CN
  lab_info: "Your Lab Name and Description"
```

## Troubleshooting

### Common Issues

1. **Configuration problems**: Run `hedwig health` to diagnose configuration issues
2. **No summaries generated**: Check if there are recent commits within the lookback period
3. **Sync failures**: Verify Notion API key and page permissions
4. **LLM errors**: Check API key and rate limits
5. **Messaging failures**: Verify bot token and channel permissions

### First-Time Setup Issues

If you encounter problems during initial setup, run the health check:

```bash
hedwig health --config config.yml
```

This will identify:
- Missing or invalid configuration
- Permission issues
- Missing dependencies
- API connectivity problems

### Debug Mode

Run with verbose output for troubleshooting:

```bash
hedwig pipeline --config config.yml --verbose
```

### Logs

Check application logs for detailed error messages. The location depends on your configuration.

## License

MIT License - see LICENSE.txt for details

## Author

Hyeshik Chang <hyeshik@snu.ac.kr>