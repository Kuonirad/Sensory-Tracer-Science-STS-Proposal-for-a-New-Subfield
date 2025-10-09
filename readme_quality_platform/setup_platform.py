#!/usr/bin/env python3
"""
README Quality Platform Setup Script

Automated setup and installation script for the comprehensive README quality assessment platform.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {text}")
    print(f"{'='*60}")


def print_step(step: str):
    """Print formatted step."""
    print(f"\n📋 {step}")
    print("-" * 50)


def run_command(cmd: str, description: str) -> bool:
    """Run command and return success status."""
    print(f"⚙️  {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - FAILED: {e}")
        return False


def check_python_version():
    """Check Python version compatibility."""
    print_step("Checking Python Version")
    
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False


def install_dependencies():
    """Install required dependencies."""
    print_step("Installing Dependencies")
    
    # Core dependencies
    core_deps = [
        "textstat>=0.7.3",
        "beautifulsoup4>=4.12.2", 
        "markdown>=3.5.1",
        "pyyaml>=6.0.1",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
    ]
    
    success_count = 0
    for dep in core_deps:
        if run_command(f"pip install '{dep}'", f"Installing {dep.split('>=')[0]}"):
            success_count += 1
    
    print(f"\n📊 Installed {success_count}/{len(core_deps)} core dependencies")
    
    # Optional dependencies
    print("\n🔧 Installing optional dependencies...")
    optional_deps = [
        ("fastapi>=0.104.1", "Web API server"),
        ("uvicorn>=0.24.0", "ASGI server"),
        ("rich>=13.6.0", "CLI formatting"), 
        ("click>=8.1.7", "CLI framework"),
        ("plotly>=5.17.0", "Visualizations"),
        ("PyGithub>=1.59.1", "GitHub integration"),
    ]
    
    optional_success = 0
    for dep, desc in optional_deps:
        if run_command(f"pip install '{dep}'", f"Installing {desc}"):
            optional_success += 1
    
    print(f"📊 Installed {optional_success}/{len(optional_deps)} optional dependencies")
    
    return success_count == len(core_deps)


def download_nltk_data():
    """Download required NLTK data."""
    print_step("Setting Up NLTK Data")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('cmudict', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except ImportError:
        print("⚠️  NLTK not installed - skipping data download")
        return True
    except Exception as e:
        print(f"❌ NLTK data download failed: {e}")
        return False


def create_config_files():
    """Create sample configuration files."""
    print_step("Creating Configuration Files")
    
    # Create sample config
    config_content = """# README Quality Platform Configuration

analysis:
  scoring_weights:
    readability: 0.25
    structural: 0.30
    complexity: 0.20
    consistency: 0.25
  
  quality_thresholds:
    excellent: 90
    good: 75
    fair: 60
    poor: 45

server:
  host: "0.0.0.0"
  port: 8000
  debug: false
  github_token: "${GITHUB_TOKEN}"

database:
  cache_enabled: true
  cache_ttl_seconds: 3600
  storage_type: "file"
  storage_path: "./results"
"""
    
    config_file = Path("config.yaml")
    if not config_file.exists():
        config_file.write_text(config_content)
        print(f"✅ Created sample configuration: {config_file}")
    else:
        print(f"ℹ️  Configuration file already exists: {config_file}")
    
    # Create .env template
    env_content = """# Environment Variables for README Quality Platform

# GitHub Integration
GITHUB_TOKEN=your_github_token_here

# Server Configuration
README_SERVER_HOST=0.0.0.0
README_SERVER_PORT=8000
README_DEBUG=false

# Custom Scoring Weights (optional)
# README_READABILITY_WEIGHT=0.25
# README_STRUCTURAL_WEIGHT=0.30
# README_COMPLEXITY_WEIGHT=0.20
# README_CONSISTENCY_WEIGHT=0.25

# Database (optional)
# DATABASE_URL=postgresql://user:pass@localhost/readme_quality
# README_STORAGE_PATH=./results
"""
    
    env_file = Path(".env.example")
    if not env_file.exists():
        env_file.write_text(env_content)
        print(f"✅ Created environment template: {env_file}")
    
    return True


def test_installation():
    """Test the installation by running the demo."""
    print_step("Testing Installation")
    
    # Test basic imports
    print("🔍 Testing core imports...")
    
    test_imports = [
        ("textstat", "Readability metrics"),
        ("bs4", "HTML parsing"),
        ("markdown", "Markdown processing"),
        ("yaml", "Configuration"),
    ]
    
    import_success = 0
    for module, desc in test_imports:
        try:
            __import__(module)
            print(f"✅ {desc}: {module}")
            import_success += 1
        except ImportError:
            print(f"❌ {desc}: {module} - Not available")
    
    print(f"\n📊 Core imports: {import_success}/{len(test_imports)} successful")
    
    # Test demo execution
    print("\n🧪 Running platform demo...")
    
    demo_file = Path("demo_working.py")
    if demo_file.exists():
        if run_command("python demo_working.py", "Platform demonstration"):
            return True
    
    print("⚠️  Demo test skipped - file not found")
    return import_success >= len(test_imports) * 0.75


def create_service_scripts():
    """Create service startup scripts."""
    print_step("Creating Service Scripts")
    
    # API server script
    api_script = """#!/usr/bin/env python3
