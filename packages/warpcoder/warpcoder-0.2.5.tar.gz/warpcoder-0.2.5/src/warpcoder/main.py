#!/usr/bin/env python3
"""
WarpClaude - Universal BDD Project Generator for Claude Code
Automatically sets up Claude Code environment and manages BDD development lifecycle
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
import platform
import time

# Try to import optional packages
try:
    import questionary
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Embedded command content
BDDINIT_CONTENT = '''**BDD INITIALIZATION COMMAND**
Usage: /project:bddinit "your app goal"

Initialize a BDD project in the current directory with domain models, state diagrams, and feature files.

**ARGUMENT:**
Parse the app goal from "$ARGUMENTS" - a single string describing what to build.

**TECH STACK DETECTION:**
Analyze the app_goal to detect the appropriate tech stack:
- If mentions "fastapi", "flask", "django" → use python stack
- If mentions "express", "node", "react" → use node stack  
- If mentions "rails", "ruby" → use ruby stack
- Default: python-fastapi

**PHASE 1: ENVIRONMENT SETUP**

Work in the current directory and create:
- features/ directory
- features/steps/ directory  
- docs/ directory for documentation
- pseudocode/ directory for architecture planning

Based on tech_stack, set up the appropriate BDD framework:

**Python Stack:**
- Check if behave is installed: `pip show behave`
- For Django projects: Install behave-django
- For Flask/FastAPI: Install behave
- Create features/environment.py with basic configuration

**Node.js Stack:**
- Check if cucumber is installed: `npm list cucumber`
- Install @cucumber/cucumber if needed
- Create cucumber.js configuration file

**Ruby Stack:**
- Check if cucumber is installed: `gem list cucumber`
- Install cucumber gem if needed
- Create cucumber.yml configuration

**PHASE 2: GOAL ANALYSIS & APP NAMING**

Analyze the app_goal to extract:
- Core domain entities
- Primary user actions
- Key business processes
- Success criteria

Generate an appropriate app name:
- Extract key concepts from the goal
- Create a memorable, descriptive name
- Ensure it's suitable for the domain

**PHASE 3: DOMAIN-DRIVEN DESIGN DOCUMENT**

Create `docs/ddd.md` with minimal, essential domain model:

```markdown
# Domain Model - [App Name]

## Bounded Context
[Single bounded context for this simple app]

## Aggregates
[List only essential aggregates - usually 1-3 for simple apps]

### [Aggregate Name]
- **Root Entity**: [Entity name]
- **Value Objects**: [List if any, keep minimal]
- **Business Rules**: [Core invariants only]

## Domain Events
[List 2-4 critical events that drive the system]

## Ubiquitous Language
[5-10 key terms max, with clear definitions]
```

Focus on:
- Only entities that directly serve the app goal
- Remove any "nice-to-have" concepts
- Keep relationships simple
- No technical implementation details

**PHASE 4: STATE DIAGRAM GENERATION**

Create `docs/state-diagram.md` with Mermaid stateDiagram:

```markdown
# State Flow - [App Name]

## Business State Diagram

\```mermaid
stateDiagram-v2
    [*] --> Initial
    Initial --> [Core State 1]
    [Core State 1] --> [Core State 2]: [Action]
    [Core State 2] --> [End State]: [Completion]
    [End State] --> [*]
\```

## State Definitions
- **Initial**: [What triggers the process]
- **[Core States]**: [What happens in each state]
- **[End State]**: [Success condition]

## Transitions
[List each transition with business rules]
```

Rules for state diagram:
- Maximum 5-7 states total
- Only happy path transitions
- No error states unless critical
- Clear start and end

**PHASE 5: MISSION DOCUMENT**

Create `docs/mission.md`:

```markdown
# Mission - [App Name]

## Vision
[Elaborate the one-sentence goal into 2-3 paragraphs]

## Success Criteria
1. [Specific, measurable outcome 1]
2. [Specific, measurable outcome 2]
3. [Specific, measurable outcome 3]

## In Scope
- [Core feature 1]
- [Core feature 2]
- [Core feature 3]

## Out of Scope
- [Explicitly excluded feature 1]
- [Explicitly excluded feature 2]
- [Future enhancement 1]

## App Name Rationale
**Chosen Name**: [App Name]
**Reasoning**: [Why this name fits the mission]
```

**PHASE 6: MINIMAL FEATURE FILES**

Create ultra-minimal feature files - first pass:

1. Identify all possible features
2. Reduce to happy paths only
3. Further reduce to critical path only

Final features should be:
- One core workflow feature
- Optional: One setup feature (only if required)
- Maximum 3-5 scenarios total across all features

Example `features/core_workflow.feature`:
```gherkin
Feature: [Core Workflow Name]
  As a [primary user]
  I want to [primary action]
  So that [primary value]

  Scenario: [Single Critical Path]
    Given [minimal precondition]
    When [essential action]
    Then [core success criteria]
```

**PHASE 7: 1990s PSEUDOCODE ARCHITECTURE**

Generate strict procedural pseudocode with:
- Clear BEGIN/END blocks
- Explicit variable declarations
- Simple procedural flow
- No patterns or abstractions

Structure:
```
pseudocode/
├── main_controller.pseudo
├── data_manager.pseudo
├── business_rules.pseudo
└── io_handler.pseudo
```

Example format:
```
PROGRAM MainController
BEGIN
    DECLARE userInput AS STRING
    DECLARE dataStore AS DataManager
    DECLARE result AS BOOLEAN
    
    FUNCTION ProcessRequest(input)
    BEGIN
        VALIDATE input
        IF input IS VALID THEN
            result = dataStore.Save(input)
            RETURN result
        ELSE
            RETURN FALSE
        END IF
    END
    
    // Main execution
    userInput = GetUserInput()
    result = ProcessRequest(userInput)
    DisplayResult(result)
END
```

**PHASE 8: ARCHITECTURE REVIEW & SIMPLIFICATION**

Review all pseudocode and ask:
1. Can any two modules be combined?
2. Is there any unnecessary indirection?
3. Could this be done with fewer files?
4. Would a beginner understand this immediately?

Simplify until the answer to #4 is absolutely YES.

**PHASE 9: SUMMARY GENERATION**

Create `summary.md`:

```markdown
# BDD Project Initialized - [App Name]

## Generated Structure
- ✅ BDD framework configured ([behave/cucumber])
- ✅ Domain model defined (docs/ddd.md)
- ✅ State flow mapped (docs/state-diagram.md)
- ✅ Mission clarified (docs/mission.md)
- ✅ Features created ([list feature files])
- ✅ Architecture planned ([list pseudocode files])

## Quick Start
1. Review the generated documents in docs/
2. Examine the features/ directory
3. Check pseudocode/ for the planned architecture

## Next Steps
Run the bddloop command to:
- Generate step definitions
- Implement the pseudocode as real code
- Make all tests pass

## Configuration
- Tech Stack: [chosen stack]
- BDD Framework: [behave/cucumber]
- App Goal: "[original goal]"
```

**EXECUTION PRINCIPLES:**

1. **Ruthless Simplification**: Always choose the simpler option
2. **No Gold Plating**: Only what directly serves the stated goal
3. **Clear Over Clever**: 1990s clarity beats modern patterns
4. **Test-First Thinking**: Everything prepared for BDD implementation
5. **Single Responsibility**: Each component does ONE thing

Begin by parsing arguments and systematically work through each phase, constantly asking "Can this be simpler?"'''

BDDWARP_CONTENT = '''**BDD WARP COMMAND**
Usage: /project:bddwarp

Execute a BDD-driven development loop with infinite iterations in the current directory.

**NO ARGUMENTS NEEDED** - Always runs infinite iterations in current directory.

**PHASE 1: INITIAL ASSESSMENT**

Verify BDD setup in current directory:
- Check for features/ directory with .feature files
- Verify features/steps/ directory exists
- Confirm behave (or cucumber) is installed
- Read docs/mission.md, ddd.md, and state-diagram.md for context
- Examine pseudocode/ for implementation guidance

**CRITICAL: Understand the Mission**
Read mission.md and identify:
- What is the ONE main purpose of this app?
- What is the critical path to achieve that purpose?
- Is this a web app (needs browser) or CLI app (needs menu)?
- What would make the user say "this works!"?

Run initial BDD test suite:
```bash
behave --format progress3 --no-capture
```

Capture and analyze:
- Which steps are undefined
- Which steps fail
- Overall test structure

**FAIL-FIRST PRINCIPLE:**
Remember: We WANT tests to fail initially. This is TDD:
- No mocks or stubs
- No "pass" statements
- Love exceptions and errors
- Each failure guides implementation

**PHASE 2: IMPLEMENTATION LOOP**

For iteration = 1 to iterations (or infinite):

**Step 1: Run Tests & Capture State**
```bash
behave --format progress3 --no-capture > test_output.txt
```
Parse output to identify:
- Undefined steps needing implementation
- Failing steps needing code
- Passing steps (victory markers)

**Step 2: Generate Step Definitions**
Deploy Sub Agent for undefined steps:
```
TASK: Generate step definitions for BDD tests

CONTEXT:
- Feature file: [content]
- Undefined steps: [list]
- Tech stack: [from bddinit]

REQUIREMENTS:
1. Create step definition files in features/steps/
2. Each step should RAISE NotImplementedError
3. Include proper behave decorators
4. Match step text exactly
5. Add TODO comments for implementation

DELIVERABLE: Step definition files that fail correctly
```

**Step 3: Implement Domain/Model Layer**
Deploy Sub Agent for data layer:
```
TASK: Implement database models and domain logic

CONTEXT:
- Domain model: [from ddd.md]
- Pseudocode: [from pseudocode/]
- Tech stack: [framework specific]

REQUIREMENTS:
1. Create database models/tables
2. Run migrations if needed (Django: migrate, etc)
3. Implement domain logic from DDD
4. Create test data fixtures
5. Verify database connectivity

DELIVERABLE: Working data layer with test data
```

**Step 4: Implement API Layer**
Deploy Sub Agent for API:
```
TASK: Implement API endpoints

CONTEXT:
- Pseudocode: [main_controller.pseudo]
- Routes needed: [from features]
- Models: [from previous step]

REQUIREMENTS:
1. Create all API endpoints
2. Connect to real database
3. Implement business logic
4. Generate API documentation
5. Test each endpoint manually

DELIVERABLE: Working API with documentation
```

**Step 5: Connect Frontend**
Deploy Sub Agent for UI:
```
TASK: Wire frontend to API

CONTEXT:
- Pseudocode: [web_interface.pseudo]
- API endpoints: [from previous step]
- UI framework: [JavaScript/etc]

REQUIREMENTS:
1. Replace any hardcoded data with API calls
2. Implement real fetch/ajax requests
3. Handle loading states
4. Display real data from backend
5. Ensure error handling

DELIVERABLE: Frontend connected to live API
```

**Step 6: Create User Entry Point**
Deploy Sub Agent for user experience:
```
TASK: Create single-file entry point for users

CONTEXT:
- Mission goal: [from mission.md]
- App type: [web or CLI]
- Tech stack: [from setup]

REQUIREMENTS FOR WEB APPS:
1. Create play.py (or start.py) that:
   - Finds available ports automatically
   - Starts backend API server
   - Serves frontend (if separate)
   - Opens browser to the GAME/APP (not API docs!)
   - Shows "Starting [App Name]..." message
2. Handle Ctrl+C gracefully to stop all services

REQUIREMENTS FOR CLI APPS:
1. Create menu.py using Rich/Textual/Blessed that:
   - Shows beautiful welcome screen
   - Provides numbered menu options
   - Has "1. Quick Start" as first option (no params)
   - Includes help and exit options
   - Uses colors and boxes for visual appeal
2. Make the critical path obvious and immediate

DELIVERABLE: One file that starts everything
```

**Step 7: Integration Testing**
Run full stack test:
```bash
# Use the new entry point
python play.py &  # or menu.py for CLI
APP_PID=$!

# Wait for startup
sleep 3

# Run integration tests
behave --tags=@integration

# Kill app
kill $APP_PID
```

**Step 8: Reality Checks**
Deploy Sub Agent for verification:
```
TASK: Perform user-focused reality verification

REQUIREMENTS:
1. Run the entry point file (play.py/menu.py)
2. Verify it opens to the MAIN PURPOSE immediately
3. For web: Ensure browser opens to game/app (NOT api docs)
4. For CLI: Ensure menu is beautiful and clear
5. Test the critical path as a real user would
6. Verify NO technical barriers between user and goal
7. Check that mission.md goal is achievable in <3 clicks/actions

DELIVERABLE: Reality check report proving user success
```

Deploy Screenshot Sub Agent:
```
TASK: Capture screenshots of running application

CONTEXT:
- App type: [web or CLI]
- Entry point: [play.py or menu.py]

REQUIREMENTS:
1. Create screenshots/ directory
2. For web apps:
   - Use selenium/playwright headless browser
   - Capture: landing page, main interaction, success state
3. For CLI apps:
   - Capture terminal output as images using available tools
   - Alternative: Save text output to screenshots/cli_output.txt
4. Name files descriptively: 01_landing.png, 02_game_in_progress.png, etc.
5. Include a screenshots/README.md explaining what each image shows

DELIVERABLE: screenshots/ folder with captured images and documentation
```

**Step 9: Test Data Verification**
Create and test with realistic data:
- Generate test_data.json with realistic examples
- Create unit tests for data transformations
- Verify edge cases in data flow
- Test validation at each layer

**Step 10: Documentation & README**
Create user-friendly README.md:
```markdown
# [App Name]

[One sentence description from mission.md]

## Quick Start

```bash
python play.py
```

That's it! The game/app will start automatically.

## What This Does
[2-3 sentences about the main purpose]

## Requirements
- Python 3.x
- [Any other requirements]
```

Verify documentation:
- README focuses on USER not developer
- First command is the entry point
- No complex setup instructions
- API docs exist but are secondary

**PHASE 3: LOGGING & EVOLUTION**

**Update droid_log.md:**
```markdown
# Droid Log - Iteration [N]

## Patterns Observed
- [Pattern]: [Description]
- [Challenge]: [How resolved]

## Wild Successes
- [Success]: [What worked well]

## Common Issues
- [Issue]: [Root cause and fix]

## Screenshot Status
- Screenshots captured: [Yes/No]
- Location: screenshots/
- Issues encountered: [Any screenshot setup problems]
```

**Update prompt_evolution.md:**
```markdown
# Prompt Evolution - Iteration [N]

## Improvements for Next Time
- Instead of: "[current approach]"
- Try: "[better approach]"

## Effective Patterns
- "[pattern]" works well for [situation]

## Self-Notes
- [Advice for next iteration]
```

**Step 11: Apply Self-Improvements**
Read prompt_evolution.md and immediately apply suggestions:
- Adjust prompts based on learnings
- Modify approach based on patterns
- Implement suggested improvements
- Focus on user experience improvements

**PHASE 4: LOOP CONTROL**

After each iteration:
1. Check if all tests are passing
2. If yes and iterations != infinite: Complete
3. If no and iterations remaining: Continue
4. If infinite: Continue until context limits

**Progress Tracking:**
```
Iteration [N] of [Total]
- Tests Passing: X/Y
- Coverage: Z%
- Integration: [Status]
```

**PHASE 5: FINAL VERIFICATION**

When all tests pass:
1. Run full test suite one final time
2. Start application and verify manually
3. Document any remaining issues
4. Create summary report

**SUCCESS CRITERIA:**
- All behave tests passing
- Single entry point (play.py/menu.py) works perfectly
- User reaches main goal in <3 actions
- For web: Browser opens to game/app directly
- For CLI: Beautiful menu with quick start
- No technical barriers for users
- README has one simple command to start
- Mission.md goal is immediately achievable

**EXECUTION PRINCIPLES:**

1. **Test-Driven**: Let failing tests drive development
2. **Real Implementation**: No mocks, actual code
3. **Full Stack**: Verify every layer
4. **Continuous Feedback**: Behave is the truth
5. **Self-Improving**: Learn and adapt each iteration
6. **Reality-Based**: Screenshots and manual verification
7. **Data-Centric**: Test actual data flow
8. **Documentation-Aware**: Keep all docs in sync
9. **USER-FIRST**: Always think "How does the user start this?"
10. **CRITICAL PATH**: Focus on mission.md goal above all else

Begin with initial test run and proceed through iterations until success!'''

def print_console(message, style=""):
    """Print with rich console if available, otherwise plain print"""
    if console and RICH_AVAILABLE:
        console.print(message, style=style)
    else:
        print(message)

def print_panel(title, content):
    """Print a panel with rich if available"""
    if console and RICH_AVAILABLE:
        console.print(Panel(content, title=title))
    else:
        print(f"\n=== {title} ===")
        print(content)
        print("=" * (len(title) + 8))

def check_command(command, timeout=None):
    """Check if a command exists and return version or status"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout.strip() or "Installed"
        return None
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None

