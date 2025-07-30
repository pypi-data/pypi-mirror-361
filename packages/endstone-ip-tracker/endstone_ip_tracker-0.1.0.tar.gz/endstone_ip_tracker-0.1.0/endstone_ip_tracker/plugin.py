# -*- coding: utf-8 -*-
# @Time    : 7/10/2025 5:48 PM
# @FileName: plugin.py
# @Software: PyCharm
import json
import os
from datetime import datetime
from typing import Dict, Any

from endstone import ColorFormat
from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerJoinEvent, PlayerQuitEvent
from endstone.command import Command, CommandSender


class IPTrackerPlugin(Plugin):
    """IP追踪插件主类"""

    # 插件基本信息
    api_version = "0.6"
    prefix = "IPTracker"

    # 定义命令
    commands = {
        "checkip": {
            "description": "Check player IP address",
            "usages": ["/checkip <player: string>"],
            "permissions": ["iptracker.check"],
        },
        "iplist": {
            "description": "List all recorded IPs",
            "usages": ["/iplist"],
            "permissions": ["iptracker.list"],
        },
    }

    # 定义权限
    permissions = {
        "iptracker.admin": {
            "description": "IP tracker admin permissions",
            "default": "op",
            "children": {
                "iptracker.check": True,
                "iptracker.list": True,
            },
        },
        "iptracker.check": {
            "description": "Allow querying player IP",
            "default": "op",
        },
        "iptracker.list": {
            "description": "Allow viewing IP lists",
            "default": "op",
        },
    }

    def on_load(self) -> None:
        """插件加载时执行"""
        self.logger.info("🔍 IP追踪插件加载中...")
        self.ip_data_file = os.path.join(self.data_folder, "player_ips.json")
        self.player_ips: Dict[str, Dict[str, Any]] = {}

    def on_enable(self) -> None:
        """插件启用时执行"""
        self.logger.info("✅ IP追踪插件已启用")

        # 注册事件监听器
        self.register_events(self)

        # 加载IP数据
        self.load_ip_data()

    def on_disable(self) -> None:
        """插件禁用时执行"""
        self.save_ip_data()
        self.logger.info("❌ IP追踪插件已禁用")

    def load_ip_data(self) -> None:
        """加载IP数据"""
        try:
            if os.path.exists(self.ip_data_file):
                with open(self.ip_data_file, 'r', encoding='utf-8') as f:
                    self.player_ips = json.load(f)
                self.logger.info(f"📊 已加载 {len(self.player_ips)} 个玩家的IP记录")
            else:
                os.makedirs(self.data_folder, exist_ok=True)
                self.player_ips = {}
                self.logger.info("📁 创建新的IP数据文件")
        except Exception as e:
            self.logger.error(f"❌ 加载IP数据失败: {e}")
            self.player_ips = {}

    def save_ip_data(self) -> None:
        """保存IP数据"""
        try:
            os.makedirs(self.data_folder, exist_ok=True)
            with open(self.ip_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.player_ips, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ 保存IP数据失败: {e}")

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        """玩家加入服务器时记录IP"""
        player = event.player
        player_name = player.name

        # 获取IP地址
        try:
            player_ip = "127.0.0.1"  # 默认值
            if hasattr(player, 'address'):
                if hasattr(player.address, 'hostname'):
                    player_ip = player.address.hostname
                elif hasattr(player.address, 'address'):
                    player_ip = player.address.address
                else:
                    addr_str = str(player.address)
                    if ':' in addr_str:
                        player_ip = addr_str.split(':')[0]
                    else:
                        player_ip = addr_str
        except Exception as e:
            self.logger.warning(f"⚠️ 无法获取玩家IP: {e}")
            player_ip = "未知IP"

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 记录玩家IP信息
        if player_name not in self.player_ips:
            self.player_ips[player_name] = {
                "current_ip": player_ip,
                "first_join": current_time,
                "last_join": current_time,
                "join_count": 1,
                "ip_history": [{"ip": player_ip, "time": current_time}]
            }
        else:
            self.player_ips[player_name]["last_join"] = current_time
            self.player_ips[player_name]["join_count"] += 1

            if self.player_ips[player_name]["current_ip"] != player_ip:
                self.player_ips[player_name]["current_ip"] = player_ip
                self.player_ips[player_name]["ip_history"].append({
                    "ip": player_ip,
                    "time": current_time
                })

        self.save_ip_data()

        # 记录到日志
        self.logger.info(
            f"🎮 {ColorFormat.YELLOW}玩家 {player_name} 加入游戏，IP: {player_ip} "
            f"(第 {self.player_ips[player_name]['join_count']} 次加入){ColorFormat.RESET}"
        )

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        """玩家退出服务器时保存数据"""
        player = event.player
        player_name = player.name

        self.logger.info(f"👋 {ColorFormat.YELLOW}玩家 {player_name} 离开游戏{ColorFormat.RESET}")
        self.save_ip_data()

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        """处理命令"""
        match command.name:
            case "checkip":
                return self.handle_checkip_command(sender, args)
            case "iplist":
                return self.handle_iplist_command(sender, args)
        return False

    def handle_checkip_command(self, sender: CommandSender, args: list[str]) -> bool:
        """处理checkip命令"""
        if len(args) != 1:
            sender.send_error_message("Usage: /checkip <player>")
            return True

        player_name = args[0]

        if player_name not in self.player_ips:
            sender.send_error_message(f"No IP record found for player {player_name}")
            return True

        player_data = self.player_ips[player_name]

        sender.send_message(f"{ColorFormat.GREEN}=== Player {player_name} IP Information ==={ColorFormat.RESET}")
        sender.send_message(f"{ColorFormat.AQUA}Current IP: {ColorFormat.WHITE}{player_data['current_ip']}")
        sender.send_message(f"{ColorFormat.AQUA}First Join: {ColorFormat.WHITE}{player_data['first_join']}")
        sender.send_message(f"{ColorFormat.AQUA}Last Join: {ColorFormat.WHITE}{player_data['last_join']}")
        sender.send_message(f"{ColorFormat.AQUA}Join Count: {ColorFormat.WHITE}{player_data['join_count']}")

        if len(player_data['ip_history']) > 1:
            sender.send_message(f"{ColorFormat.YELLOW}IP History (Recent 5):")
            for i, record in enumerate(player_data['ip_history'][-5:], 1):
                sender.send_message(f"{ColorFormat.GRAY}{i}. {record['ip']} - {record['time']}")

        return True

    def handle_iplist_command(self, sender: CommandSender, args: list[str]) -> bool:
        """处理iplist命令"""
        if not self.player_ips:
            sender.send_error_message("No IP records available")
            return True

        sender.send_message(
            f"{ColorFormat.GREEN}=== IP Record List (Total {len(self.player_ips)} players) ==={ColorFormat.RESET}")

        sorted_players = sorted(
            self.player_ips.items(),
            key=lambda x: x[1]['last_join'],
            reverse=True
        )

        display_count = min(10, len(sorted_players))
        for i, (player_name, data) in enumerate(sorted_players[:display_count], 1):
            sender.send_message(
                f"{ColorFormat.YELLOW}{i:2d}. {ColorFormat.WHITE}{player_name:<16} "
                f"{ColorFormat.AQUA}{data['current_ip']:<15} {ColorFormat.GRAY}{data['last_join']}"
            )

        if len(self.player_ips) > display_count:
            sender.send_message(f"{ColorFormat.GRAY}... and {len(self.player_ips) - display_count} more players")

        return True