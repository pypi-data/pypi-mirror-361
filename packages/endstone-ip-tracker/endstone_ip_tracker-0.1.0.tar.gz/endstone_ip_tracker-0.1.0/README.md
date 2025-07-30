# Endstone IP Tracker Plugin

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/) [![Endstone Version](https://img.shields.io/badge/endstone-0.6.0%2B-green.svg)](https://github.com/EndstoneMC/endstone) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://claude.ai/chat/LICENSE)

A comprehensive IP tracking plugin for Endstone Minecraft servers that automatically records and manages player IP addresses with detailed history tracking.

## 🚀 Features

- **🔍 Automatic IP Tracking**: Records player IP addresses when they join the server
- **📊 Join Statistics**: Tracks player join count and timestamps
- **🕐 IP History**: Maintains complete history of IP address changes
- **📋 Query Commands**: Easy-to-use commands for checking player information
- **💾 Data Persistence**: Automatic data saving and loading with JSON storage
- **🔒 Permission System**: Configurable permissions for different user roles
- **🌐 Multi-IP Support**: Tracks IP changes when players connect from different networks

## 📦 Installation
### Option 1: Install from Release (Recommended)

Download .whl file from Release Page, then put this file into Plugin folder

### Option 2: Install from PyPI

```bash
pip install endstone-ip-tracker
```

### Option 3: Install from Source

```bash
git clone https://github.com/Tsingloong611/endstone-ip-tracker.git
cd endstone-ip-tracker
pip install -e .
```

### Option 4: Install from Release

1. Download the latest `.whl` file from [Releases](https://github.com/Tsingloong611/endstone-ip-tracker/releases)
2. Install using pip:

```bash
pip install endstone_ip_tracker-0.1.0-py2.py3-none-any.whl
```

## 🎮 Usage

### Commands

| Command    | Description                 | Usage               | Permission        |
| ---------- | --------------------------- | ------------------- | ----------------- |
| `/checkip` | Check player IP information | `/checkip <player>` | `iptracker.check` |
| `/iplist`  | List all recorded players   | `/iplist`           | `iptracker.list`  |
### Example Usage

![image1](./img/1.png)

![image2](./img/2.png)

```bash
# Check a specific player's IP
/checkip Tsingloong1219

# List all players with their current IPs
/iplist
```

## 🔐 Permissions

| Permission        | Description                | Default |
| ----------------- | -------------------------- | ------- |
| `iptracker.admin` | All IP tracker permissions | `op`    |
| `iptracker.check` | Use /checkip command       | `op`    |
| `iptracker.list`  | Use /iplist command        | `op`    |

## 📊 Data Structure

The plugin stores data in `plugins/IPTrackerPlugin/player_ips.json`:

```json
{
  "Tsingloong1219": {
    "current_ip": "192.168.50.40",
    "first_join": "2025-07-10 18:10:34",
    "last_join": "2025-07-10 18:14:50",
    "join_count": 3,
    "ip_history": [
      {
        "ip": "192.168.50.39",
        "time": "2025-07-10 18:10:34"
      },
      {
        "ip": "192.168.50.40",
        "time": "2025-07-10 18:14:50"
      }
    ]
  }
}
```

## 🛠️ Configuration

The plugin works out of the box with no configuration required. However, you can customize:

- **Data Storage Location**: Modify `self.data_folder` in the plugin code
- **Display Limits**: Change the number of history entries shown in commands
- **Permissions**: Adjust permission requirements in your server configuration

## 🔧 Requirements

- **Endstone**: >= 0.6.0
- **Python**: >= 3.9
- **Operating System**: Windows, Linux, macOS

## 📝 Changelog

### v0.1.0 (2025-07-10)

- Initial release
- Basic IP tracking functionality
- Command system implementation
- Data persistence
- Permission system
- Multi-language support preparation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://claude.ai/chat/LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Tsingloong611/endstone-ip-tracker/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your setup and the issue

## 🙏 Acknowledgments

- Thanks to the Endstone team for creating an excellent Minecraft server platform
- Inspired by the need for better player management tools in Minecraft servers

## 📈 Statistics

- **Players Tracked**: Unlimited
- **IP History**: Complete history maintained
- **Performance**: Minimal server impact
- **Compatibility**: Works with all Endstone-compatible setups

------

Made with ❤️ for the Minecraft community