def is_claude_installed():
    """Quick check if Claude Code is accessible in PATH"""
    # Try fast version check first
    version = check_command(["claude", "--version"], timeout=2)
    if version:
        return True
    
    # Check common npm global bin locations
    npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
    if npm_prefix:
        npm_bin = Path(npm_prefix.strip()) / "bin" / "claude"
        if npm_bin.exists():
            # Claude is installed but not in PATH
            return "installed_not_in_path"
    
    return False

def check_python_package(package):
    """Check if a Python package is installed"""
    try:
        __import__(package)
        return "Installed"
    except ImportError:
        return None

def get_shell_config():
    """Get appropriate shell config file"""
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        if (home / ".zshrc").exists():
            return home / ".zshrc"
        return home / ".bash_profile"
    elif system == "Linux":
        return home / ".bashrc"
    elif system == "Windows":
        return None
    
def install_nvm_and_node():
    """Install nvm and Node.js"""
    if platform.system() == "Windows":
        print_console("⚠️  Windows detected. Please install Node.js from nodejs.org", style="yellow")
        print_console("Then install Claude Code with: npm install -g @anthropic-ai/claude-code")
        return False
    
    print_console("📦 Installing nvm (Node Version Manager)...")
    
    # Install nvm
    nvm_install_cmd = 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash'
    result = subprocess.run(nvm_install_cmd, shell=True)
    
    if result.returncode != 0:
        print_console("❌ Failed to install nvm", style="red")
        return False
    
    # Source nvm
    shell_config = get_shell_config()
    if shell_config:
        subprocess.run(f'source {shell_config}', shell=True)
    
    # Install node using nvm
    print_console("📦 Installing Node.js...")
    # We need to run this in a new shell that has nvm loaded
    install_node_cmd = f'source {shell_config} && nvm install node'
    result = subprocess.run(install_node_cmd, shell=True, executable='/bin/bash')
    
    if result.returncode == 0:
        print_console("✅ Node.js installed successfully", style="green")
        return True
    else:
        print_console("❌ Failed to install Node.js", style="red")
        return False

