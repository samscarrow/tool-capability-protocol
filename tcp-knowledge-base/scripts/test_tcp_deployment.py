#!/usr/bin/env python3
"""
Test TCP DigitalOcean deployment setup
"""

import os
import subprocess
import json


def test_secrets():
    """Test 1Password secret access"""
    print("🔐 Testing 1Password Secret Access")
    print("=" * 40)

    try:
        # Test Anthropic key
        result = subprocess.run(
            [
                "op",
                "item",
                "get",
                "ln3svnpksfk7l5zgvylp5ttqki",
                "--fields",
                "credential",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            anthropic_key = result.stdout.strip()
            print(
                f"✅ Anthropic API key: {anthropic_key[:20]}... ({len(anthropic_key)} chars)"
            )
        else:
            print(f"❌ Failed to get Anthropic key: {result.stderr}")
            return False

        # Test DigitalOcean token
        result = subprocess.run(
            [
                "op",
                "item",
                "get",
                "izkzdsruj2v6fdya5tzg7mo2sa",
                "--fields",
                "credential",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            do_token = result.stdout.strip()
            print(f"✅ DigitalOcean token: {do_token[:20]}... ({len(do_token)} chars)")
        else:
            print(f"❌ Failed to get DO token: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"❌ Secret test failed: {e}")
        return False


def test_doctl():
    """Test DigitalOcean CLI"""
    print("\n🌊 Testing DigitalOcean CLI")
    print("=" * 30)

    try:
        # Get DO token
        result = subprocess.run(
            [
                "op",
                "item",
                "get",
                "izkzdsruj2v6fdya5tzg7mo2sa",
                "--fields",
                "credential",
            ],
            capture_output=True,
            text=True,
        )
        do_token = result.stdout.strip()

        # Test doctl with token
        env = os.environ.copy()
        env["DIGITALOCEAN_ACCESS_TOKEN"] = do_token

        result = subprocess.run(
            ["doctl", "account", "get"], capture_output=True, text=True, env=env
        )

        if result.returncode == 0:
            print("✅ DigitalOcean account access verified")
            print(f"Account info: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ DigitalOcean access failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ doctl test failed: {e}")
        return False


def test_anthropic_api():
    """Test Anthropic API access"""
    print("\n🧠 Testing Anthropic API")
    print("=" * 25)

    try:
        # Get API key
        result = subprocess.run(
            [
                "op",
                "item",
                "get",
                "ln3svnpksfk7l5zgvylp5ttqki",
                "--fields",
                "credential",
            ],
            capture_output=True,
            text=True,
        )
        api_key = result.stdout.strip()

        # Quick API test
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="You are testing API connectivity.",
            messages=[
                {"role": "user", "content": "Respond with just 'API_TEST_SUCCESS'"}
            ],
            max_tokens=10,
        )

        if "API_TEST_SUCCESS" in response.content[0].text:
            print("✅ Anthropic API access verified")
            return True
        else:
            print(f"❌ Unexpected API response: {response.content[0].text}")
            return False

    except Exception as e:
        print(f"❌ Anthropic API test failed: {e}")
        return False


def create_deployment_config():
    """Create deployment configuration"""
    print("\n📋 Creating Deployment Configuration")
    print("=" * 40)

    config = {
        "deployment_name": "tcp-knowledge-growth",
        "droplet_config": {
            "size": "s-2vcpu-4gb",
            "region": "nyc1",
            "image": "ubuntu-22-04-x64",
        },
        "estimated_costs": {
            "droplet_monthly": 24.00,
            "api_calls_daily": 2.00,
            "total_monthly": 84.00,
        },
        "schedule": {
            "discovery_interval": "6 hours",
            "analysis_batch_size": 50,
            "daily_enhancement": "02:00",
        },
        "monitoring": {
            "log_retention": "30 days",
            "backup_frequency": "daily",
            "metrics_collection": True,
        },
    }

    with open("tcp_deployment_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✅ Configuration saved to tcp_deployment_config.json")
    print(f"💰 Estimated monthly cost: ${config['estimated_costs']['total_monthly']}")

    return config


def main():
    """Main test function"""
    print("🚀 TCP DigitalOcean Deployment Test Suite")
    print("=" * 45)

    all_tests_passed = True

    # Test secrets
    if not test_secrets():
        all_tests_passed = False

    # Test DigitalOcean CLI
    if not test_doctl():
        all_tests_passed = False

    # Test Anthropic API
    if not test_anthropic_api():
        all_tests_passed = False

    # Create config
    config = create_deployment_config()

    print(f"\n📊 Test Results Summary")
    print("=" * 25)

    if all_tests_passed:
        print("✅ All tests passed! Ready for deployment")
        print("\n🚀 Next Steps:")
        print("1. Review configuration in tcp_deployment_config.json")
        print("2. Run: ./deploy_tcp_with_secrets.sh")
        print("3. Monitor deployment with provided commands")
        print("\n🌱 Your TCP system will then:")
        print("   • Discover new Unix commands every 6 hours")
        print("   • Analyze them with Claude for security patterns")
        print("   • Build an continuously improving knowledge base")
        print("   • Provide microsecond AI safety decisions")
        print(
            f"   • Cost approximately ${config['estimated_costs']['total_monthly']}/month"
        )
    else:
        print("❌ Some tests failed. Please fix issues before deployment")

    return all_tests_passed


if __name__ == "__main__":
    main()
