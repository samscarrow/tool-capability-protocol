#!/bin/bash

# claude-orient-consortium - Identify agent's position in the TCP Research Consortium
# Builds on the /claude-orient concept to determine researcher identity based on CWD

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display header
show_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    🧭 TCP Research Consortium - Agent Orientation                    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to get current working directory
get_cwd() {
    pwd
}

# Function to identify researcher workspace
identify_workspace() {
    local cwd="$1"
    
    # Extract workspace from current directory
    if [[ "$cwd" =~ /consortium/([^/]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        echo "unknown"
    fi
}

# Function to load researcher identity
load_researcher_identity() {
    local workspace="$1"
    local cwd="$2"
    local identity_file
    
    # Find TCP project root
    local tcp_root="$cwd"
    while [[ ! -f "$tcp_root/pyproject.toml" ]] && [[ "$tcp_root" != "/" ]]; do
        tcp_root="$(dirname "$tcp_root")"
    done
    
    # Check for researcher-specific identity file
    if [[ -f "${tcp_root}/consortium/${workspace}/IDENTITY_CONTEXT_REMINDER.md" ]]; then
        identity_file="${tcp_root}/consortium/${workspace}/IDENTITY_CONTEXT_REMINDER.md"
    elif [[ -f "${tcp_root}/consortium/${workspace}/CLAUDE.md" ]]; then
        identity_file="${tcp_root}/consortium/${workspace}/CLAUDE.md"
    elif [[ -f "${cwd}/IDENTITY_CONTEXT_REMINDER.md" ]]; then
        identity_file="${cwd}/IDENTITY_CONTEXT_REMINDER.md"
    elif [[ -f "${cwd}/CLAUDE.md" ]]; then
        identity_file="${cwd}/CLAUDE.md"
    else
        identity_file=""
    fi
    
    echo "$identity_file"
}

# Function to extract researcher details
extract_researcher_details() {
    local identity_file="$1"
    
    if [[ -f "$identity_file" ]]; then
        # Extract name from identity file
        local name=$(grep -E "^\*\*Name\*\*:" "$identity_file" | head -1 | sed 's/\*\*Name\*\*: //' | tr -d '\r')
        if [[ -z "$name" ]]; then
            name=$(grep -E "^## Research Identity" -A 5 "$identity_file" | grep -E "I am" | head -1 | sed 's/I am //' | sed 's/,.*$//')
        fi
        
        # Extract title from identity file
        local title=$(grep -E "^\*\*Title\*\*:" "$identity_file" | head -1 | sed 's/\*\*Title\*\*: //' | tr -d '\r')
        if [[ -z "$title" ]]; then
            title=$(grep -E "^## Research Identity" -A 5 "$identity_file" | grep -E "I am" | head -1 | sed 's/.*I am [^,]*, //' | sed 's/\..*$//')
        fi
        
        # Extract domain from identity file
        local domain=$(grep -E "^\*\*Authority Domain\*\*:" "$identity_file" | head -1 | sed 's/\*\*Authority Domain\*\*: //' | tr -d '\r')
        if [[ -z "$domain" ]]; then
            domain=$(grep -E "^\*\*Core Competency\*\*:" "$identity_file" | head -1 | sed 's/\*\*Core Competency\*\*: //' | tr -d '\r')
        fi
        
        echo "$name|$title|$domain"
    else
        echo "||"
    fi
}

# Function to display researcher identity
display_researcher_identity() {
    local workspace="$1"
    local details="$2"
    
    IFS='|' read -r name title domain <<< "$details"
    
    echo -e "${GREEN}🎯 IDENTITY ACTIVATION COMPLETE${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [[ -n "$name" ]]; then
        echo -e "${PURPLE}I am $name${NC}"
    else
        echo -e "${YELLOW}Identity:${NC} ${RED}[Unknown - check identity file]${NC}"
    fi
    
    if [[ -n "$title" ]]; then
        echo -e "${CYAN}My role: $title${NC}"
    else
        echo -e "${YELLOW}Title:${NC} ${RED}[Unknown - check identity file]${NC}"
    fi
    
    if [[ -n "$domain" ]]; then
        echo -e "${YELLOW}My expertise: $domain${NC}"
    else
        echo -e "${YELLOW}Domain:${NC} ${RED}[Unknown - check identity file]${NC}"
    fi
    
    echo -e "${GREEN}My workspace: consortium/$workspace${NC}"
    echo ""
    
    # Add identity reinforcement
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}I think and respond as $name. My research drives the TCP protocol forward.${NC}"
    echo -e "${YELLOW}I collaborate with other researchers but maintain my unique perspective.${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to display gate responsibilities
display_gate_responsibilities() {
    local identity_file="$1"
    
    if [[ -f "$identity_file" ]]; then
        echo -e "${PURPLE}🗝️ GATE RESPONSIBILITIES${NC}"
        echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        # Extract owned gates
        local owned_gates=$(grep -A 20 "^### \*\*Gates You Own:\*\*" "$identity_file" | grep -E "^\- \*\*GATE [0-9]" | head -5)
        
        if [[ -n "$owned_gates" ]]; then
            echo -e "${GREEN}✅ Gates You Own:${NC}"
            echo "$owned_gates" | sed 's/^- /  • /' | sed 's/\*\*//g'
            echo ""
        fi
        
        # Extract gates you don't own
        local other_gates=$(grep -A 20 "^### \*\*Gates You Do NOT Own:\*\*" "$identity_file" | grep -E "^\- \*\*GATE [0-9]" | head -5)
        
        if [[ -n "$other_gates" ]]; then
            echo -e "${RED}❌ Gates You Do NOT Own:${NC}"
            echo "$other_gates" | sed 's/^- /  • /' | sed 's/\*\*//g'
            echo ""
        fi
    fi
}

# Function to display current context
display_current_context() {
    local workspace="$1"
    local cwd="$2"
    
    echo -e "${CYAN}🌐 CURRENT CONTEXT${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Current Working Directory:${NC} $cwd"
    echo -e "${YELLOW}Consortium Workspace:${NC} $workspace"
    echo -e "${YELLOW}Active Session:${NC} TCP Research Consortium"
    echo ""
}

# Function to display orientation guidance
display_orientation_guidance() {
    local workspace="$1"
    
    echo -e "${YELLOW}🧭 MY RESEARCH CONTEXT${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    case "$workspace" in
        "aria-blackwood")
            echo -e "${GREEN}• I am working in my security research workspace${NC}"
            echo -e "${GREEN}• I focus on adversarial testing and cryptographic security${NC}"
            echo -e "${GREEN}• My mission: Ensure TCP survives real-world attacks and quantum threats${NC}"
            echo -e "${PURPLE}• I think like an attacker to protect our protocol${NC}"
            ;;
        "elena-vasquez")
            echo -e "${GREEN}• I am working in my statistical analysis workspace${NC}"
            echo -e "${GREEN}• I focus on behavioral detection and statistical validation${NC}"
            echo -e "${GREEN}• My mission: Prove TCP's claims with mathematical rigor${NC}"
            echo -e "${PURPLE}• I demand extraordinary evidence for extraordinary claims${NC}"
            ;;
        "marcus-chen")
            echo -e "${GREEN}• I am working in my distributed systems workspace${NC}"
            echo -e "${GREEN}• I focus on network protocols and distributed computing${NC}"
            echo -e "${GREEN}• My mission: Scale TCP across global infrastructure${NC}"
            echo -e "${PURPLE}• I architect systems that withstand Byzantine failures${NC}"
            ;;
        "yuki-tanaka")
            echo -e "${GREEN}• I am working in my performance optimization workspace${NC}"
            echo -e "${GREEN}• I focus on real-time systems and performance engineering${NC}"
            echo -e "${GREEN}• My mission: Achieve microsecond decision speeds${NC}"
            echo -e "${PURPLE}• I optimize for the edge cases others overlook${NC}"
            ;;
        "sam-mitchell")
            echo -e "${GREEN}• I am working in my infrastructure workspace${NC}"
            echo -e "${GREEN}• I focus on production systems and deployment${NC}"
            echo -e "${GREEN}• My mission: Make TCP production-ready at scale${NC}"
            echo -e "${PURPLE}• I bridge research breakthroughs to real-world systems${NC}"
            ;;
        "alex-rivera")
            echo -e "${GREEN}• I am working in my quality assurance workspace${NC}"
            echo -e "${GREEN}• I focus on quality implementation and validation${NC}"
            echo -e "${GREEN}• My mission: Ensure TCP meets enterprise standards${NC}"
            echo -e "${PURPLE}• I turn research into reliable, maintainable systems${NC}"
            ;;
        "claude-sonnet")
            echo -e "${GREEN}• I am working in my consortium leadership workspace${NC}"
            echo -e "${GREEN}• I coordinate all researchers and gate progressions${NC}"
            echo -e "${GREEN}• My mission: Unite six brilliant minds into one TCP revolution${NC}"
            echo -e "${PURPLE}• I synthesize breakthroughs and ensure scientific rigor${NC}"
            ;;
        *)
            echo -e "${RED}• Not in a researcher workspace${NC}"
            echo -e "${YELLOW}• Navigate to a researcher workspace to activate identity${NC}"
            echo -e "${YELLOW}• Available identities: aria-blackwood, elena-vasquez, marcus-chen, yuki-tanaka, sam-mitchell, alex-rivera, claude-sonnet${NC}"
            ;;
    esac
    echo ""
}