def check_and_install_claude():
    """Ensure Claude Code is installed and working"""
    print_console("🔍 Checking Claude Code installation...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        venv_path = sys.prefix
        print_console(f"📦 Virtual environment detected: {venv_path}", style="cyan")
    
    # Quick check first
    claude_status = is_claude_installed()
    if claude_status == True:
        print_console("✅ Claude Code is installed and accessible", style="green")
        return True
    elif claude_status == "installed_not_in_path":
        print_console("⚠️  Claude Code is installed but not in PATH", style="yellow")
        npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
        if npm_prefix:
            print_console(f"💡 Add this to your PATH: {npm_prefix.strip()}/bin", style="cyan")
            print_console("   Then restart your terminal", style="dim")
        return False
    
    # Not installed, continue with installation
    print_console("❌ Claude Code not found.", style="yellow")
    
    # Check if npm exists
    try:
        print_console("🔍 Checking for npm...", style="dim")
        npm_check = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
        if npm_check.returncode != 0:
            raise FileNotFoundError
        print_console(f"✅ npm found: v{npm_check.stdout.strip()}", style="green")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_console("❌ npm not found.", style="red")
        
        if in_venv:
            print_console("\n⚠️  WARNING: You're in a virtual environment!", style="yellow bold")
            print_console("Claude Code needs to be installed globally with npm.", style="yellow")
            print_console("Options:", style="cyan")
            print_console("1. Exit venv and run: pip install warpcoder && warp", style="white")
            print_console("2. Or manually install: npm install -g @anthropic-ai/claude-code", style="white")
            print_console("\nPress Ctrl+C to exit and handle this manually.", style="yellow")
            try:
                input("\nPress Enter to continue anyway (not recommended)...")
            except KeyboardInterrupt:
                print_console("\n👋 Exiting. Please install Claude Code globally.", style="cyan")
                sys.exit(0)
        
        print_console("📦 Installing Node.js...", style="yellow")
        if not install_nvm_and_node():
            return False
        # After installing node, we need to reload the shell environment
        print_console("⚠️  Please run this script again in a new terminal to continue", style="yellow")
        sys.exit(0)
    
    # Install Claude Code
    print_console("📦 Installing Claude Code globally with npm...", style="cyan")
    print_console("⏳ This may take a minute...", style="dim")
    
    # Show the command being run
    install_cmd = ["npm", "install", "-g", "@anthropic-ai/claude-code"]
    print_console(f"🏃 Running: {' '.join(install_cmd)}", style="dim")
    
    # Run with real-time output
    already_installed = False
    try:
        process = subprocess.Popen(
            install_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
            # Detect if already installed
            if "changed" in line and "added" in line:
                if "changed" in line.split("added")[0]:
                    already_installed = True
        
        process.wait()
        result_code = process.returncode
    except Exception as e:
        print_console(f"❌ Error during installation: {e}", style="red")
        result_code = 1
    
    if result_code == 0:
        if already_installed:
            print_console("✅ Claude Code was already installed (updated)", style="green")
        else:
            print_console("✅ npm install completed", style="green")
        
        # Quick verify with version check instead of doctor
        print_console("🔍 Verifying Claude Code installation...", style="dim")
        claude_check = is_claude_installed()
        if claude_check == True:
            print_console("✅ Claude Code installed successfully!", style="green")
            return True
        elif claude_check == "installed_not_in_path":
            print_console("⚠️  Claude Code installed but not in PATH", style="yellow")
            npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
            if npm_prefix:
                print_console(f"\n💡 To fix this, add npm's bin directory to your PATH:", style="yellow")
                print_console(f"   export PATH=\"{npm_prefix.strip()}/bin:$PATH\"", style="cyan")
                print_console("   Then restart your terminal or run:", style="dim")
                print_console(f"   source ~/.zshrc  # or ~/.bashrc", style="cyan")
            return False
    
    print_console("❌ Failed to install Claude Code", style="red")
    print_console("Please install manually: npm install -g @anthropic-ai/claude-code")
    return False

def setup_context7():
    """Install and configure Context7 MCP server"""
    return install_mcp_server(
        "context7",
        ["context7", "--", "npx", "-y", "@upstash/context7-mcp@latest"],
        "Context7 MCP (Enhanced memory)"
    )

def install_mcp_server(server_name, command_args, description):
    """Generic function to install an MCP server"""
    print_console(f"\n🔧 Installing {description}...", style="cyan")
    
    if not is_claude_installed():
        print_console(f"⚠️  Claude Code not found. Skipping {server_name} setup.", style="yellow")
        return False
    
    try:
        # Build the full command
        cmd = ["claude", "mcp", "add"] + command_args
        
        print_console(f"🏃 Running: claude mcp add {' '.join(command_args[:3])}...", style="dim")
        
        # Run with timeout
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        timeout_seconds = 60
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout_seconds:
                process.terminate()
                print_console(f"\n⏱️  {server_name} setup timed out after 60 seconds", style="yellow")
                return False
                
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
                
            if line:
                line = line.rstrip()
                if line:
                    print_console(f"   {line}", style="dim")
        
        return_code = process.poll()
        
        if return_code == 0:
            print_console(f"✅ {description} configured successfully!", style="green")
            return True
        else:
            print_console(f"⚠️  Could not configure {server_name} automatically", style="yellow")
            return False
    except Exception as e:
        print_console(f"⚠️  Error setting up {server_name}: {e}", style="yellow")
        return False

def setup_all_mcp_servers():
    """Install all recommended MCP servers"""
    print_console("\n🚀 Setting up MCP servers for enhanced Claude capabilities...", style="cyan bold")
    
    servers = [
        {
            "name": "context7",
            "args": ["context7", "--", "npx", "-y", "@upstash/context7-mcp@latest"],
            "description": "Context7 MCP (Enhanced memory)"
        },
        {
            "name": "puppeteer",
            "args": ["puppeteer", "--", "npx", "-y", "@modelcontextprotocol/server-puppeteer"],
            "description": "Puppeteer MCP (Browser automation)"
        },
        {
            "name": "magic",
            "args": ["magic", "--", "npx", "-y", "@modelcontextprotocol/server-magic"],
            "description": "Magic MCP (AI-powered utilities)"
        },
        {
            "name": "sequence-mcp",
            "args": ["--transport", "http", "sequence-mcp", "npx", "-y", "@modelcontextprotocol/server-sequence"],
            "description": "Sequence MCP (Sequential operations)"
        }
    ]
    
    success_count = 0
    for server in servers:
        if install_mcp_server(server["name"], server["args"], server["description"]):
            success_count += 1
        time.sleep(1)  # Brief pause between installations
    
    print_console(f"\n📊 MCP Server Installation Summary:", style="cyan bold")
    print_console(f"   Successfully installed: {success_count}/{len(servers)} servers", style="green" if success_count == len(servers) else "yellow")
    
    if success_count < len(servers):
        print_console("\n💡 To manually install missing servers:", style="yellow")
        print_console("   Context7: claude mcp add context7 -- npx -y @upstash/context7-mcp@latest", style="dim")
        print_console("   Puppeteer: claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer", style="dim")
        print_console("   Magic: claude mcp add magic -- npx -y @modelcontextprotocol/server-magic", style="dim")
        print_console("   Sequence: claude mcp add --transport http sequence-mcp npx -y @modelcontextprotocol/server-sequence", style="dim")
    
    return success_count == len(servers)

def setup_claude_environment():
    """Creates .claude directory structure if not exists"""
    print_console("📁 Setting up Claude environment...", style="cyan")
    
    claude_dir = Path(".claude")
    commands_dir = claude_dir / "commands"
    
    # Create directories
    print_console("📂 Creating .claude/commands directory...", style="dim")
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Write bddinit.md
    print_console("📝 Writing bddinit command...", style="dim")
    (commands_dir / "bddinit.md").write_text(BDDINIT_CONTENT)
    
    # Write bddwarp.md
    print_console("📝 Writing bddwarp command...", style="dim")
    (commands_dir / "bddwarp.md").write_text(BDDWARP_CONTENT)
    
    # Write settings.json
    print_console("⚙️  Creating settings.json...", style="dim")
    settings = {
        "commands": {
            "enabled": True,
            "directories": ["~/.claude/commands", ".claude/commands"]
        }
    }
    (claude_dir / "settings.json").write_text(json.dumps(settings, indent=2))
    
    # Write comprehensive settings.local.json for BDD development
    print_console("🔓 Creating permissive settings.local.json for BDD development...", style="dim")
    local_settings = {
        "permissions": {
            "allow": [
                # Directory operations
                "Bash(mkdir:*)",
                "Bash(cd:*)",
                "Bash(pwd:*)",
                "Bash(ls:*)",
                "Bash(find:*)",
                "Bash(tree:*)",
                
                # File operations
                "Bash(touch:*)",
                "Bash(cp:*)",
                "Bash(mv:*)",
                "Bash(rm:*)",
                "Bash(cat:*)",
                "Bash(echo:*)",
                "Bash(grep:*)",
                "Bash(sed:*)",
                "Bash(awk:*)",
                
                # Python operations
                "Bash(python:*)",
                "Bash(python3:*)",
                "Bash(pip:*)",
                "Bash(pip3:*)",
                "Bash(behave:*)",
                "Bash(pytest:*)",
                
                # Node/npm operations
                "Bash(node:*)",
                "Bash(npm:*)",
                "Bash(npx:*)",
                "Bash(cucumber:*)",
                
                # Ruby operations
                "Bash(ruby:*)",
                "Bash(gem:*)",
                "Bash(bundle:*)",
                "Bash(rake:*)",
                
                # Git operations
                "Git(*)",
                
                # Build/run operations
                "Bash(make:*)",
                "Bash(./play.py:*)",
                "Bash(./menu.py:*)",
                "Bash(./start.py:*)",
                "Bash(./run.py:*)",
                
                # Django/Flask/FastAPI
                "Bash(django-admin:*)",
                "Bash(manage.py:*)",
                "Bash(flask:*)",
                "Bash(uvicorn:*)",
                "Bash(gunicorn:*)",
                
                # Database operations
                "Bash(psql:*)",
                "Bash(mysql:*)",
                "Bash(sqlite3:*)",
                "Bash(redis-cli:*)",
                
                # Testing tools
                "Bash(coverage:*)",
                "Bash(tox:*)",
                "Bash(black:*)",
                "Bash(ruff:*)",
                "Bash(eslint:*)",
                "Bash(prettier:*)",
                
                # Docker (if needed)
                "Bash(docker:*)",
                "Bash(docker-compose:*)",
                
                # Other useful commands
                "Bash(curl:*)",
                "Bash(wget:*)",
                "Bash(which:*)",
                "Bash(whereis:*)",
                "Bash(ps:*)",
                "Bash(kill:*)",
                "Bash(pkill:*)",
                "Bash(lsof:*)",
                "Bash(netstat:*)",
                "Bash(ss:*)",
                "Bash(export:*)",
                "Bash(source:*)",
                "Bash(.:*)",
                
                # Text editors (for quick edits)
                "Bash(nano:*)",
                "Bash(vim:*)",
                "Bash(vi:*)",
                
                # Catch-all for common operations
                "Cd(*)",
                "Mkdir(*)"
            ],
            "deny": []
        }
    }
    (claude_dir / "settings.local.json").write_text(json.dumps(local_settings, indent=2))
    
    print_console("✅ Claude environment created (.claude/commands/)", style="green")
    
    # Print MCP setup instructions
    print_console("\n💡 To enhance Claude with MCP servers:", style="yellow")
    print_console("   Use menu option 7 to install all recommended servers", style="cyan")
    print_console("   Or install individually:", style="dim")
    print_console("   • Context7: claude mcp add context7 -- npx -y @upstash/context7-mcp@latest", style="dim")
    print_console("   • Puppeteer: claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer", style="dim")
    print_console("   • Magic: claude mcp add magic -- npx -y @modelcontextprotocol/server-magic", style="dim")
    print_console("   • Sequence: claude mcp add --transport http sequence-mcp npx -y @modelcontextprotocol/server-sequence", style="dim")

def detect_tech_stack(app_goal):
    """Detect appropriate tech stack from the app goal description"""
    goal_lower = app_goal.lower()
    
    # Python frameworks
    if any(word in goal_lower for word in ["fastapi", "fast api", "fast-api"]):
        return "python-fastapi"
    elif "django" in goal_lower:
        return "python-django"
    elif "flask" in goal_lower:
        return "python-flask"
    elif "python" in goal_lower:
        return "python-fastapi"  # Default Python stack
    
    # JavaScript/Node frameworks
    elif any(word in goal_lower for word in ["express", "nodejs", "node.js", "node"]):
        return "node-express"
    elif any(word in goal_lower for word in ["react", "nextjs", "next.js"]):
        return "node-react"
    elif any(word in goal_lower for word in ["vue", "vuejs", "vue.js"]):
        return "node-vue"
    elif "javascript" in goal_lower or "js" in goal_lower:
        return "node-express"  # Default Node stack
    
    # Ruby frameworks
    elif any(word in goal_lower for word in ["rails", "ruby on rails", "ror"]):
        return "ruby-rails"
    elif "ruby" in goal_lower:
        return "ruby-rails"
    
    # Other languages/frameworks
    elif any(word in goal_lower for word in ["rust", "actix", "rocket"]):
        return "rust"
    elif any(word in goal_lower for word in ["go", "golang", "gin", "echo"]):
        return "go"
    elif any(word in goal_lower for word in ["java", "spring", "springboot"]):
        return "java-spring"
    elif any(word in goal_lower for word in ["c#", "csharp", ".net", "aspnet"]):
        return "dotnet"
    
    # Default fallback
    else:
        return "python-fastapi"

def detect_bdd_project():
    """Returns True if features/ folder exists AND contains .feature files"""
    features_dir = Path("features")
    if features_dir.exists() and features_dir.is_dir():
        feature_files = list(features_dir.glob("*.feature"))
        return len(feature_files) > 0
    return False

def find_entry_points():
    """Find play.py, menu.py, start.py, run.py in current directory"""
    patterns = ["play.py", "menu.py", "start.py", "run.py"]
    found = []
    for pattern in patterns:
        if Path(pattern).exists():
            found.append(pattern)
    return found

def find_latest_app_directory():
    """Find the most recently created directory with features/ inside"""
    dirs_with_features = []
    for item in Path(".").iterdir():
        if item.is_dir() and (item / "features").exists():
            dirs_with_features.append(item)
    
    if dirs_with_features:
        # Return the most recently modified
        return max(dirs_with_features, key=lambda d: d.stat().st_mtime).name
    return "."

def run_bddinit(app_goal):
    """Run bddinit with the given app goal"""
    print_console("🚀 Starting BDD initialization...", style="cyan")
    print_console(f"📝 Goal: {app_goal}", style="dim")
    
    # Detect and display tech stack
    tech_stack = detect_tech_stack(app_goal)
    print_console(f"🔧 Detected tech stack: {tech_stack}", style="dim")
    print_console("", style="")
    
    try:
        print_console("🏃 Launching Claude Code with bddinit command...", style="dim")
        subprocess.run(["claude", f"/project:bddinit {app_goal}"])
    except FileNotFoundError:
        print_console("❌ Claude Code not found. Please ensure it's installed.", style="red")
        print_console("💡 Try running: npm install -g @anthropic-ai/claude-code", style="yellow")
        sys.exit(1)
    except KeyboardInterrupt:
        print_console("\n👋 Cancelled by user", style="yellow")
        sys.exit(0)

def run_bddwarp():
    """Run bddwarp with infinite iterations in current directory"""
    print_console(f"🔄 Starting BDD development loop...", style="cyan")
    print_console("📁 Working in: current directory", style="dim")
    print_console("🔢 Iterations: infinite", style="dim")
    print_console("📋 This will:", style="dim")
    print_console("   1. Run BDD tests", style="dim")
    print_console("   2. Generate step definitions", style="dim")
    print_console("   3. Implement code to pass tests", style="dim")
    print_console("   4. Create entry points (play.py/menu.py)", style="dim")
    print_console("", style="")
    
    try:
        print_console("🏃 Launching Claude Code with bddwarp command...", style="dim")
        subprocess.run(["claude", "/project:bddwarp"])
    except FileNotFoundError:
        print_console("❌ Claude Code not found. Please ensure it's installed.", style="red")
        print_console("💡 Try running: npm install -g @anthropic-ai/claude-code", style="yellow")
        sys.exit(1)
    except KeyboardInterrupt:
        print_console("\n👋 Cancelled by user", style="yellow")
        sys.exit(0)

def handle_with_goal(app_goal):
    """Handle warpcoder when given a goal directly"""
    # Setup claude environment first
    setup_claude_environment()
    
    # If BDD project already exists, just mention it and continue
    if detect_bdd_project():
        print_console("✓ BDD project already exists. Re-initializing with new goal...", style="yellow")
    
    # Run bddinit with the goal
    run_bddinit(app_goal)
    
    # Wait a moment for bddinit to complete
    print_console("\n⏳ Waiting for initialization to complete...", style="dim")
    time.sleep(3)
    
    # Now run bddwarp
    print_console("\n✅ Initialization complete! Starting development loop...", style="green")
    run_bddwarp()

def simple_input(prompt):
    """Simple input function when questionary not available"""
    return input(f"{prompt}: ")

def simple_select(prompt, choices):
    """Simple selection when questionary not available"""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    while True:
        try:
            selection = int(input("Choose (number): "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
        except ValueError:
            pass
        print("Invalid choice. Please enter a number.")

def get_input(prompt, default=None):
    """Get input with fallback for missing questionary"""
    if QUESTIONARY_AVAILABLE:
        if default is None:
            return questionary.text(prompt).ask()
        else:
            return questionary.text(prompt, default=default).ask()
    else:
        result = simple_input(prompt)
        return result if result else default

def get_select(prompt, choices):
    """Get selection with fallback for missing questionary"""
    if QUESTIONARY_AVAILABLE:
        return questionary.select(prompt, choices=choices).ask()
    else:
        return simple_select(prompt, choices)

def handle_quick_start():
    """Option 1: Quick start - auto init + warp"""
    if detect_bdd_project():
        print_console("✓ BDD project detected. Continuing development...", style="green")
        run_bddwarp()
    else:
        print_console("No BDD project found.", style="yellow")
        app_goal = get_input("What would you like to build?")
        if app_goal:
            print_console(f"\n💡 Tip: Next time you can run: warpcoder \"{app_goal}\"", style="dim")
            handle_with_goal(app_goal)

def handle_initialize():
    """Option 2: Initialize new project"""
    app_goal = get_input("What would you like to build?")
    if app_goal:
        run_bddinit(app_goal)
    else:
        print_console("❌ App goal is required.", style="red")

def handle_continue():
    """Option 3: Continue existing project"""
    if detect_bdd_project():
        run_bddwarp()
    else:
        print_console("❌ No BDD project found. Run option 2 first.", style="red")

def handle_run_project():
    """Option 4: Run finished project"""
    entry_points = find_entry_points()
    if entry_points:
        if len(entry_points) == 1:
            selected = entry_points[0]
        else:
            selected = get_select("Run which file?", entry_points)
        print_console(f"🎮 Starting {selected}...", style="cyan")
        try:
            subprocess.run(["python", selected])
        except FileNotFoundError:
            print_console("❌ Python not found in PATH", style="red")
        except KeyboardInterrupt:
            print_console("\n👋 Stopped by user", style="yellow")
    else:
        print_console("❌ No entry point (play.py/menu.py) found.", style="red")

def handle_install_claude():
    """Option 5: Install Claude Code and dependencies"""
    print_console("📦 Installing Claude Code and dependencies...", style="cyan")
    if check_and_install_claude():
        print_console("✅ Installation complete!", style="green")
        
        # Ask if user wants to install MCP servers
        if QUESTIONARY_AVAILABLE:
            install_mcp = questionary.confirm(
                "Would you like to install recommended MCP servers (Context7, Puppeteer, Magic, Sequence)?",
                default=True
            ).ask()
        else:
            response = input("\nInstall recommended MCP servers? (Y/n): ").strip().lower()
            install_mcp = response != 'n'
        
        if install_mcp:
            setup_all_mcp_servers()
        else:
            print_console("💡 You can install MCP servers later from the menu", style="dim")
    else:
        print_console("❌ Installation failed. Please try manually.", style="red")

def handle_setup_only():
    """Option 6: Setup Claude environment only"""
    setup_claude_environment()
    print_console("✅ Claude environment setup complete", style="green")

def create_sdk_example():
    """Option 6: Create SDK example"""
    sdk_example = '''#!/usr/bin/env python3
"""Example of using Claude Code SDK with Context7"""

from claude_code_sdk import ClaudeClient, ClaudeOptions

# Configure with Context7 MCP
options = ClaudeOptions(
    mcp_config="mcp-servers.json",
    allowed_tools=["mcp__context7"]
)

# Create client
client = ClaudeClient(options=options)

# Example: Use Context7 for memory
project_goal = "Your project goal here"
tech_stack = "Your tech stack here"

response = client.prompt(f"""
    Remember this project is about: {project_goal}
    Tech stack: {tech_stack}
""")

print(response)
'''
    
    with open("claude_sdk_example.py", "w") as f:
        f.write(sdk_example)
    print_console("📝 Created claude_sdk_example.py for SDK usage", style="green")

def check_mcp_servers():
    """Check which MCP servers are installed"""
    if not is_claude_installed():
        return {}
    
    try:
        result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            mcp_servers = {}
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('Available servers'):
                    # Parse MCP server entries
                    server_name = line.strip().split()[0] if line.strip() else None
                    if server_name:
                        mcp_servers[server_name] = "Installed"
            return mcp_servers
        return {}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}

def check_installation_status():
    """Option 7: Check installation status"""
    print_panel("Installation Status", "Checking all components...")
    
    # Check each component
    checks = {
        "Node.js": check_command(["node", "--version"]),
        "npm": check_command(["npm", "--version"]),
        "Claude Code": check_command(["claude", "--version"]),
        "Python": check_command(["python", "--version"]),
    }
    
    # Add optional package checks
    if QUESTIONARY_AVAILABLE:
        checks["Questionary"] = "Installed"
    else:
        checks["Questionary"] = "Not installed (using fallback)"
    
    if RICH_AVAILABLE:
        checks["Rich"] = "Installed"
    else:
        checks["Rich"] = "Not installed (using plain text)"
    
    # Display results
    all_good = True
    for component, status in checks.items():
        if status and "Not installed" not in status:
            print_console(f"✅ {component}: {status}", style="green")
        else:
            print_console(f"❌ {component}: {status or 'Not installed'}", style="red")
            all_good = False
    
    # Check MCP servers
    print_console("\n📡 MCP Servers:", style="cyan bold")
    mcp_servers = check_mcp_servers()
    
    mcp_status = {
        "context7": "Context7 (Enhanced memory)",
        "puppeteer": "Puppeteer (Browser automation)",
        "magic": "Magic (AI-powered utilities)",
        "sequence-mcp": "Sequence (Sequential operations)"
    }
    
    for server_id, description in mcp_status.items():
        if server_id in mcp_servers:
            print_console(f"✅ {description}", style="green")
        else:
            print_console(f"❌ {description} - Not installed", style="dim")
    
    if not mcp_servers:
        print_console("   No MCP servers detected", style="dim")
    
    if all_good:
        print_console("\n✨ All core components installed!", style="green bold")
    else:
        print_console("\n⚠️  Some components missing. Run setup to install.", style="yellow")

def show_interactive_menu():
    """Show the interactive menu"""
    print_panel("WarpCoder BDD Tool", "Complete BDD Development Environment")
    
    choices = [
        "1. Quick Start (Auto Init + Warp)",
        "2. Initialize New Project (bddinit)",
        "3. Continue Project (bddwarp)",
        "4. Run Finished Project",
        "5. Install Claude Code & Dependencies",
        "6. Setup Claude Environment Only",
        "7. Install MCP Servers",
        "8. Create SDK Example",
        "9. Check Installation Status",
        "10. Exit"
    ]
    
    while True:
        choice = get_select("Choose an option:", choices)
        
        if "1." in choice:
            handle_quick_start()
            break
        elif "2." in choice:
            handle_initialize()
            break
        elif "3." in choice:
            handle_continue()
            break
        elif "4." in choice:
            handle_run_project()
            break
        elif "5." in choice:
            handle_install_claude()
        elif "6." in choice:
            handle_setup_only()
        elif "7." in choice:
            setup_all_mcp_servers()
        elif "8." in choice:
            create_sdk_example()
        elif "9." in choice:
            check_installation_status()
        elif "10." in choice:
            print_console("👋 Goodbye!", style="cyan")
            break

def show_help():
    """Show help information"""
    help_text = """
WarpCoder - BDD Development Tool for Claude Code

Usage:
  warpcoder "your app idea"         # Direct goal specification
  warpcoder                         # Interactive mode
  warpcoder [OPTIONS]              # Various options

Quick Start Examples:
  warpcoder "I want to build a tic tac toe game in python fastapi"
  warpcoder "Create a todo app with tags and categories"
  warpcoder "Build a REST API for managing books"
  
Options:
  --menu            Show interactive menu with all options
  --help            Show this help message
  --check           Check installation status (includes MCP servers)
  --installclaude   Install Claude Code and dependencies
  --installmcp      Install all recommended MCP servers

Default Behavior:
  - With goal: Initialize BDD project and start development
  - Without goal: Check for existing project or prompt for goal
  - Always works in current directory (no subfolders)
  - Always runs infinite iterations (no limits)

Features:
  ✓ Direct command line goal specification
  ✓ Smart tech stack detection from goal
  ✓ BDD project initialization with domain models
  ✓ Automated test-driven development loop
  ✓ Creates entry points (play.py/menu.py)

Inside Claude Code:
  /project:bddinit "your app goal"  # Initialize BDD project
  /project:bddwarp                  # Continue development (infinite)

Examples:
  warpcoder "build a chat app"      # Start new project with goal
  warpcoder                         # Continue existing or prompt
  warpcoder --menu                  # Interactive menu
  warpcoder --installclaude         # Install dependencies
"""
    print(help_text)

def main():
    """Main entry point"""
    # Check for direct goal as first argument (no --flag)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        app_goal = sys.argv[1]
        print_console(f"🚀 WarpCoder - Building: {app_goal}", style="cyan bold")
        
        # Check Claude availability
        claude_status = is_claude_installed()
        if claude_status == "installed_not_in_path":
            print_console("\n⚠️  Claude Code is installed but not in PATH", style="yellow")
            npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
            if npm_prefix:
                print_console(f"💡 Add this to your PATH: {npm_prefix.strip()}/bin", style="cyan")
                print_console("   Then restart your terminal", style="dim")
            return
        elif not claude_status:
            print_console("\n❌ Claude Code not found.", style="red")
            print_console("Install with: warp --installclaude", style="yellow")
            return
            
        handle_with_goal(app_goal)
        return
    
    # Show banner for other modes
    if RICH_AVAILABLE:
        print_console("╭─────────────────────────────╮", style="cyan")
        print_console("│     🚀 WarpCoder v0.2.5     │", style="cyan bold")
        print_console("╰─────────────────────────────╯", style="cyan")
    else:
        print_console("=== 🚀 WarpCoder v0.2.5 ===", style="")
    
    # Handle command line arguments
    if "--help" in sys.argv:
        show_help()
        return
    
    if "--check" in sys.argv:
        check_installation_status()
        return
    
    if "--installclaude" in sys.argv:
        print_console("\n📦 Installing Claude Code...", style="cyan")
        if not check_and_install_claude():
            print_console("\n❌ Could not install Claude Code.", style="red")
            print_console("Please install manually:", style="yellow")
            print_console("  npm install -g @anthropic-ai/claude-code", style="white")
            return
        print_console("\n✅ Installation complete!", style="green")
        # Try to setup Context7, but don't fail if it doesn't work
        setup_context7()
        return
    
    if "--installmcp" in sys.argv:
        print_console("\n📡 Installing MCP Servers...", style="cyan")
        if not is_claude_installed():
            print_console("\n❌ Claude Code is required to install MCP servers.", style="red")
            print_console("Install with: warp --installclaude", style="yellow")
            return
        setup_all_mcp_servers()
        return
    
    print_console("", style="")  # Empty line
    
    # Just check if Claude exists, don't install
    claude_status = is_claude_installed()
    if claude_status == True:
        print_console("✅ Claude Code detected", style="green dim")
    elif claude_status == "installed_not_in_path":
        print_console("⚠️  Claude Code installed but not in PATH", style="yellow dim")
        npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
        if npm_prefix:
            print_console(f"💡 Add to PATH: {npm_prefix.strip()}/bin", style="cyan dim")
    else:
        print_console("⚠️  Claude Code not found. Install with: warp --installclaude", style="yellow dim")
    
    # Setup Claude environment
    setup_claude_environment()
    
    # Handle menu or auto-run
    if "--menu" in sys.argv:
        show_interactive_menu()
    else:
        # DEFAULT: Auto-run based on project state
        if claude_status != True:
            if claude_status == "installed_not_in_path":
                print_console("\n⚠️  Claude Code is installed but not in PATH.", style="yellow")
                npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
                if npm_prefix:
                    print_console(f"💡 Fix by adding to PATH: {npm_prefix.strip()}/bin", style="cyan")
                    print_console("   Then restart your terminal", style="dim")
            else:
                print_console("\n⚠️  Claude Code is required to run BDD commands.", style="yellow")
                print_console("Install with: warp --installclaude", style="yellow")
            print_console("Or use menu: warp --menu", style="yellow")
            return
            
        if detect_bdd_project():
            print_console("✓ BDD project detected. Continuing development...", style="green")
            run_bddwarp()
        else:
            print_console("No BDD project found.", style="yellow")
            app_goal = get_input("What would you like to build?")
            if app_goal:
                print_console(f"\n💡 Tip: Next time you can run: warpcoder \"{app_goal}\"", style="dim")
                handle_with_goal(app_goal)

if __name__ == "__main__":
    main()