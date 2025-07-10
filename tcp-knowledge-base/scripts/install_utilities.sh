#!/bin/bash
# Install comprehensive set of utilities on TCP droplet

echo "🚀 Installing Comprehensive Utility Suite"
echo "========================================"

ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
set -e

echo "📦 Phase 1: Development Tools"
echo "----------------------------"
apt-get update -qq
apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    meson \
    golang \
    rustc \
    cargo \
    nodejs \
    npm \
    ruby \
    perl \
    php-cli \
    lua5.4 \
    tcl \
    erlang \
    elixir \
    clang \
    llvm \
    valgrind \
    gdb \
    strace \
    ltrace

echo ""
echo "📦 Phase 2: System Administration"
echo "--------------------------------"
apt-get install -y --no-install-recommends \
    htop \
    iotop \
    iftop \
    nethogs \
    bmon \
    vnstat \
    sysstat \
    dstat \
    atop \
    glances \
    ncdu \
    tree \
    ranger \
    mc \
    tmux \
    screen \
    byobu \
    mosh \
    autossh \
    fail2ban \
    ufw \
    nmap \
    tcpdump \
    wireshark-common \
    tshark \
    traceroute \
    mtr \
    whois \
    dnsutils \
    net-tools \
    iproute2 \
    bridge-utils \
    vlan \
    ethtool

echo ""
echo "📦 Phase 3: File Management & Compression"
echo "---------------------------------------"
apt-get install -y --no-install-recommends \
    p7zip-full \
    unrar \
    lzop \
    lz4 \
    zstd \
    pigz \
    pbzip2 \
    pixz \
    plzip \
    rar \
    arj \
    cabextract \
    unace \
    sharutils \
    uudeview \
    mpack \
    lhasa \
    rclone \
    rsync \
    lftp \
    aria2 \
    axel \
    transmission-cli

echo ""
echo "📦 Phase 4: Text Processing & Editors"
echo "------------------------------------"
apt-get install -y --no-install-recommends \
    vim \
    neovim \
    emacs-nox \
    nano \
    ne \
    joe \
    jed \
    sed \
    awk \
    ripgrep \
    ag \
    ack \
    fzf \
    fd-find \
    bat \
    exa \
    jq \
    yq \
    xmlstarlet \
    html-xml-utils \
    pandoc \
    asciidoc \
    markdown \
    dos2unix \
    detox \
    rename

echo ""
echo "📦 Phase 5: Security & Forensics"
echo "-------------------------------"
apt-get install -y --no-install-recommends \
    john \
    hashcat \
    aircrack-ng \
    hydra \
    medusa \
    nikto \
    sqlmap \
    metasploit-framework \
    burpsuite \
    zaproxy \
    lynis \
    chkrootkit \
    rkhunter \
    aide \
    tripwire \
    ossec-hids \
    snort \
    suricata \
    clamav \
    foremost \
    scalpel \
    testdisk \
    photorec \
    autopsy \
    sleuthkit \
    volatility3 \
    binwalk \
    radare2 \
    ghidra || true  # Some might fail

echo ""
echo "📦 Phase 6: Container & Cloud Tools"
echo "----------------------------------"
# Docker already installed via curl method
curl -fsSL https://get.docker.com | sh || true
apt-get install -y --no-install-recommends \
    docker-compose \
    podman \
    buildah \
    skopeo \
    kubectl \
    helm \
    k9s \
    terraform \
    ansible \
    vagrant \
    packer \
    consul \
    nomad \
    vault

echo ""
echo "📦 Phase 7: Database & Data Tools"
echo "--------------------------------"
apt-get install -y --no-install-recommends \
    postgresql-client \
    mysql-client \
    mariadb-client \
    redis-tools \
    mongodb-clients \
    sqlite3 \
    influxdb-client \
    cassandra-tools \
    memcached-tools \
    rabbitmq-server \
    kafka \
    elasticsearch \
    logstash \
    kibana || true

echo ""
echo "📦 Phase 8: Monitoring & Observability"
echo "------------------------------------"
apt-get install -y --no-install-recommends \
    prometheus \
    grafana \
    telegraf \
    collectd \
    nagios4 \
    zabbix-agent \
    monit \
    supervisor \
    circus \
    pm2 || true

echo ""
echo "📦 Phase 9: Media & Graphics Tools"
echo "---------------------------------"
apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    graphicsmagick \
    sox \
    lame \
    flac \
    vorbis-tools \
    opus-tools \
    exiftool \
    mediainfo \
    jpegoptim \
    optipng \
    pngquant \
    webp \
    gifsicle \
    potrace \
    inkscape \
    ghostscript

echo ""
echo "📦 Phase 10: Scientific & Data Analysis"
echo "--------------------------------------"
apt-get install -y --no-install-recommends \
    octave \
    scilab \
    r-base \
    julia \
    maxima \
    gnuplot \
    grace \
    gsl-bin \
    bc \
    dc \
    calc \
    units \
    dateutils

echo ""
echo "✅ Installation Complete!"
echo ""
echo "📊 Counting new commands..."
compgen -c | sort | uniq | wc -l
echo ""
echo "🔄 Restarting TCP Knowledge Growth service..."
systemctl start tcp-knowledge-growth || echo "Service not configured for auto-restart"
EOF

echo ""
echo "🎯 All utilities installed! Monitor TCP adaptation with:"
echo "   python tcp_live_monitor.py"