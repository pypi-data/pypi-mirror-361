# gh-feed

**gh-feed** is## Installation

### From PyPI (Recommended)

Once published to PyPI, you can install with:

```bash
pip install gh-feed
```

### From TestPyPI (Current)

You can install `gh-feed` from [TestPyPI](https://test.pypi.org/project/gh-feed/0.1.2/) using the following command:

```bash
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gh-feed==0.1.2
```

### From Source

```bash
git clone https://github.com/bhantsi/gh-feed.git
cd gh-feed
pip install .
```ommand-line tool written in Python that fetches and displays a GitHub user's recent public activity directly in the terminal.  
It uses the GitHub API and works with no external libraries.

---

## 🚀 Features

- **Fetches GitHub activity** - Get the most recent public events for any GitHub user
- **Rich event support** - Supports pushes, issues, pull requests, stars, forks, releases, comments, and more
- **Beautiful output** - Colorized terminal output with relative timestamps (e.g., "2h ago")
- **Smart filtering** - Filter events by type using `--filter <event_type>`
- **Export functionality** - Export results to JSON with `--json` flag
- **Authentication support** - Use GitHub tokens via `--token` or `GITHUB_TOKEN` env variable
- **Interactive mode** - Step-by-step guided usage with `--interactive`
- **Offline caching** - Caches API responses for 5 minutes to reduce API calls
- **Error handling** - Graceful handling of rate limits, network issues, and invalid users
- **Update notifications** - Automatic check for new versions with upgrade instructions
- **Version information** - Check current version with `--version` or `-v`
- **Comprehensive help** - Detailed usage guide with `--help` or `-h`
- **No dependencies** - Pure Python standard library, no external packages required

---

## 📦 Installation

You can install `gh-feed` from [TestPyPI](https://test.pypi.org/project/gh-feed/0.1.2/) using the following command:

```bash
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gh-feed==0.1.2
```

> **Note:**  
> This package is currently published on [TestPyPI](https://test.pypi.org/project/gh-feed/0.1.2/), which is for testing purposes.  
> For production use, wait for the package to be published on the main PyPI repository.

---

## 🛠️ Usage

### Prerequisites
- Python 3 (comes pre-installed on most systems)

### Running the CLI

After installation, you can run the CLI from anywhere:

```bash
gh-feed <github_username>
```

Or, if you want to run the script directly (if you have the source):

```bash
python3 app.py <github_username>
```

### Basic Commands

```bash
# Get user activity
gh-feed octocat

# Show version
gh-feed --version
gh-feed -v

# Show help
gh-feed --help
gh-feed -h

# Interactive mode
gh-feed --interactive
```

### Filtering Events

You can filter by event type (e.g., only show push events):

```bash
gh-feed octocat --filter PushEvent
```

### Exporting to JSON

Export the latest events to a file:

```bash
gh-feed octocat --json
```

You can combine filtering and export:

```bash
gh-feed octocat --filter IssuesEvent --json
```

### Using a GitHub Token

To increase your API rate limit, you can provide a personal access token:

```bash
gh-feed octocat --token <your_github_token>
```

Or set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_github_token
gh-feed octocat
```

### Interactive Mode

Start an interactive session for guided usage:

```bash
gh-feed --interactive
```
You'll be prompted for the username, event filter, token, and export options.

### Caching

API responses are cached for 5 minutes in the `~/.cache/gh-feed/` directory to reduce API calls and speed up repeated queries.

### Update Notifications

The tool automatically checks for new versions when you run commands and notifies you if an update is available:

```
📦 New version available: 0.1.3 (current: 0.1.2)
💡 Run 'pip install --upgrade gh-feed' to update
```

### Example

```bash
gh-feed octocat
```

Sample output:
```
- Pushed 2 commits to octocat/Hello-World (3h ago)
- Opened an issue in octocat/Hello-World (5h ago)
- Starred octocat/Spoon-Knife (1d ago)

Summary:
- push commit: 1
- issue opened: 1
- repo starred: 1
- Activity in 3 repos
```

---

## ⚠️ Important Notes

- The tool uses the public GitHub API, which is subject to [rate limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting). If you make too many requests in a short period, you may be temporarily blocked from making further requests.
- Only public events are shown. Private activity will not appear.
- If you see a warning about nearing the rate limit, wait a while before making more requests.
- Make sure you have an active internet connection.
- The tool displays up to 7 of the most recent events.
- Cached data is stored in `~/.cache/gh-feed/` and is valid for 5 minutes.

---

## � Changelog

### v0.1.2 (Latest)
- ✅ **NEW**: Added `--help` and `-h` command support for comprehensive usage guide
- ✅ **NEW**: Added `--version` and `-v` command to display current version
- ✅ **NEW**: Automatic update notifications when newer versions are available
- 🐛 **FIXED**: Interactive mode now properly validates empty username input
- 🐛 **FIXED**: Help command now works correctly with installed package
- 📚 **IMPROVED**: Enhanced help documentation with examples and options
- 🎨 **IMPROVED**: Better error handling and user experience

### v0.1.1
- 🚀 **NEW**: Offline caching system for API responses (5-minute cache)
- 🚀 **NEW**: Interactive mode with guided prompts
- 🚀 **NEW**: Colorized terminal output for better readability
- 🚀 **NEW**: Event filtering by type with `--filter` option
- 🚀 **NEW**: JSON export functionality with `--json` flag
- 🚀 **NEW**: GitHub token authentication support
- 📚 **IMPROVED**: Comprehensive error handling for rate limits and network issues

### v0.1.0
- 🎉 Initial release
- ✅ Basic GitHub user activity fetching
- ✅ Support for multiple event types
- ✅ Relative timestamp display
- ✅ Activity summary with repository count

---

## �📝 Attribution

This project was inspired by the [GitHub User Activity CLI](https://roadmap.sh/projects/github-user-activity) project on [roadmap.sh](https://roadmap.sh/).  
Check out their project for more ideas and inspiration!

---

## 📈 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License
MIT License
