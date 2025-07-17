# Contributing to SST Lounge Bot

Welcome to the SST Lounge Bot project! We're excited that you want to contribute to making our batch's Discord experience better. 🎉

## 🎯 How to Contribute

### 🐛 Reporting Bugs

1. **Use the `/contribute` command** in Discord for quick access to this repository
2. **Check existing issues** to avoid duplicates
3. **Create a bug report** using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
4. **Include specific details**:
   - Exact Discord command used
   - Bot's response or error message
   - Your role/permissions in the server
   - Steps to reproduce the issue

### 💡 Suggesting Features

1. **Create a feature request** using our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
2. **Explain the benefit** to SST Batch '29
3. **Provide examples** of how the feature would be used
4. **Consider implementation** details if you have technical knowledge

### ❓ Asking Questions

1. **Check documentation** first (README.md, FEATURES.md)
2. **Use `/help`** command in Discord
3. **Search existing issues** for similar questions
4. **Create a question issue** using our [question template](.github/ISSUE_TEMPLATE/question.md)

## 👨‍💻 Code Contributions

### 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature: `git checkout -b feature-name`
4. **Set up the development environment**:
   ```bash
   cd "Discord Bot"
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   cp .env.example .env  # Add your bot token
   ```

### 📁 Project Structure

```
core/                    # Bot core and database
├── bot.py              # Main bot class
└── database.py         # SQLite database operations

features/               # Modular features
├── admin/              # Admin commands and permissions
├── contests/           # Contest system with caching
├── roles/              # Automatic role management
└── utilities/          # Basic utility commands

.github/               # GitHub templates and workflows
├── ISSUE_TEMPLATE/    # Issue templates
└── pull_request_template.md
```

### 🎨 Code Style

- **Follow existing patterns** in the codebase
- **Use meaningful variable names** and function names
- **Add docstrings** to functions and classes
- **Include comments** for complex logic
- **Use Discord embed formatting** for bot responses
- **Handle errors gracefully** with user-friendly messages

### 🧪 Testing Your Changes

1. **Test in Discord**: Create a test server and invite your bot
2. **Check all commands**: Ensure your changes don't break existing functionality
3. **Test permissions**: Verify admin/owner restrictions work correctly
4. **Test error cases**: Try invalid inputs and edge cases
5. **Check database**: Ensure database operations work correctly

### 📝 Submitting Changes

1. **Commit your changes** with clear commit messages
2. **Push to your fork**: `git push origin feature-name`
3. **Create a Pull Request** using our [PR template](.github/pull_request_template.md)
4. **Fill out the template** completely
5. **Include screenshots** of Discord command responses if applicable

## 🎭 Areas Where We Need Help

### 🏆 Contest Features

- **New platforms**: HackerRank, TopCoder, GeeksforGeeks integration
- **Contest analysis**: Statistics and batch performance tracking
- **Notification improvements**: Better timing and formatting

### 🎨 User Experience

- **Better embeds**: More informative and visually appealing responses
- **Command improvements**: Better parameter validation and help text
- **Error messages**: More helpful and user-friendly error responses

### 🔧 Technical Improvements

- **Performance optimization**: Faster database queries and API calls
- **Code cleanup**: Refactoring and removing duplicate code
- **Documentation**: README updates and inline code documentation

### 🚀 New Features

- **Study groups**: Commands to form and manage study groups
- **Announcements**: Better batch communication tools
- **Utilities**: Time zone conversion, reminder system, etc.

## 📋 Development Guidelines

### 🔍 Before You Start

- **Check existing issues** to see if someone is already working on it
- **Comment on the issue** to let others know you're working on it
- **Ask questions** if you need clarification

### 💻 While Developing

- **Keep commits focused** on single features or fixes
- **Write clear commit messages**: "Add contest filtering by platform"
- **Test thoroughly** before submitting
- **Update documentation** if needed

### 🤝 Code Review Process

- **Be patient**: Reviews help maintain code quality
- **Be open to feedback**: Reviewers are here to help
- **Make requested changes**: Address all review comments
- **Test again** after making changes

## 🎯 Priority Features for SST Batch '29

1. **Contest coordination** improvements
2. **Batch communication** tools
3. **Study group** management
4. **Academic calendar** integration
5. **Performance tracking** and analytics

## 🏷️ Labels We Use

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `question` - Further information is requested
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `priority` - Important for batch coordination

## 🎉 Recognition

Contributors will be:

- **Listed in CHANGELOG.md** for their contributions
- **Mentioned in release notes** for significant features
- **Credited in bot responses** for major additions
- **Appreciated by the entire SST Batch '29** community!

## 📞 Getting Help

- **Use `/contribute`** command in Discord for quick links
- **Ask in the SST Lounge Discord server** for general help
- **Create a question issue** for technical questions
- **Tag maintainers** in issues for urgent matters

Thank you for contributing to the SST Lounge Bot! Together, we're making our batch's Discord experience better! 🚀
