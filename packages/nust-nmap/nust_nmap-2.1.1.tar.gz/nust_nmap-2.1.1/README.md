<h1 align="center">nust-nmap</h1>
<p align="center">
    <img src="https://badge.fury.io/py/nust-nmap.svg" alt="PyPI version" />
    <img src="https://img.shields.io/pypi/pyversions/nust-nmap.svg" alt="Python versions" />
    <img src="https://img.shields.io/badge/License-GPL--3.0-blue.svg" alt="License: GPL-3.0" />
    <img src="https://pepy.tech/badge/nust-nmap" alt="Downloads" />
</p>

<p align="center">
    <strong>🎯 Enterprise-Grade Python Nmap Wrapper</strong><br>
    <em>Production-ready network scanning with built-in stealth capabilities</em>
</p>

---

## 🌟 **What is nust-nmap?**

A comprehensive Python wrapper for nmap that enhances the original functionality with enterprise-grade features. Designed for security professionals, penetration testers, and network administrators who need reliable, production-ready network scanning capabilities.

## ✨ **Key Features**

- **🎯 Complete nmap Coverage**: All scan types, NSE scripts, and advanced features
- **🛡️ Built-in Security**: Stealth profiles, evasion techniques, input validation
- **⚡ High Performance**: Async scanning, intelligent caching, memory efficiency
- **🔧 Enterprise Ready**: Thread-safe, comprehensive error handling, resource management
- **📊 Rich Output**: Multiple export formats (XML, JSON, CSV) with enhanced parsing
- **🌐 Cross-Platform**: Windows, macOS, Linux with automatic nmap detection
- **🔄 100% Compatible**: Drop-in replacement for python-nmap

## 📦 **Quick Installation**

### Prerequisites
- **Python 3.8+** 
- **Nmap 7.90+** installed on your system

### Install
```bash
pip install nust-nmap
```

### Install Nmap
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nmap

# macOS  
brew install nmap

# Windows: Download from nmap.org
```

## 🚀 **Quick Start**

### Basic Usage
```python
import nmap

# Create scanner instance
scanner = nmap.PortScanner()

# Basic network scan
result = scanner.scan('192.168.1.0/24', '22,80,443')

# Process results
for host in scanner.all_hosts():
    print(f"Host: {host} ({scanner[host].state()})")
    for protocol in scanner[host].all_protocols():
        ports = scanner[host][protocol].keys()
        for port in ports:
            state = scanner[host][protocol][port]['state']
            print(f"  {port}/{protocol}: {state}")
```

### Stealth Scanning
```python
# Built-in stealth profiles
result = scanner.scan(
    hosts='target.com',
    evasion_profile=nmap.EvasionProfile.STEALTH
)

# Quick stealth functions
result = nmap.scan_stealth('target.com', '1-1000')
result = nmap.scan_ghost('target.com', '80,443')  # Maximum stealth
```

### Advanced Features
```python
# Asynchronous scanning
def scan_callback(host, result):
    print(f"Completed scan for {host}")

nmap.scan_progressive('192.168.1.0/24', callback=scan_callback)

# Memory-efficient large network scanning
yield_scanner = nmap.YieldScanner()
for host, result in yield_scanner.scan('10.0.0.0/16'):
    process_host_data(host, result)
```

## 📚 **Documentation**

- **[📖 Complete Programmer Guide](README_PROGRAMMER_GUIDE.md)**: Comprehensive technical documentation
- **[🔧 API Reference](docs/)**: Detailed API documentation  
- **[🚀 Examples](examples/)**: Usage examples and patterns
- **[📝 Changelog](docs/CHANGELOG.md)**: Version history and updates

## 🛡️ **Security & Ethics**

This tool is designed for legitimate security testing and network administration. Users are responsible for:
- Obtaining proper authorization before scanning networks
- Complying with applicable laws and regulations
- Using responsible disclosure for any vulnerabilities discovered

## 🤝 **Contributing**

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## 📄 **License**

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## � **Author**

**Sameer Ahmed**
- Email: [sameer.cs@proton.me](mailto:sameer.cs@proton.me)
- GitHub: [@codeNinja62](https://github.com/codeNinja62)

## �🙏 **Acknowledgments**

- Powered by the [Nmap Security Scanner](https://nmap.org/) - the industry standard for network discovery
- Inspired by the network security community and best practices in vulnerability assessment
- Thanks to the cybersecurity community for continuous feedback and improvements

## 🔗 **Links**

- [📦 PyPI Package](https://pypi.org/project/nust-nmap/)
- [📚 Documentation](https://github.com/codeNinja62/nust-nmap/wiki)
- [🐛 Issue Tracker](https://github.com/codeNinja62/nust-nmap/issues)
- [🌐 Nmap Official Site](https://nmap.org/)

## ⚠️ **Legal Disclaimer**

**IMPORTANT: This tool is designed for authorized security testing and network administration only.**

- ✅ **Authorized Use**: Own networks, approved penetration testing, security research
- ❌ **Prohibited Use**: Unauthorized scanning, malicious activities, illegal reconnaissance

**Users are solely responsible for compliance with applicable laws and regulations. Always obtain explicit permission before scanning networks you do not own or administer.**

---

<p align="center">
    <strong>⚡ Ready to secure your network? Start scanning with nust-nmap today!</strong>
</p>
