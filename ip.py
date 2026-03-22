#!/usr/bin/env python3
"""
Ankit Dev VPS Management Bot
Real IPv4 VPS Management with License Verification
Created by: Ankit Dev
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import json
import sqlite3
import subprocess
import uuid
import time
import logging
import ipaddress
import os
import shutil
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
import netifaces
import random
import psutil

# ==================== CONFIGURATION ====================
BOT_TOKEN = ""  # Replace with your bot token
ADMIN_ID = 1405866008127864852  # Replace with your Discord Admin ID
ADMIN_NAME = "Ankit Dev"
BOT_NAME = "AnkitVPS Bot"
LOGO_URL = "https://i.imgur.com/your-logo.png"  # Replace with your logo URL
LICENSE_KEY = "AnkitDev99$@"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ankit_vps_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VPSInstance:
    """VPS Instance Data Class"""
    vps_id: str
    owner_id: int
    name: str
    cpu_cores: int
    ram_mb: int
    disk_gb: int
    ipv4: str
    mac: str
    status: str
    vnc_port: int
    ssh_port: int
    created_at: str
    expires_at: str
    os_template: str
    password: str

class LicenseManager:
    """License Key Management System"""
    
    def __init__(self, db_path: str = '/opt/ankit_vps_bot/license.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize license database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                user_id INTEGER PRIMARY KEY,
                license_key TEXT,
                verified_at TEXT,
                expires_at TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()
    
    def verify_license(self, user_id: int, license_key: str) -> bool:
        """Verify license key"""
        if license_key != LICENSE_KEY:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM licenses WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE licenses 
                SET verified_at = ?, expires_at = ?, is_active = 1
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), 
                  (datetime.now() + timedelta(days=365)).isoformat(),
                  user_id))
        else:
            cursor.execute('''
                INSERT INTO licenses (user_id, license_key, verified_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (user_id, license_key, datetime.now().isoformat(),
                  (datetime.now() + timedelta(days=365)).isoformat()))
        
        conn.commit()
        conn.close()
        return True
    
    def is_verified(self, user_id: int) -> bool:
        """Check if user is verified"""
        if user_id == ADMIN_ID:
            return True
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT is_active, expires_at FROM licenses 
            WHERE user_id = ? AND expires_at > ?
        ''', (user_id, datetime.now().isoformat()))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None and result[0] == 1
    
    def get_license_info(self, user_id: int) -> Optional[Dict]:
        """Get license information"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM licenses WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

