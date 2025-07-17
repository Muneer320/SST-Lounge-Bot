# Changelog

All notable changes to the SST Lounge Discord Bot project will be documented in this file.

## [1.1.0] - 2024-12-19

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

## [1.0.0] - 2024-12-18

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
