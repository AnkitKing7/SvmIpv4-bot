#!/bin/bash

# ==============================================
#    SVMIPV4 BOT - Complete Installation Script
#    Created by: Ankit Dev
#    License Key: AnkitDev99$@
#    Version: 1.0
# ==============================================

# Rainbow colors for title
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Rainbow function
rainbow_text() {
    local text="$1"
    local colors=($RED $GREEN $YELLOW $BLUE $PURPLE $CYAN)
    local color_index=0
    for (( i=0; i<${#text}; i++ )); do
        echo -ne "${colors[$color_index]}${text:$i:1}${NC}"
        color_index=$(( (color_index + 1) % ${#colors[@]} ))
    done
    echo
}

# Big title
clear
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                                                                              ${CYAN}║${NC}"
rainbow_text "║                    ███████╗██╗   ██╗███╗   ███╗██╗██████╗ ██╗   ██╗██╗  ██╗               ║"
rainbow_text "║                    ██╔════╝██║   ██║████╗ ████║██║██╔══██╗██║   ██║╚██╗██╔╝               ║"
rainbow_text "║                    ███████╗██║   ██║██╔████╔██║██║██████╔╝██║   ██║ ╚███╔╝                ║"
rainbow_text "║                    ╚════██║██║   ██║██║╚██╔╝██║██║██╔═══╝ ██║   ██║ ██╔██╗                ║"
rainbow_text "║                    ███████║╚██████╔╝██║ ╚═╝ ██║██║██║     ╚██████╔╝██╔╝ ██╗               ║"
rainbow_text "║                    ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝               ║"
rainbow_text "║                                                                                              ║"
rainbow_text "║                         ██████╗  ██████╗ ████████╗                                          ║"
rainbow_text "║                         ██╔══██╗██╔═══██╗╚══██╔══╝                                          ║"
rainbow_text "║                         ██████╔╝██║   ██║   ██║                                             ║"
rainbow_text "║                         ██╔══██╗██║   ██║   ██║                                             ║"
rainbow_text "║                         ██████╔╝╚██████╔╝   ██║                                             ║"
rainbow_text "║                         ╚═════╝  ╚═════╝    ╚═╝                                             ║"
echo -e "${CYAN}║${NC}                                                                              ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}                    ${BOLD}REAL IPv4 VPS MANAGEMENT SYSTEM${NC}                             ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}                    ${BOLD}Created by: Ankit Dev | License: AnkitDev99$@${NC}                ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}                    ${BOLD}Version: 2.0 | Type: KVM Virtualization${NC}                    ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# License Verification
echo -e "${BOLD}${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${PURPLE}                    LICENSE VERIFICATION REQUIRED${NC}"
echo -e "${BOLD}${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Enter License Key to proceed with installation:${NC}"
echo -e "${WHITE}(License Key: AnkitDev99$@)${NC}"
echo -n -e "${GREEN}License Key > ${NC}"
read -s license_input
echo ""

if [ "$license_input" != "AnkitDev99\$@" ]; then
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║${NC}      ${BOLD}❌ INVALID LICENSE KEY! INSTALLATION ABORTED ❌${NC}          ${RED}║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Please contact Ankit Dev to get a valid license key.${NC}"
    echo -e "${YELLOW}License Key: AnkitDev99\$@${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}          ${BOLD}✅ LICENSE VERIFIED SUCCESSFULLY! ✅${NC}                    ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}     Welcome to SVMIPV4 BOT - Real IPv4 VPS Management      ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo su)${NC}"
    exit 1
fi

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 1: System Update & Dependencies Installation${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv \
    qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils \
    virtinst virt-manager virt-viewer \
    dnsmasq dnsmasq-utils \
    wget curl git unzip \
    genisoimage cloud-image-utils \
    net-tools netplan.io \
    screen htop nmon \
    ufw fail2ban \
    jq bc

echo -e "${GREEN}✅ System dependencies installed!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 2: Python Packages Installation${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

pip3 install --upgrade pip
pip3 install discord.py
pip3 install psutil
pip3 install netifaces
pip3 install requests
pip3 install python-telegram-bot

echo -e "${GREEN}✅ Python packages installed!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 3: Enable & Start Services${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

systemctl enable libvirtd
systemctl start libvirtd
systemctl enable dnsmasq
systemctl start dnsmasq

echo -e "${GREEN}✅ Services started!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 4: Network Bridge Configuration${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

# Detect main interface
MAIN_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -z "$MAIN_IFACE" ]; then
    MAIN_IFACE="eth0"
fi

# Backup existing netplan
if [ -f /etc/netplan/01-netcfg.yaml ]; then
    cp /etc/netplan/01-netcfg.yaml /etc/netplan/01-netcfg.yaml.backup
fi

# Create bridge configuration
cat > /etc/netplan/01-netcfg.yaml << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $MAIN_IFACE:
      dhcp4: no
  bridges:
    br0:
      interfaces: [$MAIN_IFACE]
      dhcp4: yes
      parameters:
        stp: false
        forward-delay: 0
      addresses: [10.10.0.1/16]
      routes:
        - to: default
          via: 10.10.0.1
EOF

# Apply network configuration
netplan apply
sleep 3

echo -e "${GREEN}✅ Network bridge configured!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 5: Create Directory Structure${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

mkdir -p /opt/svmipv4_bot
mkdir -p /opt/svmipv4_bot/logs
mkdir -p /opt/svmipv4_bot/data
mkdir -p /var/lib/libvirt/images/base
mkdir -p /var/lib/libvirt/cloud-init
mkdir -p /etc/svmipv4_bot
mkdir -p /var/log/svmipv4_bot

chmod -R 755 /opt/svmipv4_bot
chmod -R 755 /var/lib/libvirt/images

echo -e "${GREEN}✅ Directories created!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 6: Download Base OS Images${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cd /var/lib/libvirt/images/base

# Ubuntu 22.04
echo -e "${YELLOW}Downloading Ubuntu 22.04 LTS...${NC}"
wget -q --show-progress -O ubuntu2204.qcow2 https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img || echo -e "${RED}Failed to download Ubuntu 22.04${NC}"

# Ubuntu 20.04
echo -e "${YELLOW}Downloading Ubuntu 20.04 LTS...${NC}"
wget -q --show-progress -O ubuntu2004.qcow2 https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img || echo -e "${RED}Failed to download Ubuntu 20.04${NC}"

# Debian 11
echo -e "${YELLOW}Downloading Debian 11...${NC}"
wget -q --show-progress -O debian11.qcow2 https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2 || echo -e "${RED}Failed to download Debian 11${NC}"

# Resize images
for img in *.qcow2; do
    if [ -f "$img" ]; then
        qemu-img resize $img +5G 2>/dev/null || true
    fi
done

echo -e "${GREEN}✅ Base images downloaded!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 7: Create Bot Configuration${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

# Create config file
cat > /etc/svmipv4_bot/config.json << EOF
{
    "bot_name": "SVMIPV4 BOT",
    "creator": "Ankit Dev",
    "license_key": "AnkitDev99\$@",
    "version": "2.0",
    "network": {
        "subnet": "10.10.0.0/16",
        "gateway": "10.10.0.1",
        "bridge": "br0",
        "dns": ["8.8.8.8", "1.1.1.1"]
    },
    "limits": {
        "max_vps_per_user": 5,
        "min_cpu": 1,
        "max_cpu": 8,
        "min_ram_mb": 512,
        "max_ram_mb": 16384,
        "min_disk_gb": 10,
        "max_disk_gb": 100
    },
    "os_templates": [
        "ubuntu2204",
        "ubuntu2004",
        "debian11"
    ]
}
EOF

echo -e "${GREEN}✅ Configuration created!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 8: Create Bot Script${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

# Download bot script (you would place your Python script here)
# For now, we'll create a placeholder
cat > /opt/svmipv4_bot/svmipv4_bot.py << 'EOF'
#!/usr/bin/env python3
"""
SVMIPV4 BOT - Real IPv4 VPS Management System
Created by: Ankit Dev
License: AnkitDev99$@
Version: 2.0
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import subprocess
import uuid
import json
import os
import sys
from datetime import datetime, timedelta

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 123456789  # Replace with your Discord ID
ADMIN_NAME = "Ankit Dev"
BOT_NAME = "SVMIPV4 BOT"
LICENSE_KEY = "AnkitDev99$@"

class SVMIPV4Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        await self.tree.sync()
        print(f"{BOT_NAME} is ready!")

bot = SVMIPV4Bot()

@bot.event
async def on_ready():
    print(f"✅ {BOT_NAME} Started Successfully!")
    print(f"📡 Logged in as: {bot.user}")
    print(f"👤 Created by: {ADMIN_NAME}")
    print(f"🔑 License: {LICENSE_KEY}")
    print(f"🖥️ Real IPv4 VPS Management System Active")

@bot.tree.command(name="license", description="Verify your license key")
@app_commands.describe(key="Enter your license key")
async def verify_license(interaction: discord.Interaction, key: str):
    if key == LICENSE_KEY:
        embed = discord.Embed(
            title="✅ License Verified!",
            description=f"Welcome to {BOT_NAME}!\nYour license is now active.",
            color=0x00ff00
        )
        embed.set_footer(text=f"Powered by {ADMIN_NAME}")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Invalid License!",
            description="Please contact Ankit Dev for a valid license.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"🖥️ {BOT_NAME} - Help Menu",
        description="Complete VPS Management System",
        color=0x00ff00
    )
    embed.add_field(name="📦 VPS Commands", 
                    value="/create - Create VPS\n/list - List VPS\n/info - VPS Details\n/delete - Delete VPS",
                    inline=False)
    embed.add_field(name="🔑 License", 
                    value="/license - Verify license",
                    inline=False)
    embed.set_footer(text=f"Created by {ADMIN_NAME} | License: {LICENSE_KEY}")
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your bot token in the script!")
        sys.exit(1)
    bot.run(BOT_TOKEN)
EOF

chmod +x /opt/svmipv4_bot/svmipv4_bot.py

echo -e "${GREEN}✅ Bot script created!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 9: Create Systemd Service${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cat > /etc/systemd/system/svmipv4-bot.service << EOF
[Unit]
Description=SVMIPV4 BOT - Real IPv4 VPS Management
After=network.target libvirtd.service
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/svmipv4_bot
ExecStart=/usr/bin/python3 /opt/svmipv4_bot/svmipv4_bot.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/svmipv4_bot/bot.log
StandardError=append:/var/log/svmipv4_bot/error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo -e "${GREEN}✅ Systemd service created!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 10: Configure Firewall${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

# Configure UFW
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5900:5999/tcp
ufw allow 22000:22999/tcp
ufw allow 53/udp
ufw --force enable

echo -e "${GREEN}✅ Firewall configured!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 11: Setup Log Rotation${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cat > /etc/logrotate.d/svmipv4-bot << EOF
/var/log/svmipv4_bot/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 root root
}
EOF

echo -e "${GREEN}✅ Log rotation configured!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 12: Create Admin Script${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cat > /usr/local/bin/svmipv4-admin << 'EOF'
#!/bin/bash
# SVMIPV4 Admin Management Script

case "$1" in
    start)
        systemctl start svmipv4-bot
        echo "SVMIPV4 Bot Started"
        ;;
    stop)
        systemctl stop svmipv4-bot
        echo "SVMIPV4 Bot Stopped"
        ;;
    restart)
        systemctl restart svmipv4-bot
        echo "SVMIPV4 Bot Restarted"
        ;;
    status)
        systemctl status svmipv4-bot
        ;;
    logs)
        tail -f /var/log/svmipv4_bot/bot.log
        ;;
    error)
        tail -f /var/log/svmipv4_bot/error.log
        ;;
    *)
        echo "SVMIPV4 Admin Script"
        echo "Usage: $0 {start|stop|restart|status|logs|error}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/svmipv4-admin

echo -e "${GREEN}✅ Admin script created!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 13: Create Uninstall Script${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

cat > /opt/svmipv4_bot/uninstall.sh << 'EOF'
#!/bin/bash
echo "⚠️  This will remove SVMIPV4 BOT completely!"
read -p "Are you sure? (y/N): " confirm
if [[ $confirm == [yY] ]]; then
    systemctl stop svmipv4-bot
    systemctl disable svmipv4-bot
    rm -f /etc/systemd/system/svmipv4-bot.service
    rm -rf /opt/svmipv4_bot
    rm -rf /etc/svmipv4_bot
    rm -rf /var/log/svmipv4_bot
    rm -f /usr/local/bin/svmipv4-admin
    rm -f /etc/logrotate.d/svmipv4-bot
    systemctl daemon-reload
    echo "✅ SVMIPV4 BOT removed successfully!"
fi
EOF

chmod +x /opt/svmipv4_bot/uninstall.sh

echo -e "${GREEN}✅ Uninstall script created!${NC}"

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}STEP 14: Installation Complete!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${BOLD}${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║${NC}     ${BOLD}✅ SVMIPV4 BOT INSTALLED SUCCESSFULLY! ✅${NC}                ${GREEN}║${NC}"
echo -e "${BOLD}${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}📋 Installation Summary:${NC}"
echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Bot Name:${NC} SVMIPV4 BOT"
echo -e "${GREEN}✅ Creator:${NC} Ankit Dev"
echo -e "${GREEN}✅ License:${NC} AnkitDev99\$@"
echo -e "${GREEN}✅ Version:${NC} 2.0"
echo -e "${GREEN}✅ Installation Path:${NC} /opt/svmipv4_bot"
echo -e "${GREEN}✅ Config Path:${NC} /etc/svmipv4_bot"
echo -e "${GREEN}✅ Logs Path:${NC} /var/log/svmipv4_bot"
echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "${WHITE}1. Edit bot token in:${NC} nano /opt/svmipv4_bot/svmipv4_bot.py"
echo -e "${WHITE}2. Set your Admin ID in the script${NC}"
echo -e "${WHITE}3. Start the bot:${NC} svmipv4-admin start"
echo -e "${WHITE}4. Check status:${NC} svmipv4-admin status"
echo -e "${WHITE}5. View logs:${NC} svmipv4-admin logs"
echo ""

echo -e "${GREEN}🔧 Admin Commands:${NC}"
echo -e "${CYAN}  svmipv4-admin start   ${NC}- Start the bot"
echo -e "${CYAN}  svmipv4-admin stop    ${NC}- Stop the bot"
echo -e "${CYAN}  svmipv4-admin restart ${NC}- Restart the bot"
echo -e "${CYAN}  svmipv4-admin status  ${NC}- Check bot status"
echo -e "${CYAN}  svmipv4-admin logs    ${NC}- View bot logs"
echo -e "${CYAN}  svmipv4-admin error   ${NC}- View error logs"
echo ""

echo -e "${PURPLE}🔑 License Verification:${NC}"
echo -e "${WHITE}  Use command in Discord: ${CYAN}/license AnkitDev99\$@${NC}"
echo ""

echo -e "${BOLD}${GREEN}🎉 SVMIPV4 BOT is ready to use! 🎉${NC}"
echo ""

# Final check
echo -e "${YELLOW}Do you want to edit the bot token now? (y/N):${NC}"
read -p "" edit_token
if [[ $edit_token == [yY] ]]; then
    nano /opt/svmipv4_bot/svmipv4_bot.py
fi

echo -e "${GREEN}Installation complete! Use 'svmipv4-admin start' to launch the bot.${NC}"