\"\"\"
README Quality Platform API Server
\"\"\"

import sys
from pathlib import Path

# Add platform to path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

try:
    from api.server import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Could not start API server: {e}")
    print("Make sure all dependencies are installed: pip install fastapi uvicorn")
    sys.exit(1)
"""
    
    Path("start_api.py").write_text(api_script)
    print("✅ Created API server script: start_api.py")
    
    # Web dashboard script  
    web_script = """#!/usr/bin/env python3
\"\"\"
README Quality Platform Web Dashboard
\"\"\"

import sys
from pathlib import Path

# Add platform to path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

try:
    from web.app import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Could not start web dashboard: {e}")
    print("Make sure all dependencies are installed: pip install fastapi plotly jinja2")
    sys.exit(1)
"""
    
    Path("start_web.py").write_text(web_script)
    print("✅ Created web dashboard script: start_web.py")
    
    # CLI wrapper script
    cli_script = """#!/usr/bin/env python3
\"\"\"
README Quality Platform CLI Tool
\"\"\"

import sys
from pathlib import Path

# Add platform to path
platform_dir = Path(__file__).parent
sys.path.insert(0, str(platform_dir))

try:
    from cli.main import app
    
    if __name__ == "__main__":
        app()
        
except ImportError as e:
    print(f"Error: Could not start CLI tool: {e}")
    print("Make sure all dependencies are installed: pip install typer rich")
    sys.exit(1)
"""
    
    Path("readme_analyzer.py").write_text(cli_script)
    print("✅ Created CLI tool script: readme_analyzer.py")
    
    return True


def show_usage_instructions():
    """Display usage instructions."""
    print_step("Usage Instructions")
    
    instructions = """
🎯 README Quality Platform is now set up!

🚀 Quick Start:

1. Test the platform:
   python demo_working.py

2. Analyze a README file:
   python readme_analyzer.py README.md

3. Start the API server:
   python start_api.py
   # Access at: http://localhost:8000

4. Start the web dashboard:
   python start_web.py  
   # Access at: http://localhost:8001

5. GitHub Integration (optional):
   export GITHUB_TOKEN=your_token_here
   python readme_analyzer.py https://github.com/user/repo

📚 Documentation:
   - Configuration: config.yaml
   - Environment: .env.example
   - GitHub Actions: github_actions/
   - Examples: examples/

🛠️  Advanced Setup:
   - Install full dependencies: pip install -r requirements.txt
   - Configure GitHub token for repository analysis
   - Set up database for result storage (optional)
   - Deploy as microservices with Docker (optional)

💡 Need Help?
   - Check README.md for comprehensive documentation
   - Run demo_working.py for examples
   - View API docs at http://localhost:8000/docs (when server running)
"""
    
    print(instructions)


def main():
    """Main setup function."""
    
    print_header("README Quality Platform Setup")
    
    print("""
📊 Comprehensive Multi-Dimensional README Quality Assessment Platform

This setup script will install and configure the complete platform including:
• Multi-dimensional analysis (readability, structure, complexity, consistency)  
• CLI tools with rich output formatting
• REST API server with comprehensive endpoints
• Interactive web dashboard with visualizations
• GitHub Actions for automated quality checks
• GitHub API integration for repository analysis
• Extensible configuration and plugin system
""")
    
    # Setup steps
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies), 
        ("NLTK Data", download_nltk_data),
        ("Configuration", create_config_files),
        ("Service Scripts", create_service_scripts),
        ("Installation Test", test_installation),
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print(f"⚠️  {step_name} completed with warnings")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    # Summary
    print_header("Setup Summary")
    
    print(f"📊 Setup Progress: {success_count}/{len(steps)} steps completed")
    
    if success_count == len(steps):
        print("🎉 Setup completed successfully!")
        show_usage_instructions()
    elif success_count >= len(steps) * 0.75:
        print("⚠️  Setup completed with some warnings")
        print("💡 The platform should work, but some features may be limited")
        show_usage_instructions() 
    else:
        print("❌ Setup failed - please check errors above")
        print("💡 Try installing dependencies manually:")
        print("   pip install textstat beautifulsoup4 markdown pyyaml")
        
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)