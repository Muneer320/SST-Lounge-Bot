# Changelog

All notable changes to the SST Lounge Discord Bot project will be documented in this file.

## [1.4.0] - 2025-07-18

### Changed

- **Codebase Cleanup**: Complete code cleanup with improved documentation and comments
- **Version Management**: Updated version numbers across all files for consistency
- **Documentation Updates**: Refreshed all markdown files with current information
- **Code Quality**: Removed unnecessary comments and improved code organization
- **File Cleanup**: Removed temporary files and improved repository structure

### Technical Improvements

- **Consistent Versioning**: Aligned version numbers in all configuration files
- **Enhanced Documentation**: Improved function docstrings and inline comments
- **Code Organization**: Better separation of concerns and cleaner file structure
- **Repository Hygiene**: Cleaned up unnecessary files and improved .gitignore coverage

## [1.3.0] - 2025-07-18

### Added

- **Manual Update Command**: New `/update` command to manually trigger bot updates
- **Version Tracking**: Added version.json file to track version information
- **Admin Notifications**: Automatic notifications for administrators when updates are available
- **Interactive Updates**: Confirmation dialog with interactive buttons for update process
- **Semantic Versioning**: Smart version comparison to detect new releases
- **Update Details**: Display update information including version number and description

### Changed

- **Auto-Update System**: Enhanced to check both version.json and git commits for updates
- **Updater Class**: Redesigned GitUpdater to support both automatic and manual updates
- **Admin Permissions**: Update command requires bot admin privileges
- **Documentation**: Updated requirements to include necessary dependencies
- **Error Handling**: Improved error handling and user feedback during update process

### Technical Improvements

- **Version Comparison**: Semantic versioning with proper comparison of version components
- **Remote Version Detection**: Direct checks of version.json in GitHub repository
- **UI Components**: Interactive confirmation buttons for update command
- **Notification System**: Direct messages to bot administrators for update notifications
- **Process Management**: Improved restart handling after updates

## [1.2.0] - 2025-07-17

### Added

- **Auto-Update System**: Automatic GitHub repository checking and bot updates
- **Configurable Repository**: Support for custom GitHub URLs and branch selection
- **Smart Restart**: Bot automatically restarts after pulling latest changes
- **Environment Variables**: New environment variables for controlling auto-update behavior
  - `ENABLE_AUTO_UPDATES`: Enable/disable auto-update system (default: true)
  - `GITHUB_REPO_URL`: Set custom repository URL
  - `GITHUB_REPO_BRANCH`: Specify branch to track (empty for default branch)
  - `UPDATE_CHECK_INTERVAL`: Configure check frequency in seconds (default: 300)
- **Logging**: Detailed update checking and pull logging

### Changed

- **Bot Core**: Updated to support auto-update functionality
- **Startup Sequence**: Added update checker initialization
- **Documentation**: Updated README.md to include auto-update feature details
- **Environment Example**: Updated .env.example with auto-update configuration options

### Technical Improvements

- **GitUpdater Class**: New class for handling GitHub repository checks
- **Async Git Operations**: Non-blocking git fetch and pull operations
- **Process Management**: Clean bot restart after updates
- **Error Handling**: Graceful handling of git operation failures

## [1.1.0] - 2025-07-17

### Added

- **Bot Admin System**: Three-tier permission system (Server owner → Discord admins → Bot admins)
- **Granular Admin Control**: Grant/revoke bot admin privileges to users or roles
- **Admin Transparency**: `/list_admins` command shows all bot admins with grant history
- **Enhanced Help System**: Reorganized and improved `/help` command with better categorization
- **Contribute Command**: `/contribute` command with GitHub repository information and contribution guidelines
- **GitHub Templates**: Complete issue templates, PR template, contributing guide, and code of conduct

### Changed

- **Permission System**: Admin commands now use bot-level admin system instead of Discord server roles
- **Admin Commands**: Updated grant/revoke admin commands to work with bot-level privileges only
- **Database Schema**: Added `bot_admins` table for persistent bot admin storage
- **Error Handling**: Improved error handling with better user feedback and logging

### Technical Improvements

- **Database Methods**: Added `grant_bot_admin()`, `revoke_bot_admin()`, `is_bot_admin()`, `get_bot_admins()`
- **Permission Checking**: Updated `is_bot_admin()` function to support async checking of user and role privileges
- **Documentation**: Updated README.md and FEATURES.md to reflect new bot admin system
- **Code Cleanup**: Removed redundant code, improved logging consistency, and enhanced error handling
- **GitHub Automation**: Added issue and PR management workflows with auto-labeling and welcome messages

### Security

- **Permission Isolation**: Bot admin privileges don't affect Discord server permissions
- **Owner Control**: Only server owners can grant/revoke bot admin privileges
- **Audit Trail**: All bot admin grants tracked with timestamps and granter information


## [1.0.0] - 2025-07-16

### Initial Release

- **Contest System**: Complete contest tracking with caching and real-time status
- **Role Management**: Automatic Discord Veteran role assignment
- **Admin Commands**: Basic admin functionality with Discord permission checking
- **Utility Commands**: Ping, hello, help, and info commands
- **Database Integration**: SQLite database with optimized queries
- **Background Tasks**: Daily cache refresh and role checking
- **Documentation**: Comprehensive README and FEATURES documentation

### Features

- Contest fetching from clist.by API with intelligent caching
- Real-time contest status detection (upcoming/running/ended)
- Automatic Discord Veteran role assignment based on account age
- Daily background tasks for cache refresh and role management
- Slash command interface with rich embed responses
- IST timezone support for local relevance
- Modular architecture with feature separation
