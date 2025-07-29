#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nust-nmap Python library

Unified Enterprise-Grade Python Nmap Wrapper with enhanced capabilities
built into the original API. No "Enhanced" or duplicated classes.

Quick Start:
    >>> import nmap
    >>> nm = nmap.PortScanner()
    >>> result = nm.scan('127.0.0.1', '22-443')
    >>> print(nm.csv())

Advanced Usage:
    >>> # Stealth scanning
    >>> result = nm.scan_with_evasion('target.com', profile=nmap.EvasionProfile.GHOST)
    >>> 
    >>> # Async scanning
    >>> def callback(host, data): print(f"Found: {host}")
    >>> nm_async = nmap.PortScannerAsync()
    >>> nm_async.scan('192.168.1.0/24', callback=callback)
    >>>
    >>> # Memory-efficient large network scanning
    >>> nm_yield = nmap.PortScannerYield()
    >>> for host, data in nm_yield.scan('10.0.0.0/16'):
    ...     process_host(host, data)

Author: Sameer Ahmed (sameer.cs@proton.me)
License: GPL v3 or later
Source: https://github.com/codeNinja62/nust-nmap
"""

__version__ = "2.0.0"
__author__ = "Sameer Ahmed"

# Type imports
from typing import Optional, List, Dict, Any

# === UNIFIED ENTERPRISE API ===
# Single file with enhanced original functions - no duplicates
from .nmap import (
    # Version and metadata
    __author__, 
    __last_modification__, 
    __version__,
    
    # Core scanner classes (enhanced originals)
    PortScanner,
    PortScannerAsync, 
    PortScannerYield,
    PortScannerHostDict,
    
    # Exception classes
    PortScannerError,
    PortScannerTimeout,
    
    # Enums
    ScanType,
    EvasionProfile,
    
    # Utility functions
    enable_performance_monitoring,
    set_cache_max_age,
    clear_global_cache,
    
    # Convenience functions
    scan_stealth,
    scan_ghost,
    scan_progressive,
    
    # Modern aliases
    Scanner,
    AsyncScanner,
    YieldScanner,
)

# === ALIASES FOR CONVENIENCE ===
# Provide intuitive aliases while maintaining original names
Scanner = PortScanner              # Modern alias for new projects
AsyncScanner = PortScannerAsync    # Modern alias for async scanning
YieldScanner = PortScannerYield    # Modern alias for yield scanning

# Legacy compatibility
EnhancedPortScanner = PortScanner    
ComprehensiveScanner = PortScanner   

# === CONVENIENCE API FUNCTIONS ===
def scan_with_evasion(targets: str, profile: EvasionProfile = EvasionProfile.STEALTH, **kwargs):
    """
    Quick evasion scanning with predefined profiles.
    
    Args:
        targets: Target specification (IP, range, domain)
        profile: Evasion profile (STEALTH, BASIC, GHOST, ADAPTIVE)
        **kwargs: Additional scan options
        
    Returns:
        Scan results with evasion applied
    """
    scanner = PortScanner()
    return scanner.scan_with_evasion(targets, profile=profile, **kwargs)


def scan_network(network: str, **kwargs) -> Dict[str, Any]:
    """Quick network scan with sensible defaults"""
    scanner = PortScanner()
    return scanner.network_discovery(network, **kwargs)


def scan_host(host: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Quick host scan with service detection"""
    scanner = PortScanner()
    return scanner.version_scan(host, ports, **kwargs)


def scan_vulnerabilities(target: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Quick vulnerability scan"""
    scanner = PortScanner()
    return scanner.vuln_scan(target, ports, **kwargs)


# === PUBLIC API ===
__all__ = [
    # Core classes
    'PortScanner', 'PortScannerAsync', 'PortScannerYield', 'PortScannerHostDict',
    
    # Modern aliases
    'Scanner', 'AsyncScanner', 'YieldScanner',
    
    # Legacy compatibility
    'EnhancedPortScanner', 'ComprehensiveScanner',
    
    # Exceptions
    'PortScannerError', 'PortScannerTimeout',
    
    # Enums and types
    'ScanType', 'EvasionProfile',
    
    # Convenience functions
    'scan_with_evasion', 'scan_network', 'scan_host', 'scan_vulnerabilities',
    'scan_stealth', 'scan_ghost', 'scan_progressive',
    
    # Configuration
    'enable_performance_monitoring', 'set_cache_max_age', 'clear_global_cache',
]
