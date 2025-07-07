#!/usr/bin/env python3
"""
TCP Remote Setup Script
Dr. Sam Mitchell - Hardware Security Engineer

Automated setup for seamless gentoo.local access
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    
    requirements = [
        "asyncssh>=2.13.0",
        "asyncio-compat>=0.1.0"
    ]
    
    for req in requirements:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", req], 
                         check=True, capture_output=True)
            print(f"✓ Installed {req}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {req}: {e}")
            return False
    
    return True

def setup_ssh_config():
    """Setup SSH configuration for gentoo.local"""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    
    config_file = ssh_dir / "config"
    
    # SSH configuration for gentoo.local
    gentoo_config = """
# TCP Consortium gentoo.local configuration
Host gentoo.local tcp-gentoo tcp-gentoo.consortium.net
    HostName tcp-gentoo.consortium.net
    User {username}
    Port 22
    IdentityFile ~/.ssh/tcp_rsa
    KeepAlive yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel QUIET

"""
    
    username = input("Enter your TCP consortium username: ").strip()
    if not username:
        username = os.getenv('USER', 'researcher')
    
    gentoo_config = gentoo_config.format(username=username)
    
    # Read existing config
    existing_config = ""
    if config_file.exists():
        with open(config_file, 'r') as f:
            existing_config = f.read()
    
    # Add gentoo config if not present
    if "gentoo.local" not in existing_config:
        with open(config_file, 'a') as f:
            f.write(gentoo_config)
        print("✓ Added gentoo.local SSH configuration")
    else:
        print("✓ SSH configuration already present")
    
    # Set proper permissions
    os.chmod(config_file, 0o600)
    
    return username

def setup_ssh_key(username):
    """Setup SSH key for gentoo.local"""
    ssh_dir = Path.home() / ".ssh"
    key_file = ssh_dir / "tcp_rsa"
    
    if key_file.exists():
        print("✓ SSH key already exists")
        return True
    
    print("Generating SSH key for TCP consortium...")
    
    try:
        subprocess.run([
            "ssh-keygen", 
            "-t", "ed25519",
            "-f", str(key_file),
            "-N", "",  # No passphrase
            "-C", f"{username}@tcp-consortium"
        ], check=True, capture_output=True)
        
        print("✓ Generated SSH key")
        
        # Set proper permissions
        os.chmod(key_file, 0o600)
        os.chmod(f"{key_file}.pub", 0o644)
        
        # Display public key for manual registration
        with open(f"{key_file}.pub", 'r') as f:
            public_key = f.read().strip()
        
        print("\n" + "="*60)
        print("📋 MANUAL STEP REQUIRED:")
        print("Copy this public key and send to Sam Mitchell for access:")
        print("="*60)
        print(public_key)
        print("="*60)
        print("📧 Email: sam.mitchell@tcp-consortium.org")
        print("💬 Slack: @sam-mitchell")
        print("="*60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate SSH key: {e}")
        return False

def test_connection():
    """Test connection to gentoo.local"""
    print("\nTesting connection to gentoo.local...")
    
    try:
        result = subprocess.run([
            "ssh", 
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes",
            "gentoo.local", 
            "echo 'Connection successful'"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✓ Connection to gentoo.local successful")
            return True
        else:
            print("❌ Connection failed - key may not be registered yet")
            print("   Wait for SSH key approval from Sam Mitchell")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection timeout - check VPN/network")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def create_example_script():
    """Create example usage script"""
    example_script = Path.home() / "tcp_remote_example.py"
    
    script_content = '''#!/usr/bin/env python3
"""
TCP Remote Example Usage
Auto-generated by setup script
"""

# Add TCP remote tools to path
import sys
sys.path.insert(0, "{script_dir}")

from tcp_remote_api import validate, benchmark, status, run, TCPSession

def main():
    print("TCP Remote API Example")
    print("=" * 40)
    
    try:
        # Simple status check
        print("1. Checking gentoo.local status...")
        sys_status = status()
        print(f"   CPU cores: {{sys_status['cpu']['cores']}}")
        print(f"   Available memory: {{sys_status['memory']['available_gb']}}GB")
        
        # Run simple command
        print("\\n2. Running test command...")
        result = run("hostname && uptime")
        print(f"   Output: {{result['stdout'].strip()}}")
        
        # TCP validation (comment out if no descriptors available)
        # print("\\n3. TCP validation test...")
        # sample_descriptors = [b"TCP\\x02" + b"\\x00" * 20 for _ in range(5)]
        # validation_result = validate(sample_descriptors)
        # print(f"   Validation result: {{validation_result}}")
        
        print("\\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {{e}}")
        print("\\nTroubleshooting:")
        print("1. Check VPN connection")
        print("2. Verify SSH key is registered")
        print("3. Contact Sam Mitchell if issues persist")

if __name__ == "__main__":
    main()
'''
    
    script_dir = Path(__file__).parent.absolute()
    script_content = script_content.format(script_dir=script_dir)
    
    with open(example_script, 'w') as f:
        f.write(script_content)
    
    os.chmod(example_script, 0o755)
    print(f"✓ Created example script: {example_script}")

def main():
    """Main setup process"""
    print("TCP Remote Access Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup SSH configuration
    username = setup_ssh_config()
    
    # Setup SSH key
    if not setup_ssh_key(username):
        sys.exit(1)
    
    # Create example script
    create_example_script()
    
    # Test connection (may fail if key not registered yet)
    connection_success = test_connection()
    
    print("\n" + "=" * 60)
    print("🎉 TCP Remote Setup Complete!")
    print("=" * 60)
    
    if connection_success:
        print("✓ Ready to use gentoo.local immediately")
        print("\\n📝 Quick start:")
        print("   python tcp_remote_example.py")
        print("\\n🐍 In Python:")
        print("   from tcp_remote_api import status, run, validate")
        print("   print(status())  # Get system status")
        print("   run('echo Hello from gentoo.local')  # Run command")
    else:
        print("⏳ SSH key registration pending")
        print("\\n📧 Next steps:")
        print("1. Send your public key to Sam Mitchell")
        print("2. Wait for approval notification")
        print("3. Test: ssh gentoo.local")
        print("4. Run: python tcp_remote_example.py")
    
    print("\\n📚 Documentation:")
    print("   ~/tcp_remote_example.py - Usage examples")
    print("   tcp_remote_api.py - Full API reference")
    print("\\n🔧 Support:")
    print("   sam.mitchell@tcp-consortium.org")
    print("   #gentoo-local Slack channel")

if __name__ == "__main__":
    main()