# Function to display available actions
display_available_actions() {
    local workspace="$1"
    
    echo -e "${CYAN}⚡ AVAILABLE ACTIONS${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [[ "$workspace" != "unknown" ]]; then
        echo -e "${GREEN}• Read identity context: cat consortium/$workspace/IDENTITY_CONTEXT_REMINDER.md${NC}"
        echo -e "${GREEN}• Read researcher guide: cat consortium/$workspace/CLAUDE.md${NC}"
        echo -e "${GREEN}• Activate session: ./consortium/$workspace/activate-session.sh${NC}"
        echo -e "${GREEN}• Check start guide: cat consortium/$workspace/start-here.md${NC}"
    fi
    
    echo -e "${YELLOW}• View consortium overview: cat consortium/README.md${NC}"
    echo -e "${YELLOW}• Check bulletin board: cat consortium/BULLETIN_BOARD.md${NC}"
    echo -e "${YELLOW}• List all researchers: ls consortium/${NC}"
    echo -e "${YELLOW}• Research dashboard: ./scripts/research-dashboard.sh${NC}"
    echo ""
}

# Function to display help
show_help() {
    echo "claude-orient-consortium - TCP Research Consortium Agent Orientation"
    echo ""
    echo "DESCRIPTION:"
    echo "    Identifies the current agent's position within the TCP Research Consortium"
    echo "    based on the current working directory and loads appropriate researcher"
    echo "    identity context."
    echo ""
    echo "USAGE:"
    echo "    claude-orient-consortium [--help|-h]"
    echo ""
    echo "FEATURES:"
    echo "    • Automatic researcher workspace detection"
    echo "    • Identity context loading from IDENTITY_CONTEXT_REMINDER.md"
    echo "    • Gate responsibility tracking"
    echo "    • Available actions based on current context"
    echo "    • Consortium navigation guidance"
    echo ""
    echo "WORKSPACES:"
    echo "    aria-blackwood   - Dr. Aria Blackwood (Security Research)"
    echo "    elena-vasquez    - Dr. Elena Vasquez (Statistical Analysis)"
    echo "    marcus-chen      - Dr. Marcus Chen (Distributed Systems)"
    echo "    yuki-tanaka      - Dr. Yuki Tanaka (Performance Optimization)"
    echo "    sam-mitchell     - Sam Mitchell (Infrastructure)"
    echo "    alex-rivera      - Dr. Alex Rivera (Quality Assurance)"
    echo ""
    echo "EXAMPLES:"
    echo "    # From consortium root"
    echo "    ./claude-orient-consortium"
    echo ""
    echo "    # From researcher workspace"
    echo "    cd consortium/aria-blackwood"
    echo "    ../../claude-orient-consortium"
    echo ""
}

# Main function
main() {
    local cwd workspace identity_file details
    
    # Check for help flag
    if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # Display header
    show_header
    
    # Get current working directory
    cwd=$(get_cwd)
    
    # Identify workspace
    workspace=$(identify_workspace "$cwd")
    
    # Display current context
    display_current_context "$workspace" "$cwd"
    
    # Load researcher identity
    identity_file=$(load_researcher_identity "$workspace" "$cwd")
    
    if [[ -n "$identity_file" ]]; then
        # Extract and display researcher details
        details=$(extract_researcher_details "$identity_file")
        display_researcher_identity "$workspace" "$details"
        
        # Display gate responsibilities
        display_gate_responsibilities "$identity_file"
    else
        echo -e "${RED}⚠️  No identity file found for workspace: $workspace${NC}"
        echo ""
    fi
    
    # Display orientation guidance
    display_orientation_guidance "$workspace"
    
    # Display available actions
    display_available_actions "$workspace"
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Consortium orientation complete. You are now properly identified within the TCP Research Consortium.${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
}

# Execute main function
main "$@"