#!/bin/bash
# Install development and security tools while monitoring TCP adaptation

echo "🚀 Installing Development & Security Tools"
echo "========================================"

ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 'bash -s' << 'EOF'
set -e

echo "📊 Starting command count: $(compgen -c | sort | uniq | wc -l)"
echo ""

echo "📦 Phase 1: Modern CLI Tools"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    exa \
    fzf \
    ag \
    jq \
    yq \
    httpie \
    direnv \
    tldr \
    neofetch \
    figlet \
    toilet \
    cowsay \
    lolcat \
    fortune-mod \
    sl \
    cmatrix \
    hollywood || true

echo "Commands after Phase 1: $(compgen -c | sort | uniq | wc -l)"

echo ""
echo "📦 Phase 2: Development Essentials"
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git-flow \
    git-extras \
    tig \
    lazygit \
    gh \
    hub \
    pre-commit \
    shellcheck \
    shfmt \
    black \
    flake8 \
    mypy \
    pylint \
    prettier \
    eslint || true

echo "Commands after Phase 2: $(compgen -c | sort | uniq | wc -l)"

echo ""
echo "📦 Phase 3: Container Tools"
# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
fi

DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    docker-compose \
    docker-buildx \
    ctop \
    lazydocker \
    dive \
    hadolint || true

echo "Commands after Phase 3: $(compgen -c | sort | uniq | wc -l)"

echo ""
echo "📦 Phase 4: Security Analysis"
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    nmap \
    masscan \
    zmap \
    rustscan \
    nikto \
    gobuster \
    dirb \
    wfuzz \
    sqlmap \
    hydra \
    john \
    hashcat \
    aircrack-ng \
    lynis \
    chkrootkit \
    rkhunter || true

echo "Commands after Phase 4: $(compgen -c | sort | uniq | wc -l)"

echo ""
echo "📦 Phase 5: System Analysis"
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    sysdig \
    bpftrace \
    perf-tools-unstable \
    flamegraph \
    stress-ng \
    sysbench \
    iperf3 \
    speedtest-cli \
    mtr-tiny \
    bandwhich || true

echo "Commands after Phase 5: $(compgen -c | sort | uniq | wc -l)"

echo ""
echo "📦 Phase 6: Rust Tools (cargo install)"
if command -v cargo &> /dev/null; then
    echo "Installing Rust-based tools..."
    cargo install --locked \
        tokei \
        hyperfine \
        sd \
        dust \
        procs \
        bottom \
        zoxide \
        starship || true
fi

echo ""
echo "✅ Installation Complete!"
echo "📊 Final command count: $(compgen -c | sort | uniq | wc -l)"
echo ""
echo "🔄 Waiting for TCP to discover new commands..."
sleep 10
echo "📊 TCP has analyzed: $(cat /opt/tcp-knowledge-system/data/discovered_commands.json | jq '.commands | length')"
EOF