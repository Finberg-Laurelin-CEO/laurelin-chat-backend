# Beads Issue Tracker Usage Guide - Backend

This project uses [Beads](https://github.com/steveyegge/beads) - a dependency-aware issue tracker designed for AI-assisted development workflows.

## Quick Setup

To use Beads in your development session:

```bash
# Add Beads to your PATH (run this in your shell)
export PATH="$PATH:/Users/Joe/go/bin"

# Or use the setup script
source ./setup-beads.sh
```

## Current Project Status

### Epic: Flask Backend - Laurelin Chat API
- **Main Epic**: `laurelin-chat-backend-1` - Flask Backend - Laurelin Chat API
- **Status**: Open (P0 priority)

### Key Features Being Tracked

1. **Google OAuth Integration** (`laurelin-chat-backend-2`)
   - JWT token management
   - User profile handling
   - Authentication endpoints

2. **Chat Session Management** (`laurelin-chat-backend-3`)
   - Session creation and management
   - Message handling
   - Firestore integration

3. **AI Model Integration** (`laurelin-chat-backend-4`)
   - LLM backend communication
   - OpenAI GPT and Google Gemini integration
   - Model processing endpoints

4. **A/B Testing Infrastructure** (`laurelin-chat-backend-5`)
   - Model comparison system
   - User assignment logic
   - Analytics and tracking

5. **Firestore Database Integration** (`laurelin-chat-backend-6`)
   - Session storage
   - User data management
   - A/B testing analytics

6. **API Security & CORS** (`laurelin-chat-backend-7`)
   - CORS protection
   - Input validation
   - Security headers

7. **Health Monitoring & Logging** (`laurelin-chat-backend-8`)
   - Health check endpoints
   - Structured logging
   - Monitoring capabilities

## Common Commands

### View Issues
```bash
bd list                    # List all issues
bd list --status open      # List open issues only
bd list --priority 0       # List highest priority issues
bd ready                   # Show work ready to start (no blockers)
```

### Create Issues
```bash
bd create "Fix login bug"                    # Basic issue
bd create "Add feature" -p 0 -t feature      # High priority feature
bd create "Write tests" -d "Unit tests"      # With description
```

### Manage Dependencies
```bash
bd dep add issue-1 issue-2        # Add dependency (issue-2 blocks issue-1)
bd dep tree issue-1               # Show dependency tree
bd dep cycles                     # Detect circular dependencies
```

### Update Issues
```bash
bd update issue-1 --status in_progress
bd update issue-1 --priority 1
bd update issue-1 --assignee developer
```

### Close Issues
```bash
bd close issue-1
bd close issue-1 --reason "Fixed in PR #42"
```

## Development Workflow

1. **Check Ready Work**: `bd ready` - Shows issues with no blockers
2. **Claim Work**: Update issue status to `in_progress`
3. **Track Progress**: Update descriptions, add comments
4. **Close When Done**: Close issues with completion reason

## Git Integration

Beads automatically syncs with git:
- Issues are exported to `.beads/issues.jsonl` after changes
- Import happens automatically when pulling from git
- No manual export/import needed for normal workflow

## Database Location

- **Local Database**: `.beads/laurelin-chat-backend.db`
- **JSONL Export**: `.beads/issues.jsonl` (for git sync)
- **Auto-discovery**: Beads finds the database automatically

## Agent-Friendly Features

- **JSON Output**: Use `--json` flag for programmatic access
- **Dependency Awareness**: Prevents duplicate work
- **Ready Work**: Shows unblocked tasks perfect for AI agents
- **Structured Data**: All data stored in SQLite for queries

## Backend-Specific Notes

This is a Flask Python application with:
- Google Cloud integration (Firestore, OAuth)
- RESTful API design
- JWT authentication
- CORS protection
- Docker containerization
- Cloud Build deployment

## API Endpoints

The backend provides these main API endpoints:
- `POST /api/auth/login` - Google OAuth login
- `GET /api/auth/profile` - Get user profile
- `GET /api/chat/sessions` - Get user's chat sessions
- `POST /api/chat/sessions` - Create new chat session
- `POST /api/chat/sessions/{id}/messages` - Send message
- `GET /api/ab-testing/experiments` - Get experiments
- `GET /health` - Health check

## Troubleshooting

### Command Not Found
```bash
# Make sure Go bin is in PATH
export PATH="$PATH:/Users/Joe/go/bin"
which bd
```

### Database Issues
```bash
# Check database location
bd list --json | head -1

# Reinitialize if needed (DESTROYS DATA!)
rm -rf .beads/
bd init
```

### Git Conflicts
```bash
# Resolve conflicts in .beads/issues.jsonl
# Then sync to database
bd import -i .beads/issues.jsonl
```

## Resources

- [Beads GitHub Repository](https://github.com/steveyegge/beads)
- [Beads Documentation](https://github.com/steveyegge/beads/blob/main/README.md)
- [Agent Integration Guide](https://github.com/steveyegge/beads/blob/main/AGENTS.md)

## Current Project Statistics

Run `bd stats` to see current project metrics including:
- Total issues created
- Issues by status
- Issues by priority
- Dependency relationships
