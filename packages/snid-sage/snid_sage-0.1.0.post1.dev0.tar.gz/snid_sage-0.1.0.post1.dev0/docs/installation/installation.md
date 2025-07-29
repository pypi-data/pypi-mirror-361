# Installation Guide

This guide provides comprehensive instructions for installing SNID SAGE on your system.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **Python**: 3.9 or 3.10
- **RAM**: 16GB for optimal performance
- **Storage**: 5GB+ for templates and results
- **GPU**: CUDA-compatible for local LLM support (optional)

## Quick Installation

### Recommended Method: Install from TestPyPI

SNID SAGE is available on TestPyPI. This is the preferred installation method:

```bash
pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3
```

For installation with all optional features:

```bash
pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3 --extra-index-url https://pypi.org/simple
```

### Virtual Environment Setup

#### Using venv (Recommended)

**Windows:**
```powershell
# Create virtual environment
python -m venv snid_env

# Activate environment
snid_env\Scripts\activate

# Install SNID SAGE
pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3

# Verify installation
python -c "import snid_sage; print('SNID SAGE installed successfully!')"

# Deactivate when done
deactivate
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv snid_env

# Activate environment
source snid_env/bin/activate

# Install SNID SAGE
pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3

# Verify installation
python -c "import snid_sage; print('SNID SAGE installed successfully!')"

# Deactivate when done
deactivate
```

#### Using conda

```bash
# Create conda environment with Python 3.10
conda create -n snid_sage python=3.10

# Activate environment
conda activate snid_sage

# Install SNID SAGE from TestPyPI
pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3

# Verify installation
python -c "import snid_sage; print('SNID SAGE installed successfully!')"

# Deactivate when done
conda deactivate
```

### Alternative: Install from Source

If you need the latest development version or want to contribute:

```bash
# Clone repository
git clone https://github.com/FiorenSt/SNID-SAGE.git
cd SNID_SAGE

# Install in development mode
pip install -e .

# For all optional features
pip install -e ".[all]"
```

## Platform-Specific Instructions

### Windows

1. **Install Python 3.8+** from [python.org](https://python.org/downloads/)
2. **Ensure pip is in PATH** during Python installation
3. **PowerShell Execution Policy** (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. **Install SNID SAGE**:
   ```powershell
   pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3
   ```

### macOS

1. **Install Python** (if not present):
   ```bash
   # Using Homebrew
   brew install python@3.10
   ```
2. **Install Xcode Command Line Tools** (if needed):
   ```bash
   xcode-select --install
   ```
3. **Install SNID SAGE**:
   ```bash
   pip3 install -i https://test.pypi.org/simple/ snid-sage==1.2.3
   ```

### Linux

**Ubuntu/Debian:**
```bash
# Update package manager
sudo apt update

# Install Python and pip
sudo apt install python3.10 python3-pip python3-tk

# Install SNID SAGE
pip3 install -i https://test.pypi.org/simple/ snid-sage==1.2.3
```

**Fedora/CentOS/RHEL:**
```bash
# Install Python and pip
sudo dnf install python3.10 python3-pip python3-tkinter  # Fedora
# sudo yum install python3 python3-pip python3-tkinter   # CentOS/RHEL

# Install SNID SAGE
pip3 install -i https://test.pypi.org/simple/ snid-sage==1.2.3
```

## Launching SNID SAGE

After installation, you can launch SNID SAGE using the following commands:

### GUI Interface
```bash
snid-sage
# or
snid-gui
```

### Command Line Interface
```bash
snid --help
```

### Quick Analysis Example
```bash
# Analyze a spectrum
snid identify spectrum.dat -o results
```

## Installation Verification

### Test Basic Installation
```bash
# Test Python import
python -c "import snid_sage; print('Core modules OK')"

# Check version
snid --version

# Launch GUI (will open a window)
snid-gui
```

### Test with Sample Data
```bash
# Download sample spectrum (if not included)
# Run analysis
snid identify data/sn2003jo.dat --output-dir test_results/
```

## Troubleshooting

### Common Issues

**"Module not found" errors:**
- Ensure you're using the correct Python environment
- Try reinstalling: `pip install -i https://test.pypi.org/simple/ snid-sage==1.2.3 --force-reinstall`

**GUI doesn't launch:**
- Linux: Install tkinter: `sudo apt install python3-tk`
- macOS: Ensure XQuartz is installed for X11 support
- Windows: Tkinter should be included with Python

**Permission errors:**
- Use `--user` flag: `pip install --user -i https://test.pypi.org/simple/ snid-sage==1.2.3`
- Or use a virtual environment (recommended)

**SSL Certificate errors:**
- Add `--trusted-host test.pypi.org` to pip command
- Update certificates on macOS: `/Applications/Python\ 3.x/Install\ Certificates.command`

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Search [GitHub Issues](https://github.com/FiorenSt/SNID-SAGE/issues)
3. Create a new issue with:
   - Operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

## Updating SNID SAGE

### From TestPyPI
```bash
pip install -i https://test.pypi.org/simple/ snid-sage --upgrade
```

### From Source
```bash
cd SNID_SAGE
git pull origin main
pip install -e . --upgrade
```

## Uninstallation

```bash
# Uninstall package
pip uninstall snid-sage

# Remove virtual environment (if used)
rm -rf snid_env  # Unix/macOS
# or
rmdir /s snid_env  # Windows

# Remove conda environment (if used)
conda remove -n snid_sage --all
```

## Next Steps

After installation, proceed to the [Quick Start Guide](../quickstart/first-analysis.md) to perform your first supernova spectrum analysis! 