class DatabaseManager:
    """SQLite Database Manager"""
    
    def __init__(self, db_path: str = '/opt/ankit_vps_bot/vps_bot.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                discord_name TEXT,
                balance REAL DEFAULT 0,
                total_vps INTEGER DEFAULT 0,
                created_at TEXT,
                last_active TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vps_instances (
                vps_id TEXT PRIMARY KEY,
                owner_id INTEGER,
                name TEXT,
                cpu_cores INTEGER,
                ram_mb INTEGER,
                disk_gb INTEGER,
                ipv4 TEXT,
                mac TEXT,
                status TEXT,
                vnc_port INTEGER,
                ssh_port INTEGER,
                created_at TEXT,
                expires_at TEXT,
                os_template TEXT,
                password TEXT,
                FOREIGN KEY (owner_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def add_user(self, user_id: int, username: str, discord_name: str) -> bool:
        """Add new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, discord_name, created_at, last_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, discord_name, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user info"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def add_vps(self, vps: VPSInstance) -> bool:
        """Add VPS to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vps_instances 
                (vps_id, owner_id, name, cpu_cores, ram_mb, disk_gb, ipv4, mac, 
                 status, vnc_port, ssh_port, created_at, expires_at, os_template, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vps.vps_id, vps.owner_id, vps.name, vps.cpu_cores, vps.ram_mb,
                vps.disk_gb, vps.ipv4, vps.mac, vps.status, vps.vnc_port,
                vps.ssh_port, vps.created_at, vps.expires_at, vps.os_template, vps.password
            ))
            conn.commit()
            
            cursor.execute('''
                UPDATE users SET total_vps = (
                    SELECT COUNT(*) FROM vps_instances WHERE owner_id = ? AND status != 'deleted'
                ) WHERE user_id = ?
            ''', (vps.owner_id, vps.owner_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding VPS: {e}")
            return False
    
    def get_user_vps(self, user_id: int) -> List[Dict]:
        """Get all VPS for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM vps_instances 
                WHERE owner_id = ? AND status != 'deleted'
                ORDER BY created_at DESC
            ''', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user VPS: {e}")
            return []
    
    def get_vps(self, vps_id: str) -> Optional[Dict]:
        """Get specific VPS"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM vps_instances WHERE vps_id = ?', (vps_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting VPS: {e}")
            return None
    
    def update_vps_status(self, vps_id: str, status: str) -> bool:
        """Update VPS status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE vps_instances SET status = ? WHERE vps_id = ?', (status, vps_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating VPS status: {e}")
            return False
    
    def delete_vps(self, vps_id: str) -> bool:
        """Soft delete VPS"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE vps_instances SET status = ? WHERE vps_id = ?', ('deleted', vps_id))
            
            cursor.execute('SELECT owner_id FROM vps_instances WHERE vps_id = ?', (vps_id,))
            owner = cursor.fetchone()
            
            if owner:
                cursor.execute('''
                    UPDATE users SET total_vps = (
                        SELECT COUNT(*) FROM vps_instances WHERE owner_id = ? AND status != 'deleted'
                    ) WHERE user_id = ?
                ''', (owner[0], owner[0]))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting VPS: {e}")
            return False

class NetworkManager:
    """Network Management for IPv4 Allocation"""
    
    def __init__(self):
        self.network_config = self.load_network_config()
    
    def load_network_config(self) -> Dict:
        """Load network configuration"""
        config = {
            'subnet': '10.10.0.0/16',
            'gateway': '10.10.0.1',
            'bridge': 'br0',
            'dns': ['8.8.8.8', '1.1.1.1'],
            'available_range': {
                'start': '10.10.1.1',
                'end': '10.10.255.254'
            }
        }
        self.create_bridge(config['bridge'])
        return config
    
    def create_bridge(self, bridge_name: str):
        """Create network bridge"""
        try:
            result = subprocess.run(['ip', 'link', 'show', bridge_name], capture_output=True)
            if result.returncode != 0:
                subprocess.run(['ip', 'link', 'add', bridge_name, 'type', 'bridge'], check=True)
                subprocess.run(['ip', 'link', 'set', bridge_name, 'up'], check=True)
                
                interfaces = netifaces.interfaces()
                main_iface = None
                for iface in interfaces:
                    if iface.startswith('eth') or iface.startswith('ens') or iface.startswith('enp'):
                        main_iface = iface
                        break
                
                if main_iface:
                    subprocess.run(['ip', 'link', 'set', main_iface, 'master', bridge_name], check=True)
                    subprocess.run(['ip', 'addr', 'add', f"{self.network_config['gateway']}/16", 'dev', bridge_name], check=True)
                    logger.info(f"Network bridge {bridge_name} created")
        except Exception as e:
            logger.error(f"Error creating bridge: {e}")
    
    def allocate_ip(self) -> Tuple[str, str]:
        """Allocate new IPv4 address"""
        try:
            conn = sqlite3.connect('/opt/ankit_vps_bot/vps_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT ipv4 FROM vps_instances WHERE status != "deleted"')
            used_ips = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            start_ip = ipaddress.IPv4Address(self.network_config['available_range']['start'])
            end_ip = ipaddress.IPv4Address(self.network_config['available_range']['end'])
            
            current = start_ip
            while current <= end_ip:
                ip_str = str(current)
                if ip_str not in used_ips and ip_str != self.network_config['gateway']:
                    mac = self.generate_mac(ip_str)
                    return ip_str, mac
                current += 1
            
            raise Exception("No available IP addresses")
        except Exception as e:
            logger.error(f"IP allocation failed: {e}")
            raise
    
    def generate_mac(self, ip_address: str) -> str:
        """Generate MAC address from IP"""
        ip_int = int(ipaddress.IPv4Address(ip_address))
        mac = f"52:54:00:{((ip_int >> 16) & 0xFF):02x}:{((ip_int >> 8) & 0xFF):02x}:{(ip_int & 0xFF):02x}"
        return mac

class VPSManager:
    """VPS Management using KVM/QEMU"""
    
    def __init__(self, db_manager: DatabaseManager, network_manager: NetworkManager):
        self.db = db_manager
        self.network = network_manager
        self.vps_path = Path('/var/lib/libvirt/images')
        self.config_path = Path('/etc/libvirt/qemu')
        self.setup_directories()
    
    def setup_directories(self):
        """Create required directories"""
        self.vps_path.mkdir(parents=True, exist_ok=True)
        self.config_path.mkdir(parents=True, exist_ok=True)
        Path('/var/lib/libvirt/cloud-init').mkdir(parents=True, exist_ok=True)
    
    def generate_password(self, length: int = 12) -> str:
        """Generate random password"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_vps(self, user_id: int, name: str, cpu: int, ram: int, disk: int, os_template: str = 'ubuntu2204') -> Optional[VPSInstance]:
        """Create a new VPS instance"""
        try:
            vps_id = str(uuid.uuid4())[:8]
            ipv4, mac = self.network.allocate_ip()
            password = self.generate_password()
            vnc_port = random.randint(5901, 5999)
            ssh_port = random.randint(22000, 22999)
            
            disk_path = self.vps_path / f"{vps_id}.qcow2"
            subprocess.run([
                'qemu-img', 'create', '-f', 'qcow2',
                str(disk_path), f"{disk}G"
            ], check=True)
            
            xml_config = self.create_vm_config(vps_id, name, cpu, ram, disk_path, ipv4, mac, vnc_port, ssh_port)
            self.define_vm(xml_config, vps_id)
            self.start_vm(vps_id)
            
            time.sleep(5)
            
            vps = VPSInstance(
                vps_id=vps_id,
                owner_id=user_id,
                name=name,
                cpu_cores=cpu,
                ram_mb=ram,
                disk_gb=disk,
                ipv4=ipv4,
                mac=mac,
                status='running',
                vnc_port=vnc_port,
                ssh_port=ssh_port,
                created_at=datetime.now().isoformat(),
                expires_at=(datetime.now() + timedelta(days=30)).isoformat(),
                os_template=os_template,
                password=password
            )
            
            self.db.add_vps(vps)
            logger.info(f"VPS {vps_id} created successfully")
            return vps
            
        except Exception as e:
            logger.error(f"Failed to create VPS: {e}")
            return None
    
    def create_vm_config(self, vps_id: str, name: str, cpu: int, ram: int, disk_path: Path,
                        ip: str, mac: str, vnc_port: int, ssh_port: int) -> str:
        """Create VM XML configuration"""
        return f"""
<domain type='kvm'>
  <name>{vps_id}</name>
  <memory unit='MiB'>{ram}</memory>
  <currentMemory unit='MiB'>{ram}</currentMemory>
  <vcpu placement='static'>{cpu}</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='hd'/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{disk_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='bridge'>
      <mac address='{mac}'/>
      <source bridge='br0'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='{vnc_port}' listen='0.0.0.0'/>
    <console type='pty'/>
  </devices>
</domain>"""
    
    def define_vm(self, xml_config: str, vps_id: str):
        """Define VM in libvirt"""
        xml_path = self.config_path / f"{vps_id}.xml"
        with open(xml_path, 'w') as f:
            f.write(xml_config)
        subprocess.run(['virsh', 'define', str(xml_path)], check=True)
    
    def start_vm(self, vps_id: str):
        subprocess.run(['virsh', 'start', vps_id], check=True)
    
    def stop_vm(self, vps_id: str):
        subprocess.run(['virsh', 'shutdown', vps_id], capture_output=True)
    
    def delete_vm(self, vps_id: str):
        subprocess.run(['virsh', 'destroy', vps_id], capture_output=True)
        subprocess.run(['virsh', 'undefine', vps_id], capture_output=True)
        disk_path = self.vps_path / f"{vps_id}.qcow2"
        if disk_path.exists():
            disk_path.unlink()
    
    def get_vm_status(self, vps_id: str) -> str:
        try:
            result = subprocess.run(['virsh', 'domstate', vps_id], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return 'unknown'

class AnkitVPSCog(commands.Cog):
    """Ankit Dev VPS Management Cog with License Verification"""
    
    def __init__(self, bot, db_manager: DatabaseManager, vps_manager: VPSManager, license_manager: LicenseManager):
        self.bot = bot
        self.db = db_manager
        self.vps_manager = vps_manager
        self.license_manager = license_manager
        self.logo_url = LOGO_URL
        self.admin_id = ADMIN_ID
        self.admin_name = ADMIN_NAME
        self.bot_name = BOT_NAME
    
    def check_license(self, user_id: int) -> bool:
        """Check if user has valid license"""
        return self.license_manager.is_verified(user_id)
    
    def create_embed(self, title: str, description: str = "", color: int = 0x00ff00) -> discord.Embed:
        """Create styled embed with logo and branding"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        embed.set_thumbnail(url=self.logo_url)
        embed.set_footer(
            text=f"Powered by {self.admin_name} • {self.bot_name}",
            icon_url=self.logo_url
        )
        return embed
    
    @app_commands.command(name="license", description="Verify your license key to use the bot")
    @app_commands.describe(key="Enter your license key (AnkitDev99$@)")
    async def verify_license(self, interaction: discord.Interaction, key: str):
        """Verify license key command"""
        if self.license_manager.verify_license(interaction.user.id, key):
            embed = self.create_embed(
                "✅ License Verified Successfully!",
                f"Welcome to **{self.bot_name}**!\n\n"
                f"Your license is now active and valid for 365 days.\n"
                f"You can now use all VPS management commands.",
                color=0x00ff00
            )
            embed.add_field(name="🔑 License Key", value=f"`{key}`", inline=True)
            embed.add_field(name="📅 Valid Until", value=(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="👤 Verified By", value=self.admin_name, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed = self.create_embed(
                "❌ Invalid License Key!",
                "The license key you entered is incorrect.\n\n"
                f"Please contact **{self.admin_name}** to get a valid license key.\n"
                f"**License Key:** `{LICENSE_KEY}`",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="help", description="Show all available commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show help menu"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"You need to verify your license first to use this bot.\n\n"
                f"**License Key:** `{LICENSE_KEY}`\n"
                f"Use `/license {LICENSE_KEY}` to activate your account.\n\n"
                f"Contact **{self.admin_name}** for support.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = self.create_embed(
            f"🖥️ {self.bot_name} - Help Menu",
            f"Complete VPS Management System with Real IPv4 Addresses\n\n"
            f"**Created by:** {self.admin_name}",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📦 **VPS Management**",
            value="`/create` - Create new VPS\n"
                  "`/list` - List your VPS\n"
                  "`/info <id>` - Get VPS details\n"
                  "`/status <id>` - Check VPS status\n"
                  "`/control <id> <action>` - Start/Stop/Restart\n"
                  "`/delete <id>` - Delete VPS",
            inline=False
        )
        
        embed.add_field(
            name="📊 **System Info**",
            value="`/resources` - Show system resources\n"
                  "`/limits` - Show VPS limits\n"
                  "`/licenseinfo` - Check your license status",
            inline=False
        )
        
        embed.add_field(
            name="💻 **Access Details**",
            value="**SSH:** `ssh {username}@{ip} -p {port}`\n"
                  "**VNC:** `vnc://{ip}:{port}`\n"
                  "**Password:** Provided on creation",
            inline=False
        )
        
        embed.add_field(
            name="🎯 **Resource Limits**",
            value="• CPU: 1-8 cores\n"
                  "• RAM: 512MB - 16GB\n"
                  "• Disk: 10GB - 100GB\n"
                  "• Max VPS: 5 per user",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="licenseinfo", description="Check your license information")
    async def license_info(self, interaction: discord.Interaction):
        """Show license information"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ No Active License",
                f"You don't have an active license.\n\n"
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        license_info = self.license_manager.get_license_info(interaction.user.id)
        if license_info:
            embed = self.create_embed(
                "🔑 License Information",
                f"Your license status for **{self.bot_name}**",
                color=0x00ff00
            )
            embed.add_field(name="✅ Status", value="Active", inline=True)
            embed.add_field(name="📅 Verified On", value=license_info['verified_at'][:10], inline=True)
            embed.add_field(name="⏰ Expires On", value=license_info['expires_at'][:10], inline=True)
            embed.add_field(name="🔑 License Key", value=f"`{license_info['license_key']}`", inline=False)
            embed.add_field(name="👤 Licensed To", value=f"<@{interaction.user.id}>", inline=True)
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="create", description="Create a new VPS")
    @app_commands.describe(
        name="VPS name (lowercase, letters/numbers/hyphens)",
        cpu="CPU cores (1-8)",
        ram="RAM in MB (512-16384)",
        disk="Disk space in GB (10-100)",
        os="OS template (ubuntu2204, ubuntu2004, debian11)"
    )
    async def create_vps(
        self, 
        interaction: discord.Interaction,
        name: str,
        cpu: app_commands.Range[int, 1, 8],
        ram: app_commands.Range[int, 512, 16384],
        disk: app_commands.Range[int, 10, 100],
        os: str = "ubuntu2204"
    ):
        """Create a new VPS - License Required"""
        
        # Check license first
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"You need to verify your license first.\n\n"
                f"**License Key:** `{LICENSE_KEY}`\n"
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Add user if not exists
        if not self.db.get_user(interaction.user.id):
            self.db.add_user(interaction.user.id, interaction.user.name, interaction.user.display_name)
        
        # Validate name
        if not re.match(r'^[a-z0-9-]+$', name):
            embed = self.create_embed(
                "❌ Invalid Name",
                "Name must contain only lowercase letters, numbers, and hyphens",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check VPS limit
        user_vps = self.db.get_user_vps(interaction.user.id)
        if len(user_vps) >= 5:
            embed = self.create_embed(
                "❌ VPS Limit Reached",
                f"You have reached the maximum limit of 5 VPS.\n"
                f"Current: {len(user_vps)}/5",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            vps = self.vps_manager.create_vps(
                interaction.user.id, name, cpu, ram, disk, os
            )
            
            if vps:
                embed = self.create_embed(
                    "✅ VPS Created Successfully!",
                    f"Your VPS **{name}** has been created and is ready to use",
                    color=0x00ff00
                )
                
                embed.add_field(name="🆔 VPS ID", value=f"`{vps.vps_id}`", inline=True)
                embed.add_field(name="🌐 IPv4 Address", value=f"`{vps.ipv4}`", inline=True)
                embed.add_field(name="💻 SSH Port", value=f"`{vps.ssh_port}`", inline=True)
                embed.add_field(name="🎮 VNC Port", value=f"`{vps.vnc_port}`", inline=True)
                embed.add_field(name="🔑 Password", value=f"`{vps.password}`", inline=True)
                embed.add_field(name="⚙️ Resources", value=f"{cpu}C / {ram}MB / {disk}GB", inline=True)
                
                embed.add_field(
                    name="📝 SSH Access",
                    value=f"```bash\nssh {name}@{vps.ipv4} -p {vps.ssh_port}\nPassword: {vps.password}```",
                    inline=False
                )
                
                embed.add_field(
                    name="⚠️ Important",
                    value="• Save this information securely!\n• Password will not be shown again\n• Use `/info <id>` to retrieve details",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
            else:
                embed = self.create_embed(
                    "❌ Creation Failed",
                    "Failed to create VPS. Please contact administrator.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"VPS creation error: {e}")
            embed = self.create_embed(
                "❌ Error",
                f"Error creating VPS: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="list", description="List your VPS instances")
    async def list_vps(self, interaction: discord.Interaction):
        """List user's VPS"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        vps_list = self.db.get_user_vps(interaction.user.id)
        
        if not vps_list:
            embed = self.create_embed(
                "📭 No VPS Found",
                "You don't have any VPS. Use `/create` to create one!",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = self.create_embed(
            f"📋 Your VPS Instances",
            f"Total: {len(vps_list)}/5 VPS",
            color=0x00ff00
        )
        
        for vps in vps_list:
            status = self.vps_manager.get_vm_status(vps['vps_id'])
            status_emoji = "🟢" if status == "running" else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} {vps['name']}",
                value=f"**ID:** `{vps['vps_id']}`\n"
                      f"**IP:** `{vps['ipv4']}`\n"
                      f"**Specs:** {vps['cpu_cores']}C / {vps['ram_mb']}MB / {vps['disk_gb']}GB\n"
                      f"**Expires:** {vps['expires_at'][:10]}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="info", description="Get detailed VPS information")
    @app_commands.describe(vps_id="VPS ID to get information for")
    async def vps_info(self, interaction: discord.Interaction, vps_id: str):
        """Get detailed VPS info"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        vps = self.db.get_vps(vps_id)
        
        if not vps or vps['owner_id'] != interaction.user.id:
            embed = self.create_embed(
                "❌ Not Found",
                "VPS not found or you don't have permission",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        status = self.vps_manager.get_vm_status(vps_id)
        
        embed = self.create_embed(
            f"🖥️ VPS: {vps['name']}",
            f"Detailed information for VPS `{vps_id}`",
            0x00ff00 if status == "running" else 0xffaa00
        )
        
        embed.add_field(name="🌐 IPv4 Address", value=f"`{vps['ipv4']}`", inline=True)
        embed.add_field(name="🔌 MAC Address", value=f"`{vps['mac']}`", inline=True)
        embed.add_field(name="🟢 Status", value=f"`{status}`", inline=True)
        embed.add_field(name="💻 SSH Port", value=f"`{vps['ssh_port']}`", inline=True)
        embed.add_field(name="🎮 VNC Port", value=f"`{vps['vnc_port']}`", inline=True)
        embed.add_field(name="⚙️ Resources", value=f"{vps['cpu_cores']}C / {vps['ram_mb']}MB / {vps['disk_gb']}GB", inline=True)
        embed.add_field(name="📅 Created", value=vps['created_at'][:19], inline=True)
        embed.add_field(name="⏰ Expires", value=vps['expires_at'][:10], inline=True)
        embed.add_field(name="🔑 Password", value=f"`{vps['password']}`", inline=True)
        
        embed.add_field(
            name="📝 SSH Access",
            value=f"```bash\nssh {vps['name']}@{vps['ipv4']} -p {vps['ssh_port']}\nPassword: {vps['password']}```",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="status", description="Check VPS status")
    @app_commands.describe(vps_id="VPS ID to check")
    async def vps_status(self, interaction: discord.Interaction, vps_id: str):
        """Check VPS status"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        vps = self.db.get_vps(vps_id)
        
        if not vps or vps['owner_id'] != interaction.user.id:
            embed = self.create_embed(
                "❌ Not Found",
                "VPS not found or you don't have permission",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        status = self.vps_manager.get_vm_status(vps_id)
        
        embed = self.create_embed(
            f"📊 VPS Status: {vps['name']}",
            f"**ID:** `{vps_id}`\n**Status:** `{status}`",
            0x00ff00 if status == "running" else 0xffaa00
        )
        
        embed.add_field(name="🌐 IP Address", value=f"`{vps['ipv4']}`", inline=True)
        embed.add_field(name="💻 SSH Port", value=f"`{vps['ssh_port']}`", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="control", description="Control VPS (start/stop/restart)")
    @app_commands.describe(
        vps_id="VPS ID to control",
        action="Action: start, stop, or restart"
    )
    async def vps_control(
        self, 
        interaction: discord.Interaction,
        vps_id: str,
        action: str
    ):
        """Start/Stop/Restart VPS"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        vps = self.db.get_vps(vps_id)
        
        if not vps or vps['owner_id'] != interaction.user.id:
            embed = self.create_embed(
                "❌ Not Found",
                "VPS not found or you don't have permission",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        action = action.lower()
        
        if action not in ['start', 'stop', 'restart']:
            embed = self.create_embed(
                "❌ Invalid Action",
                "Use: start, stop, or restart",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            if action == 'start':
                self.vps_manager.start_vm(vps_id)
                embed = self.create_embed("✅ VPS Starting", f"VPS `{vps_id}` is starting...", 0x00ff00)
            elif action == 'stop':
                self.vps_manager.stop_vm(vps_id)
                embed = self.create_embed("⏹️ VPS Stopping", f"VPS `{vps_id}` is stopping...", 0xffaa00)
            elif action == 'restart':
                self.vps_manager.stop_vm(vps_id)
                time.sleep(2)
                self.vps_manager.start_vm(vps_id)
                embed = self.create_embed("🔄 VPS Restarting", f"VPS `{vps_id}` is restarting...", 0x00ff00)
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = self.create_embed("❌ Error", str(e), 0xff0000)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="delete", description="Delete a VPS")
    @app_commands.describe(vps_id="VPS ID to delete")
    async def delete_vps(self, interaction: discord.Interaction, vps_id: str):
        """Delete VPS with confirmation"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        vps = self.db.get_vps(vps_id)
        
        if not vps or vps['owner_id'] != interaction.user.id:
            embed = self.create_embed(
                "❌ Not Found",
                "VPS not found or you don't have permission",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None
            
            @discord.ui.button(label="✅ Confirm Delete", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                self.value = True
                self.stop()
            
            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                self.value = False
                self.stop()
        
        embed = self.create_embed(
            "⚠️ Confirm Deletion",
            f"Are you sure you want to delete VPS `{vps_id}`?\nThis action cannot be undone!",
            0xffaa00
        )
        
        view = ConfirmView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        await view.wait()
        
        if view.value:
            try:
                self.vps_manager.delete_vm(vps_id)
                self.db.delete_vps(vps_id)
                embed = self.create_embed("✅ Deleted", f"VPS `{vps_id}` has been deleted successfully!", 0x00ff00)
                await interaction.edit_original_response(embed=embed, view=None)
            except Exception as e:
                embed = self.create_embed("❌ Error", f"Error deleting VPS: {str(e)}", 0xff0000)
                await interaction.edit_original_response(embed=embed, view=None)
        else:
            embed = self.create_embed("❌ Cancelled", "Deletion cancelled", 0xffaa00)
            await interaction.edit_original_response(embed=embed, view=None)
    
    @app_commands.command(name="resources", description="Show system resources")
    async def show_resources(self, interaction: discord.Interaction):
        """Show available system resources"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        total_vps = len(self.db.get_user_vps(interaction.user.id))
        
        embed = self.create_embed(
            "💻 System Resources",
            f"**{self.bot_name}** - Real IPv4 VPS Management",
            0x00ff00
        )
        
        embed.add_field(
            name="🖥️ CPU",
            value=f"**Cores:** {cpu_count}\n**Usage:** {cpu_percent}%",
            inline=True
        )
        
        embed.add_field(
            name="🧠 Memory",
            value=f"**Total:** {memory.total / (1024**3):.1f} GB\n**Available:** {memory.available / (1024**3):.1f} GB\n**Used:** {memory.percent}%",
            inline=True
        )
        
        embed.add_field(
            name="💾 Disk",
            value=f"**Total:** {disk.total / (1024**3):.1f} GB\n**Free:** {disk.free / (1024**3):.1f} GB\n**Used:** {disk.percent}%",
            inline=True
        )
        
        embed.add_field(
            name="📊 Your VPS Usage",
            value=f"**Used:** {total_vps}/5\n**Available:** {5 - total_vps}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="limits", description="Show VPS limits")
    async def show_limits(self, interaction: discord.Interaction):
        """Show VPS limits"""
        if not self.check_license(interaction.user.id):
            embed = self.create_embed(
                "⚠️ License Required!",
                f"Use `/license {LICENSE_KEY}` to activate.",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = self.create_embed(
            "📊 VPS Limits & Specifications",
            f"**{self.bot_name}** - Real IPv4 VPS with dedicated resources",
            0x00ff00
        )
        
        embed.add_field(
            name="🎯 **Resource Limits**",
            value="• Max VPS per user: **5**\n"
                  "• CPU per VPS: **1-8 cores**\n"
                  "• RAM per VPS: **512MB - 16GB**\n"
                  "• Disk per VPS: **10GB - 100GB**\n"
                  "• License Validity: **365 days**",
            inline=False
        )
        
        embed.add_field(
            name="💻 **OS Templates**",
            value="• Ubuntu 22.04 LTS\n"
                  "• Ubuntu 20.04 LTS\n"
                  "• Debian 11",
            inline=True
        )
        
        embed.add_field(
            name="🔧 **Features**",
            value="• Dedicated IPv4 Address\n"
                  "• Full Root Access\n"
                  "• VNC Console Access\n"
                  "• SSH with Custom Port\n"
                  "• Resource Monitoring\n"
                  "• 24/7 Uptime",
            inline=True
        )
        
        embed.add_field(
            name="👤 **Support**",
            value=f"Created by: **{self.admin_name}**\n"
                  f"License Key: `{LICENSE_KEY}`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

class AnkitVPSBot:
    """Main Discord Bot with Ankit Dev Branding"""
    
    def __init__(self, token: str):
        self.token = token
        self.db = DatabaseManager()
        self.network = NetworkManager()
        self.vps_manager = VPSManager(self.db, self.network)
        self.license_manager = LicenseManager()
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Add cog
        self.bot.add_cog(AnkitVPSCog(self.bot, self.db, self.vps_manager, self.license_manager))
        
        @self.bot.event
        async def on_ready():
            logger.info(f'{BOT_NAME} logged in as {self.bot.user}')
            logger.info(f'Created by: {ADMIN_NAME}')
            try:
                synced = await self.bot.tree.sync()
                logger.info(f"Synced {len(synced)} commands")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
        
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("Command not found. Use `/help` for available commands.")
            else:
                logger.error(f"Command error: {error}")
    
    def run(self):
        """Run the bot"""
        self.bot.run(self.token)

def main():
    """Main entry point"""
    import sys
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Please set your bot token in the script")
        sys.exit(1)
    
    # Check required commands
    required_commands = ['virsh', 'qemu-img', 'ip']
    for cmd in required_commands:
        if not shutil.which(cmd):
            logger.error(f"Required command not found: {cmd}")
            print(f"Error: {cmd} is not installed. Please install required packages.")
            sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║     {BOT_NAME} - Starting...                                 ║
║     Created by: {ADMIN_NAME}                                 ║
║     License Key: {LICENSE_KEY}                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    bot = AnkitVPSBot(BOT_TOKEN)
    bot.run()

if __name__ == '__main__':
    main()
