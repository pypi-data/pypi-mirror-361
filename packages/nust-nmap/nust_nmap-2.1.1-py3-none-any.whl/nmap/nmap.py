#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nmap.py - Enterprise-Grade Python Nmap Wrapper

Complete implementation of nmap functionality with enhanced capabilities built into
the original API. No "Enhanced" or duplicated classes - just improved functionality
within the standard API.

This module provides a comprehensive Python interface to the nmap network scanning
tool, designed for network and vulnerability analysis systems. It exposes all nmap
features through a clean, Pythonic API while adding enterprise-grade enhancements.

Key Features:
- Complete nmap feature coverage (all scan types, NSE, evasion, etc.)
- Intelligent caching with configurable TTL
- Async and memory-efficient scanning
- Advanced evasion and stealth capabilities
- Comprehensive validation and error handling
- Performance monitoring and resource management
- Multiple output formats (XML, JSON, CSV)
- Thread-safe operations
- Security-focused design

Quick Start Examples:

Basic Scanning:
    >>> import nmap
    >>> nm = nmap.PortScanner()
    >>> result = nm.scan('192.168.1.1', '22-443')
    >>> print(nm.csv())

Advanced Network Discovery:
    >>> nm = nmap.PortScanner()
    >>> result = nm.network_discovery('192.168.1.0/24')
    >>> alive_hosts = nm.all_hosts()

Vulnerability Assessment:
    >>> nm = nmap.PortScanner()
    >>> result = nm.vuln_scan('target.com', '80,443')
    >>> vulns = nm.vulnerability_summary()

Stealth Scanning:
    >>> nm = nmap.PortScanner()
    >>> result = nm.scan_with_evasion('target.com', 
    ...                               profile=nmap.EvasionProfile.GHOST)

Async Scanning:
    >>> def callback(host, data):
    ...     print(f"Found host: {host}")
    >>> 
    >>> nm_async = nmap.PortScannerAsync()
    >>> nm_async.scan('192.168.1.0/24', callback=callback)

Memory-Efficient Large Network Scanning:
    >>> nm_yield = nmap.PortScannerYield()
    >>> for host, data in nm_yield.scan('10.0.0.0/16'):
    ...     process_host_data(host, data)

Source code : https://github.com/codeNinja62/nust-nmap

Author:
* Sameer Ahmed - sameer.cs@proton.me

License: GPL v3 or any later version

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

**************
IMPORTANT NOTE
**************

The Nmap Security Scanner used by python-nmap is distributed
under its own licence that you can find at https://svn.nmap.org/nmap/COPYING

Any redistribution of python-nmap along with the Nmap Security Scanner
must conform to the Nmap Security Scanner licence
"""

import asyncio
import base64
import csv
import hashlib
import io
import ipaddress
import json
import logging
import os
import random
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from multiprocessing import Process
from pathlib import Path
from typing import (
    Any, AsyncGenerator, Callable, Dict, Generator, List, Optional, 
    Set, TextIO, Tuple, Union
)
from xml.etree import ElementTree as ET

# =====================================================================
# MODULE METADATA
# =====================================================================

__author__ = "Sameer Ahmed (sameer.cs@proton.me)"
__version__ = "2.1.1"
__last_modification__ = "2025.07.10"

# =====================================================================
# OPTIONAL DEPENDENCIES
# =====================================================================

# Optional psutil import for advanced resource monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None  # type: ignore
    PSUTIL_AVAILABLE = False

# =====================================================================
# LOGGING AND CONFIGURATION
# =====================================================================

logger = logging.getLogger(__name__)

# Thread-safe caching and configuration
_scan_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_cache_max_age = 300  # 5 minutes
_scan_lock = threading.Lock()
_performance_monitoring = False

# =====================================================================
# EVASION AND SECURITY ENUMS (INTEGRATED)
# =====================================================================

class EvasionProfile(Enum):
    """Built-in evasion profiles for stealth scanning"""
    BASIC = "basic"
    STEALTH = "stealth"
    GHOST = "ghost"
    ADAPTIVE = "adaptive"

class ScanType(Enum):
    """Standard nmap scan types"""
    TCP_SYN = "-sS"
    TCP_CONNECT = "-sT"
    TCP_ACK = "-sA"
    TCP_WINDOW = "-sW"
    TCP_MAIMON = "-sM"
    UDP = "-sU"
    SCTP_INIT = "-sY"
    SCTP_COOKIE = "-sZ"
    IP_PROTOCOL = "-sO"
    FIN = "-sF"
    NULL = "-sN"
    XMAS = "-sX"

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def _find_nmap_executable() -> List[str]:
    """Find nmap executable across platforms"""
    nmap_paths = []
    
    # Check PATH first
    nmap_in_path = shutil.which("nmap")
    if nmap_in_path:
        nmap_paths.append(nmap_in_path)
    
    # Platform-specific paths
    if sys.platform.startswith("win"):
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        windows_paths = [
            os.path.join(program_files, "Nmap", "nmap.exe"),
            os.path.join(program_files_x86, "Nmap", "nmap.exe"),
        ]
        nmap_paths.extend(windows_paths)
    
    elif sys.platform.startswith("darwin"):
        macos_paths = [
            "/usr/local/bin/nmap",
            "/opt/local/bin/nmap",
            "/sw/bin/nmap",
        ]
        nmap_paths.extend(macos_paths)
    
    else:  # Linux/Unix
        unix_paths = [
            "/usr/bin/nmap",
            "/usr/local/bin/nmap",
            "/usr/sbin/nmap",
        ]
        nmap_paths.extend(unix_paths)
    
    # Return unique paths that exist
    unique_paths = []
    seen = set()
    for path in nmap_paths:
        if path and path not in seen and os.path.isfile(path):
            unique_paths.append(path)
            seen.add(path)
    
    return unique_paths

def _validate_targets(hosts: str) -> bool:
    """Validate target specifications"""
    if not hosts or not hosts.strip():
        return False
    
    # Basic validation - could be enhanced further
    # Allow IP addresses, hostnames, CIDR notation, ranges
    return True

def _build_evasion_arguments(profile: EvasionProfile) -> List[str]:
    """Build nmap arguments for evasion profiles"""
    evasion_args = []
    
    if profile == EvasionProfile.BASIC:
        evasion_args.extend(["-T2", "--randomize-hosts"])
    
    elif profile == EvasionProfile.STEALTH:
        evasion_args.extend([
            "-T1", "--randomize-hosts", "-f",
            "--scan-delay", "1s", "--max-scan-delay", "3s"
        ])
    
    elif profile == EvasionProfile.GHOST:
        evasion_args.extend([
            "-T0", "--randomize-hosts", "-f", "-f",
            "--scan-delay", "2s", "--max-scan-delay", "5s",
            "--spoof-mac", "0"
        ])
    
    elif profile == EvasionProfile.ADAPTIVE:
        # Adaptive profile adjusts based on target
        evasion_args.extend(["-T2", "--randomize-hosts"])
    
    return evasion_args

def _cache_key(hosts: str, arguments: str) -> str:
    """Generate cache key for scan results"""
    key_data = f"{hosts}:{arguments}".encode('utf-8')
    return hashlib.md5(key_data).hexdigest()

def _is_cache_valid(timestamp: float) -> bool:
    """Check if cached result is still valid"""
    return time.time() - timestamp < _cache_max_age

# =====================================================================
# CORE SCANNER CLASS
# =====================================================================

class PortScanner:
    """
    PortScanner class with enhanced capabilities built into the original API.
    
    No "Enhanced" classes needed - all improvements are integrated seamlessly
    while maintaining full backward compatibility.
    """
    
    def __init__(self, nmap_search_path: Optional[List[str]] = None):
        """
        Initialize PortScanner with automatic nmap detection and enhanced features.
        
        Args:
            nmap_search_path: Custom paths to search for nmap executable
        """
        self._scan_result: Dict[str, Any] = {}
        self._nmap_path: str = ""
        self._nmap_version_number: Tuple[int, int] = (0, 0)
        self._nmap_subversion_number: int = 0
        self._nmap_last_output: str = ""
        
        # Enhanced features (internal)
        self._enable_caching = True
        self._enable_evasion = False
        self._current_evasion_profile = EvasionProfile.BASIC
        self._performance_stats: Dict[str, Any] = {}
        
        # Find nmap executable
        nmap_paths = nmap_search_path or _find_nmap_executable()
        
        for nmap_path in nmap_paths:
            if nmap_path and os.path.isfile(nmap_path):
                if os.access(nmap_path, os.X_OK):
                    self._nmap_path = nmap_path
                    break
        
        if not self._nmap_path:
            raise PortScannerError(
                "nmap program was not found in path. Please install nmap or specify nmap_search_path."
            )
        
        # Get nmap version
        try:
            output = subprocess.check_output(
                [self._nmap_path, '--version'], 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                timeout=10
            )
            regex_result = re.search(r'Nmap version (\d+)\.(\d+)', output)
            if regex_result:
                self._nmap_version_number = (
                    int(regex_result.group(1)),
                    int(regex_result.group(2))
                )
                
                # Extract subversion if present
                regex_sub = re.search(r'Nmap version \d+\.\d+\.(\d+)', output)
                if regex_sub:
                    self._nmap_subversion_number = int(regex_sub.group(1))
        
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not determine nmap version")
    
    def scan(
        self, 
        hosts: str = "127.0.0.1", 
        ports: Optional[str] = None,
        arguments: str = "-sV",
        sudo: bool = False,
        timeout: Optional[int] = None,
        evasion_profile: Optional[EvasionProfile] = None
    ) -> Dict[str, Any]:
        """
        Scan given hosts with enhanced capabilities built-in.
        
        Args:
            hosts: Host(s) to scan
            ports: Port specification
            arguments: Nmap arguments
            sudo: Use sudo (Unix/Linux only)
            timeout: Scan timeout in seconds
            evasion_profile: Enable stealth/evasion techniques
            
        Returns:
            Dictionary containing scan results
        """
        if not _validate_targets(hosts):
            raise PortScannerError("Invalid target specification")
        
        # Check cache first (if enabled)
        cache_key = _cache_key(hosts, arguments) if self._enable_caching else None
        if cache_key and cache_key in _scan_cache:
            cached_result, timestamp = _scan_cache[cache_key]
            if _is_cache_valid(timestamp):
                logger.debug(f"Using cached result for {hosts}")
                self._scan_result = cached_result
                return cached_result
        
        # Build command
        nmap_command = []
        
        # Add sudo if requested (Unix/Linux only)
        if sudo and not sys.platform.startswith('win'):
            nmap_command.append('sudo')
        
        nmap_command.append(self._nmap_path)
        
        # Add evasion arguments if profile specified
        if evasion_profile:
            evasion_args = _build_evasion_arguments(evasion_profile)
            nmap_command.extend(evasion_args)
            logger.debug(f"Applied evasion profile: {evasion_profile.value}")
        
        # Add ports if specified
        if ports:
            nmap_command.extend(['-p', str(ports)])
        
        # Add custom arguments
        if arguments:
            # Parse arguments safely
            try:
                parsed_args = shlex.split(arguments)
                nmap_command.extend(parsed_args)
            except ValueError as e:
                raise PortScannerError(f"Invalid arguments: {e}")
        
        # Always output XML for parsing
        nmap_command.extend(['-oX', '-'])
        
        # Add hosts
        nmap_command.append(hosts)
        
        # Execute scan
        start_time = time.time()
        
        try:
            logger.debug(f"Running: {' '.join(nmap_command)}")
            
            process = subprocess.Popen(
                nmap_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Handle timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                raise PortScannerTimeout(f"Scan timeout after {timeout} seconds")
            
            self._nmap_last_output = stdout
            
            if process.returncode != 0:
                raise PortScannerError(f"Nmap scan failed: {stderr}")
            
            # Parse results
            scan_result = self.analyse_nmap_xml_scan(stdout, stderr)
            
            # Store performance stats
            scan_duration = time.time() - start_time
            self._performance_stats = {
                'scan_duration': scan_duration,
                'hosts_scanned': len(scan_result.get('scan', {})),
                'command_used': ' '.join(nmap_command)
            }
            
            # Cache result if caching enabled
            if cache_key and self._enable_caching:
                with _scan_lock:
                    _scan_cache[cache_key] = (scan_result, time.time())
            
            return scan_result
            
        except FileNotFoundError:
            raise PortScannerError(f"nmap executable not found at {self._nmap_path}")
        except PermissionError:
            raise PortScannerError("Permission denied. Try running with sudo.")
        except Exception as e:
            raise PortScannerError(f"Scan failed: {e}")
    
    def analyse_nmap_xml_scan(
        self,
        nmap_xml_output: Optional[str] = None,
        nmap_err: str = "",
        nmap_err_keep_trace: Optional[List[str]] = None,
        nmap_warn_keep_trace: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyse nmap XML output with enhanced parsing capabilities.
        
        Args:
            nmap_xml_output: XML output from nmap
            nmap_err: Error output from nmap
            nmap_err_keep_trace: Error patterns to keep in trace
            nmap_warn_keep_trace: Warning patterns to keep in trace
            
        Returns:
            Parsed scan results dictionary
        """
        if nmap_xml_output is None:
            nmap_xml_output = self._nmap_last_output
        
        scan_result: Dict[str, Any] = {
            'nmap': {
                'command_line': '',
                'scaninfo': {},
                'scanstats': {}
            },
            'scan': {}
        }
        
        if not nmap_xml_output:
            return scan_result
        
        try:
            # Parse XML
            dom = ET.fromstring(nmap_xml_output)
            
            # Extract command line
            scan_result['nmap']['command_line'] = dom.get('args', '')
            
            # Extract scan info
            scaninfo_element = dom.find('scaninfo')
            if scaninfo_element is not None:
                scan_result['nmap']['scaninfo'] = dict(scaninfo_element.attrib)
            
            # Extract scan stats
            runstats_element = dom.find('runstats')
            if runstats_element is not None:
                finished_element = runstats_element.find('finished')
                if finished_element is not None:
                    scan_result['nmap']['scanstats']['timestr'] = finished_element.get('timestr', '')
                    scan_result['nmap']['scanstats']['elapsed'] = finished_element.get('elapsed', '')
                
                hosts_element = runstats_element.find('hosts')
                if hosts_element is not None:
                    scan_result['nmap']['scanstats'].update(dict(hosts_element.attrib))
            
            # Parse hosts
            for dhost in dom.findall('host'):
                host = None
                hostname = ""
                
                # Get host address
                for address in dhost.findall('address'):
                    if address.get('addrtype') == 'ipv4':
                        host = address.get('addr')
                        break
                    elif address.get('addrtype') == 'ipv6':
                        host = address.get('addr')
                        break
                
                if not host:
                    continue
                
                # Get hostname
                for dhostname in dhost.findall('hostnames/hostname'):
                    hostname = dhostname.get('name', '')
                    break
                
                # Initialize host data
                scan_result['scan'][host] = {
                    'hostnames': [{'name': hostname, 'type': ''}] if hostname else [],
                    'addresses': {},
                    'vendor': {},
                    'status': {'state': 'unknown', 'reason': ''},
                    'tcp': {},
                    'udp': {},
                    'ip': {},
                    'sctp': {}
                }
                
                # Parse addresses
                for address in dhost.findall('address'):
                    addr_type = address.get('addrtype')
                    scan_result['scan'][host]['addresses'][addr_type] = address.get('addr', '')
                    if address.get('vendor'):
                        scan_result['scan'][host]['vendor'][address.get('addr', '')] = address.get('vendor', '')
                
                # Parse status
                status_element = dhost.find('status')
                if status_element is not None:
                    scan_result['scan'][host]['status'] = dict(status_element.attrib)
                
                # Parse ports
                ports_element = dhost.find('ports')
                if ports_element is not None:
                    for dport in ports_element.findall('port'):
                        protocol = dport.get('protocol')
                        port_id = dport.get('portid')
                        
                        if not protocol or not port_id:
                            continue
                        
                        # Create properly typed dictionary for mixed value types
                        port_info: Dict[str, Any] = {
                            'state': '', 'reason': '', 'name': '', 'product': '', 
                            'version': '', 'extrainfo': '', 'conf': ''
                        }
                        
                        # Parse state
                        state_element = dport.find('state')
                        if state_element is not None:
                            port_info.update(dict(state_element.attrib))
                        
                        # Parse service
                        service_element = dport.find('service')
                        if service_element is not None:
                            port_info.update(dict(service_element.attrib))
                        
                        # Parse scripts
                        port_info['script'] = {}
                        for script in dport.findall('script'):
                            script_id = script.get('id')
                            script_output = script.get('output', '')
                            if script_id:
                                port_info['script'][script_id] = script_output
                        
                        scan_result['scan'][host][protocol][int(port_id)] = port_info
                
                # Parse OS detection
                os_element = dhost.find('os')
                if os_element is not None:
                    scan_result['scan'][host]['osmatch'] = []
                    for osmatch in os_element.findall('osmatch'):
                        # Create properly typed dictionary for mixed value types
                        match_info: Dict[str, Any] = dict(osmatch.attrib)
                        match_info['osclass'] = []
                        for osclass in osmatch.findall('osclass'):
                            match_info['osclass'].append(dict(osclass.attrib))
                        scan_result['scan'][host]['osmatch'].append(match_info)
                
                # Parse traceroute
                for dtrace in dhost.findall('trace'):
                    # Create properly typed dictionary for mixed value types
                    trace_info: Dict[str, Any] = {
                        'port': dtrace.get('port', ''),
                        'protocol': dtrace.get('proto', ''),
                        'hops': []
                    }
                    scan_result['scan'][host]['trace'] = trace_info
                    
                    for dhop in dtrace.findall('hop'):
                        hop_info: Dict[str, str] = {
                            'ttl': dhop.get('ttl', ''),
                            'ipaddr': dhop.get('ipaddr', ''),
                            'rtt': dhop.get('rtt', ''),
                            'host': dhop.get('host', '')
                        }
                        scan_result['scan'][host]['trace']['hops'].append(hop_info)
            
            # Store result
            self._scan_result = scan_result
            return scan_result
            
        except ET.ParseError as e:
            raise PortScannerError(f"Failed to parse XML output: {e}")
        except Exception as e:
            raise PortScannerError(f"Analysis failed: {e}")
    
    # =================================================================
    # CONVENIENCE METHODS (ENHANCED INTERNALLY)
    # =================================================================
    
    def listscan(self, hosts: str = "127.0.0.1") -> List[str]:
        """List scan with enhanced host discovery"""
        scan_result = self.scan(hosts=hosts, arguments="-sL")
        return [host for host in scan_result.get('scan', {}).keys()]
    
    def csv(self) -> str:
        """Export scan results to CSV format"""
        if not self._scan_result:
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['host', 'hostname', 'hostname_type', 'protocol', 'port', 'name', 'state', 'product', 'extrainfo', 'reason', 'version', 'conf', 'cpe'])
        
        # Data rows
        for host in self._scan_result.get('scan', {}):
            hostnames = self._scan_result['scan'][host].get('hostnames', [{}])
            hostname = hostnames[0].get('name', '') if hostnames else ''
            hostname_type = hostnames[0].get('type', '') if hostnames else ''
            
            for protocol in ['tcp', 'udp', 'ip', 'sctp']:
                if protocol in self._scan_result['scan'][host]:
                    for port, port_info in self._scan_result['scan'][host][protocol].items():
                        writer.writerow([
                            host,
                            hostname,
                            hostname_type,
                            protocol,
                            port,
                            port_info.get('name', ''),
                            port_info.get('state', ''),
                            port_info.get('product', ''),
                            port_info.get('extrainfo', ''),
                            port_info.get('reason', ''),
                            port_info.get('version', ''),
                            port_info.get('conf', ''),
                            port_info.get('cpe', '')
                        ])
        
        return output.getvalue()
    
    def all_hosts(self) -> List[str]:
        """Get all scanned hosts"""
        return list(self._scan_result.get('scan', {}).keys())
    
    def has_host(self, host: str) -> bool:
        """Check if host exists in scan results"""
        return host in self._scan_result.get('scan', {})
    
    def scaninfo(self) -> Dict[str, Any]:
        """Get scan information"""
        return self._scan_result.get('nmap', {}).get('scaninfo', {})
    
    def scanstats(self) -> Dict[str, Any]:
        """Get scan statistics"""
        return self._scan_result.get('nmap', {}).get('scanstats', {})
    
    def command_line(self) -> str:
        """Get the nmap command line used"""
        return self._scan_result.get('nmap', {}).get('command_line', '')
    
    def nmap_version(self) -> Tuple[int, int]:
        """Get nmap version"""
        return self._nmap_version_number
    
    def __getitem__(self, host: str):
        """Dictionary-like access to scan results for backward compatibility"""
        if host not in self._scan_result.get('scan', {}):
            raise KeyError(f"Host {host} not found in scan results")
        
        # Create a dynamic class that behaves like PortScannerHostDict
        class HostDict(dict):
            def __init__(self, scan_result, host):
                super().__init__(scan_result.get('scan', {}).get(host, {}))
                self._scan_result = scan_result
                self._host = host
            
            def hostnames(self):
                hostnames_list = self.get('hostnames', [])
                return [hn.get('name', '') for hn in hostnames_list if hn.get('name')]
            
            def hostname(self):
                hostnames = self.hostnames()
                return hostnames[0] if hostnames else ''
            
            def state(self):
                return self.get('status', {}).get('state', 'unknown')
            
            def all_tcp(self):
                return self.get('tcp', {})
            
            def all_udp(self):
                return self.get('udp', {})
            
            def has_tcp(self, port):
                return port in self.get('tcp', {})
            
            def tcp(self, port):
                return self.get('tcp', {}).get(port, {})
        
        return HostDict(self._scan_result, host)
    
    def __contains__(self, host: str) -> bool:
        """Check if host exists in scan results"""
        return self.has_host(host)
    
    def keys(self):
        """Get all host keys"""
        return self._scan_result.get('scan', {}).keys()
    
    def items(self):
        """Get all host items as (host, PortScannerHostDict) pairs"""
        for host in self._scan_result.get('scan', {}):
            yield host, PortScannerHostDict(self._scan_result, host)
    
    # =================================================================
    # DIRECT API METHODS FOR ALL NMAP FEATURES
    # =================================================================
    
    # HOST DISCOVERY METHODS
    def ping_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """Ping scan (-sn) - Host discovery only"""
        return self.scan(hosts=hosts, arguments="-sn", **kwargs)
    
    def list_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """List scan (-sL) - List targets without scanning"""
        return self.scan(hosts=hosts, arguments="-sL", **kwargs)
    
    def no_ping_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Skip host discovery (-Pn)"""
        args = "-Pn"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def icmp_ping_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """ICMP ping scan (-PE)"""
        return self.scan(hosts=hosts, arguments="-PE", **kwargs)
    
    def tcp_ping_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP ping scan (-PS)"""
        args = f"-PS{ports}" if ports else "-PS"
        return self.scan(hosts=hosts, arguments=args, **kwargs)
    
    def ack_ping_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP ACK ping scan (-PA)"""
        args = f"-PA{ports}" if ports else "-PA"
        return self.scan(hosts=hosts, arguments=args, **kwargs)
    
    def udp_ping_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """UDP ping scan (-PU)"""
        args = f"-PU{ports}" if ports else "-PU"
        return self.scan(hosts=hosts, arguments=args, **kwargs)
    
    # SCAN TYPE METHODS
    def syn_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP SYN scan (-sS) - Default scan"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sS", **kwargs)
    
    def connect_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP connect scan (-sT)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sT", **kwargs)
    
    def ack_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP ACK scan (-sA) - Firewall detection"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sA", **kwargs)
    
    def window_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP Window scan (-sW)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sW", **kwargs)
    
    def maimon_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """TCP Maimon scan (-sM)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sM", **kwargs)
    
    def udp_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """UDP scan (-sU)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sU", **kwargs)
    
    def null_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """NULL scan (-sN) - Stealth scan"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sN", **kwargs)
    
    def fin_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """FIN scan (-sF) - Stealth scan"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sF", **kwargs)
    
    def xmas_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Xmas scan (-sX) - Stealth scan"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sX", **kwargs)
    
    def idle_scan(self, hosts: str, zombie_host: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Idle scan (-sI) - Ultra stealth"""
        args = f"-sI {zombie_host}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def sctp_init_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """SCTP INIT scan (-sY)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sY", **kwargs)
    
    def sctp_cookie_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """SCTP COOKIE scan (-sZ)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-sZ", **kwargs)
    
    def ip_protocol_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """IP protocol scan (-sO)"""
        return self.scan(hosts=hosts, arguments="-sO", **kwargs)
    
    # SERVICE AND VERSION DETECTION
    def version_scan(self, hosts: str, ports: Optional[str] = None, intensity: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Service version detection (-sV)"""
        args = "-sV"
        if intensity is not None:
            args += f" --version-intensity {intensity}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def aggressive_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Aggressive scan (-A) - OS detection, version detection, script scanning, and traceroute"""
        return self.scan(hosts=hosts, ports=ports, arguments="-A", **kwargs)
    
    # OS DETECTION
    def os_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """OS detection (-O)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-O", **kwargs)
    
    def os_scan_aggressive(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Aggressive OS detection (-O --osscan-guess)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-O --osscan-guess", **kwargs)
    
    # NSE SCRIPT SCANNING
    def script_scan(self, hosts: str, scripts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """NSE script scan (--script)"""
        args = f"--script {scripts}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def vuln_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Vulnerability scan (--script vuln)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--script vuln", **kwargs)
    
    def auth_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Authentication scan (--script auth)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--script auth", **kwargs)
    
    def safe_scripts_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Safe scripts scan (--script safe)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--script safe", **kwargs)
    
    def intrusive_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Intrusive script scan (--script intrusive)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--script intrusive", **kwargs)
    
    def malware_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Malware detection scan (--script malware)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--script malware", **kwargs)
    
    # FIREWALL EVASION
    def fragment_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Fragment packets (-f)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-f", **kwargs)
    
    def decoy_scan(self, hosts: str, decoys: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Decoy scan (-D)"""
        args = f"-D {decoys}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def spoof_source_scan(self, hosts: str, source_ip: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Spoof source IP (-S)"""
        args = f"-S {source_ip}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def spoof_mac_scan(self, hosts: str, mac_address: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Spoof MAC address (--spoof-mac)"""
        args = f"--spoof-mac {mac_address}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def data_length_scan(self, hosts: str, length: int, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Append random data (--data-length)"""
        args = f"--data-length {length}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    # TIMING AND PERFORMANCE
    def timing_scan(self, hosts: str, timing: int, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Set timing template (-T0 to -T5)"""
        if not 0 <= timing <= 5:
            raise PortScannerError("Timing must be between 0 and 5")
        args = f"-T{timing}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def fast_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Fast scan (-T4 -F)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-T4 -F", **kwargs)
    
    def slow_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Slow scan (-T1)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-T1", **kwargs)
    
    # IPv6 SUPPORT
    def ipv6_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """IPv6 scan (-6)"""
        return self.scan(hosts=hosts, ports=ports, arguments="-6", **kwargs)
    
    # TRACEROUTE
    def traceroute_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Traceroute scan (--traceroute)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--traceroute", **kwargs)
    
    # PORT SPECIFICATION METHODS
    def top_ports_scan(self, hosts: str, count: int, **kwargs) -> Dict[str, Any]:
        """Scan top N ports (--top-ports)"""
        args = f"--top-ports {count}"
        return self.scan(hosts=hosts, arguments=args, **kwargs)
    
    def port_ratio_scan(self, hosts: str, ratio: float, **kwargs) -> Dict[str, Any]:
        """Scan ports by ratio (--port-ratio)"""
        args = f"--port-ratio {ratio}"
        return self.scan(hosts=hosts, arguments=args, **kwargs)
    
    # ADVANCED SCAN OPTIONS
    def source_port_scan(self, hosts: str, source_port: int, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Use specific source port (--source-port)"""
        args = f"--source-port {source_port}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def interface_scan(self, hosts: str, interface: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Use specific interface (-e)"""
        args = f"-e {interface}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def mtu_discovery_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Path MTU discovery (--mtu-disc)"""
        return self.scan(hosts=hosts, ports=ports, arguments="--mtu-disc", **kwargs)
    
    # =================================================================
    # ENHANCED FEATURE METHODS (CACHING AND PERFORMANCE)
    # =================================================================
    
    def enable_caching(self, enabled: bool = True, max_age: int = 300) -> None:
        """Enable/disable result caching"""
        self._enable_caching = enabled
        global _cache_max_age
        _cache_max_age = max_age
        logger.debug(f"Caching {'enabled' if enabled else 'disabled'} with max_age={max_age}s")
    
    def clear_cache(self) -> None:
        """Clear scan result cache"""
        global _scan_cache
        with _scan_lock:
            _scan_cache.clear()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics from last scan"""
        return self._performance_stats.copy()
    
    def scan_with_evasion(
        self,
        hosts: str,
        ports: Optional[str] = None,
        profile: EvasionProfile = EvasionProfile.STEALTH,
        additional_args: str = ""
    ) -> Dict[str, Any]:
        """Convenience method for evasion scanning"""
        return self.scan(
            hosts=hosts,
            ports=ports,
            arguments=additional_args,
            evasion_profile=profile
        )
    
    # =================================================================
    # OUTPUT FORMAT METHODS
    # =================================================================
    
    def scan_to_xml(self, hosts: str, filename: str, ports: Optional[str] = None, arguments: str = "-sV", **kwargs) -> Dict[str, Any]:
        """Scan and save results to XML file"""
        args = f"{arguments} -oX {filename}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def scan_to_normal(self, hosts: str, filename: str, ports: Optional[str] = None, arguments: str = "-sV", **kwargs) -> Dict[str, Any]:
        """Scan and save results to normal text file"""
        args = f"{arguments} -oN {filename}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def scan_to_grepable(self, hosts: str, filename: str, ports: Optional[str] = None, arguments: str = "-sV", **kwargs) -> Dict[str, Any]:
        """Scan and save results to grepable format"""
        args = f"{arguments} -oG {filename}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    def scan_to_all_formats(self, hosts: str, basename: str, ports: Optional[str] = None, arguments: str = "-sV", **kwargs) -> Dict[str, Any]:
        """Scan and save results to all formats"""
        args = f"{arguments} -oA {basename}"
        return self.scan(hosts=hosts, ports=ports, arguments=args, **kwargs)
    
    # =================================================================
    # SPECIALIZED SCANNING METHODS
    # =================================================================
    
    def web_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """Web application scan focusing on HTTP/HTTPS ports"""
        web_ports = "80,443,8080,8443,8000,8888,3000,5000,9000"
        return self.script_scan(hosts=hosts, scripts="http-*", ports=web_ports, **kwargs)
    
    def database_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """Database service scan"""
        db_ports = "1433,1521,3306,5432,27017,6379,11211"
        return self.version_scan(hosts=hosts, ports=db_ports, **kwargs)
    
    def smb_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """SMB/NetBIOS scan"""
        smb_ports = "139,445"
        return self.script_scan(hosts=hosts, scripts="smb-*", ports=smb_ports, **kwargs)
    
    def ssh_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """SSH service scan"""
        return self.script_scan(hosts=hosts, scripts="ssh-*", ports="22", **kwargs)
    
    def dns_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """DNS service scan"""
        return self.script_scan(hosts=hosts, scripts="dns-*", ports="53", **kwargs)
    
    def mail_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """Mail service scan (SMTP, POP3, IMAP)"""
        mail_ports = "25,110,143,993,995,587"
        return self.script_scan(hosts=hosts, scripts="smtp-*,pop3-*,imap-*", ports=mail_ports, **kwargs)
    
    def ftp_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """FTP service scan"""
        return self.script_scan(hosts=hosts, scripts="ftp-*", ports="21", **kwargs)
    
    def snmp_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """SNMP scan"""
        return self.script_scan(hosts=hosts, scripts="snmp-*", ports="161", **kwargs)
    
    # =================================================================
    # NETWORK DISCOVERY METHODS
    # =================================================================
    
    def network_discovery(self, network: str, **kwargs) -> Dict[str, Any]:
        """Comprehensive network discovery"""
        return self.scan(hosts=network, arguments="-sn -PE -PP -PM -PS21,22,23,25,53,80,110,111,135,139,143,443,993,995,1723,3389,5900", **kwargs)
    
    def broadcast_discovery(self, **kwargs) -> Dict[str, Any]:
        """Broadcast-based host discovery"""
        return self.script_scan(hosts="", scripts="broadcast-*", **kwargs)
    
    def dhcp_discovery(self, interface: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """DHCP discovery scan"""
        args = "--script broadcast-dhcp-discover"
        if interface:
            args += f" -e {interface}"
        return self.scan(hosts="", arguments=args, **kwargs)
    
    # =================================================================
    # SECURITY TESTING METHODS
    # =================================================================
    
    def brute_force_scan(self, hosts: str, service: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Brute force authentication scan"""
        script = f"{service}-brute"
        return self.script_scan(hosts=hosts, scripts=script, ports=ports, **kwargs)
    
    def ssl_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """SSL/TLS security scan"""
        ssl_ports = ports or "443,993,995,8443"
        return self.script_scan(hosts=hosts, scripts="ssl-*,tls-*", ports=ssl_ports, **kwargs)
    
    def rpc_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """RPC service enumeration"""
        return self.script_scan(hosts=hosts, scripts="rpc-*", ports="111,135", **kwargs)
    
    def nfs_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """NFS share enumeration"""
        return self.script_scan(hosts=hosts, scripts="nfs-*", ports="2049", **kwargs)
    
    # =================================================================
    # ADVANCED EVASION METHODS
    # =================================================================
    
    def advanced_evasion_scan(
        self,
        hosts: str,
        ports: Optional[str] = None,
        fragment: bool = True,
        decoys: Optional[str] = None,
        spoof_mac: bool = True,
        random_hosts: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Advanced evasion scan with multiple techniques"""
        args = []
        
        if fragment:
            args.append("-f")
        
        if decoys:
            args.append(f"-D {decoys}")
        elif fragment:  # Auto-generate decoys if not provided
            args.append("-D RND:10")
        
        if spoof_mac:
            args.append("--spoof-mac 0")
        
        if random_hosts:
            args.append("--randomize-hosts")
        
        # Use slow timing
        args.append("-T1")
        
        return self.scan(hosts=hosts, ports=ports, arguments=" ".join(args), **kwargs)
    
    def firewall_test_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Test firewall rules and filtering"""
        # Combine different scan types to test firewall behavior
        results = {}
        
        # TCP ACK scan to detect filtering
        ack_result = self.ack_scan(hosts, ports, **kwargs)
        results['ack_scan'] = ack_result
        
        # TCP SYN scan for comparison
        syn_result = self.syn_scan(hosts, ports, **kwargs)
        results['syn_scan'] = syn_result
        
        # Window scan for additional firewall detection
        window_result = self.window_scan(hosts, ports, **kwargs)
        results['window_scan'] = window_result
        
        return results
    
    # =================================================================
    # PERFORMANCE OPTIMIZATION METHODS
    # =================================================================
    
    def parallel_scan(
        self,
        hosts: str,
        ports: Optional[str] = None,
        max_workers: int = 10,
        arguments: str = "-sV",
        **kwargs
    ) -> Dict[str, Any]:
        """Parallel scanning for improved performance"""
        if '/' not in hosts and '-' not in hosts and ',' not in hosts:
            # Single host, no need for parallelization
            return self.scan(hosts=hosts, ports=ports, arguments=arguments, **kwargs)
        
        # Expand hosts and create chunks
        scanner_yield = PortScannerYield()
        host_list = scanner_yield._expand_hosts(hosts)
        
        # Split into chunks for parallel processing
        chunk_size = max(1, len(host_list) // max_workers)
        host_chunks = [host_list[i:i + chunk_size] for i in range(0, len(host_list), chunk_size)]
        
        combined_results = {'scan': {}, 'nmap': {}}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_chunk = {
                executor.submit(self.scan, ','.join(chunk), ports, arguments, **kwargs): chunk
                for chunk in host_chunks if chunk
            }
            
            for future in as_completed(future_to_chunk):
                try:
                    result = future.result()
                    # Merge results
                    combined_results['scan'].update(result.get('scan', {}))
                    if not combined_results['nmap'] and 'nmap' in result:
                        combined_results['nmap'] = result['nmap']
                except Exception as e:
                    logger.error(f"Parallel scan chunk failed: {e}")
        
        return combined_results
    
    def adaptive_timing_scan(self, hosts: str, ports: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Adaptive timing based on target responsiveness"""
        # Start with T3 (normal), adjust based on response
        try:
            # Quick test with T3
            test_result = self.timing_scan(hosts, 3, "22,80,443", timeout=30, **kwargs)
            
            # If successful and fast, use T4
            if test_result and 'scan' in test_result:
                return self.timing_scan(hosts, 4, ports, **kwargs)
            else:
                # If slow or no response, use T2
                return self.timing_scan(hosts, 2, ports, **kwargs)
                
        except PortScannerTimeout:
            # Target is slow, use T1
            return self.timing_scan(hosts, 1, ports, **kwargs)
        except Exception:
            # Default to T2 for unknown issues
            return self.timing_scan(hosts, 2, ports, **kwargs)
    
    # =================================================================
    # COMPLIANCE AND AUDIT METHODS
    # =================================================================
    
    def compliance_scan(self, hosts: str, standard: str = "pci", **kwargs) -> Dict[str, Any]:
        """Security compliance scanning"""
        if standard.lower() == "pci":
            # PCI DSS compliance check
            return self.script_scan(hosts=hosts, scripts="ssl-cert,ssl-enum-ciphers,http-security-headers", **kwargs)
        elif standard.lower() == "hipaa":
            # HIPAA compliance check
            return self.script_scan(hosts=hosts, scripts="ssl-*,http-security-headers,smb-security-mode", **kwargs)
        else:
            # Generic security scan
            return self.vuln_scan(hosts=hosts, **kwargs)
    
    def audit_scan(self, hosts: str, **kwargs) -> Dict[str, Any]:
        """Comprehensive security audit scan"""
        return self.script_scan(hosts=hosts, scripts="vuln,auth,safe", **kwargs)
    
    # =================================================================
    # REPORTING AND ANALYSIS METHODS
    # =================================================================
    
    def generate_report(self, format_type: str = "json") -> str:
        """Generate formatted report from last scan results"""
        if not self._scan_result:
            return ""
        
        if format_type.lower() == "json":
            return json.dumps(self._scan_result, indent=2, default=str)
        elif format_type.lower() == "csv":
            return self.csv()
        elif format_type.lower() == "xml":
            return self._generate_xml_report()
        else:
            return str(self._scan_result)
    
    def _generate_xml_report(self) -> str:
        """Generate XML report from scan results"""
        # Create basic XML structure
        root = ET.Element("nmaprun")
        
        # Add scan info
        if 'nmap' in self._scan_result:
            scaninfo = ET.SubElement(root, "scaninfo")
            for key, value in self._scan_result['nmap'].get('scaninfo', {}).items():
                scaninfo.set(key, str(value))
        
        # Add hosts
        for host_ip, host_data in self._scan_result.get('scan', {}).items():
            host_elem = ET.SubElement(root, "host")
            
            # Add address
            addr_elem = ET.SubElement(host_elem, "address")
            addr_elem.set("addr", host_ip)
            addr_elem.set("addrtype", "ipv4")
            
            # Add status
            status_elem = ET.SubElement(host_elem, "status")
            status_info = host_data.get('status', {})
            for key, value in status_info.items():
                status_elem.set(key, str(value))
            
            # Add ports
            ports_elem = ET.SubElement(host_elem, "ports")
            for protocol in ['tcp', 'udp', 'sctp']:
                if protocol in host_data:
                    for port_num, port_info in host_data[protocol].items():
                        port_elem = ET.SubElement(ports_elem, "port")
                        port_elem.set("protocol", protocol)
                        port_elem.set("portid", str(port_num))
                        
                        # Add port state
                        state_elem = ET.SubElement(port_elem, "state")
                        state_elem.set("state", port_info.get('state', ''))
                        state_elem.set("reason", port_info.get('reason', ''))
        
        return ET.tostring(root, encoding='unicode')
    
    def _validate_host_specification(self, hosts: str) -> bool:
        """Comprehensive host specification validation"""
        if not hosts or not hosts.strip():
            raise PortScannerError("Host specification cannot be empty")
        
        hosts = hosts.strip()
        
        # Split by comma to handle multiple hosts
        host_parts = [h.strip() for h in hosts.split(',')]
        
        for host_spec in host_parts:
            if not host_spec:
                continue
                
            # Check for CIDR notation
            if '/' in host_spec:
                try:
                    ipaddress.ip_network(host_spec, strict=False)
                    continue
                except ValueError:
                    pass
            
            # Check for IP range notation
            if '-' in host_spec and '.' in host_spec:
                try:
                    base, range_part = host_spec.rsplit('.', 1)
                    if '-' in range_part:
                        start, end = range_part.split('-', 1)
                        start_num, end_num = int(start), int(end)
                        if not (0 <= start_num <= 255 and 0 <= end_num <= 255 and start_num <= end_num):
                            raise PortScannerError(f"Invalid IP range in host specification: {host_spec}")
                        # Validate base IP
                        base_parts = base.split('.')
                        if len(base_parts) != 3 or not all(0 <= int(part) <= 255 for part in base_parts):
                            raise PortScannerError(f"Invalid IP base in range specification: {host_spec}")
                        continue
                except (ValueError, IndexError):
                    pass
            
            # Check for single IP address
            try:
                ipaddress.ip_address(host_spec)
                continue
            except ValueError:
                pass
            
            # Check for hostname (basic validation)
            if re.match(r'^[a-zA-Z0-9.-]+$', host_spec) and not host_spec.startswith('.') and not host_spec.endswith('.'):
                continue
            
            # If none of the above, it's invalid
            raise PortScannerError(f"Invalid host specification: {host_spec}")
        
        return True

    def _validate_port_specification(self, ports: Optional[str]) -> bool:
        """Comprehensive port specification validation"""
        if ports is None or not ports.strip():
            return True  # No ports specified is valid
        
        ports = ports.strip()
        
        # Split by comma to handle multiple port specs
        port_parts = [p.strip() for p in ports.split(',')]
        
        for port_spec in port_parts:
            if not port_spec:
                continue
            
            # Check for port range
            if '-' in port_spec:
                try:
                    start, end = port_spec.split('-', 1)
                    start_num, end_num = int(start), int(end)
                    if not (1 <= start_num <= 65535 and 1 <= end_num <= 65535 and start_num <= end_num):
                        raise PortScannerError(f"Invalid port range: {port_spec}")
                except ValueError:
                    raise PortScannerError(f"Invalid port range format: {port_spec}")
                continue
            
            # Check for single port
            try:
                port_num = int(port_spec)
                if not (1 <= port_num <= 65535):
                    raise PortScannerError(f"Port number out of range (1-65535): {port_num}")
            except ValueError:
                raise PortScannerError(f"Invalid port specification: {port_spec}")
        
        return True

    def _validate_nmap_arguments(self, arguments: str) -> bool:
        """Validate nmap arguments for security and correctness"""
        if not arguments:
            return True
        
        # Dangerous arguments to block
        dangerous_patterns = [
            r'--script.*\.\.',  # Directory traversal in scripts
            r'-oN\s+/dev/',     # Writing to device files
            r'-oX\s+/dev/',     # Writing to device files
            r'-oG\s+/dev/',     # Writing to device files
            r'[;&|`$]',         # Shell injection characters
            r'--resume.*\.\.',  # Directory traversal in resume
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, arguments, re.IGNORECASE):
                raise PortScannerError(f"Potentially dangerous argument detected: {arguments}")
        
        # Check for conflicting scan types
        scan_type_args = ['-sS', '-sT', '-sA', '-sW', '-sM', '-sU', '-sN', '-sF', '-sX', '-sO', '-sY', '-sZ']
        found_scan_types = [arg for arg in scan_type_args if arg in arguments]
        if len(found_scan_types) > 1:
            logger.warning(f"Multiple scan types detected: {found_scan_types}. Nmap will use the last one.")
        
        return True

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for output operations"""
        if not filename:
            raise PortScannerError("Filename cannot be empty")
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
        
        # Ensure not too long
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        # Ensure not empty after sanitization
        if not sanitized or sanitized.isspace():
            raise PortScannerError("Filename becomes empty after sanitization")
        
        return sanitized

    def _check_nmap_requirements(self, arguments: str, sudo: bool) -> None:
        """Check if nmap requirements are met for the given arguments"""
        # Check for privileged operations
        privileged_operations = [
            '-sS', '-sF', '-sN', '-sX', '-sO', '-sY', '-sZ',  # Raw socket scans
            '--traceroute',  # Usually requires privileges
            '-O',  # OS detection
        ]
        
        needs_privilege = any(op in arguments for op in privileged_operations)
        
        if needs_privilege and not sudo and not sys.platform.startswith('win'):
            logger.warning(
                "Scan may require root privileges. Consider using sudo=True or running as root."
            )
        
        # Check nmap version compatibility
        if self._nmap_version_number < (7, 0):
            unsupported_features = []
            
            # Features requiring newer nmap versions
            if '--script' in arguments and 'ssl-cert' in arguments:
                unsupported_features.append('ssl-cert script')
            
            if unsupported_features:
                logger.warning(f"Features may not be supported in nmap {'.'.join(map(str, self._nmap_version_number))}: {', '.join(unsupported_features)}")

    def _validate_scan_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean scan results"""
        if not isinstance(result, dict):
            raise PortScannerError("Invalid scan result format")
        
        # Ensure required structure exists
        if 'scan' not in result:
            result['scan'] = {}
        
        if 'nmap' not in result:
            result['nmap'] = {'command_line': '', 'scaninfo': {}, 'scanstats': {}}
        
        # Validate host data structure
        for host, host_data in result.get('scan', {}).items():
            if not isinstance(host_data, dict):
                logger.warning(f"Invalid host data for {host}, skipping")
                continue
            
            # Ensure required protocol dictionaries exist
            for protocol in ['tcp', 'udp', 'ip', 'sctp']:
                if protocol not in host_data:
                    host_data[protocol] = {}
                elif not isinstance(host_data[protocol], dict):
                    logger.warning(f"Invalid {protocol} data for {host}, resetting")
                    host_data[protocol] = {}
        
        return result

    def _get_resource_limits(self) -> Dict[str, Any]:
        """Get current resource limits and constraints"""
        limits = {
            'max_memory_mb': 1024,  # Default 1GB limit
            'max_scan_duration': 3600,  # Default 1 hour
            'max_concurrent_scans': 10,  # Default max concurrent
            'max_hosts_per_scan': 1000,  # Default max hosts
        }
        
        # Try to get system memory info
        if PSUTIL_AVAILABLE and psutil is not None:
            try:
                memory = psutil.virtual_memory()
                # Use up to 25% of available memory
                limits['max_memory_mb'] = int(memory.available / (1024 * 1024) * 0.25)
            except Exception:
                # psutil import failed at runtime
                logger.debug("psutil failed at runtime, using default memory limits")
        else:
            logger.debug("psutil not available, using default memory limits")
        
        return limits

    def _monitor_resource_usage(self, start_time: float, max_duration: int) -> None:
        """Monitor resource usage during scan"""
        current_time = time.time()
        elapsed = current_time - start_time
        
        if elapsed > max_duration:
            raise PortScannerTimeout(f"Scan exceeded maximum duration of {max_duration} seconds")
        
        # Check memory usage if psutil is available
        if PSUTIL_AVAILABLE and psutil is not None:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                limits = self._get_resource_limits()
                
                if memory_mb > limits['max_memory_mb']:
                    logger.warning(f"High memory usage detected: {memory_mb:.1f}MB")
            except Exception:
                # psutil failed at runtime
                logger.debug("psutil failed at runtime, skipping memory monitoring")
        else:
            logger.debug("psutil not available, skipping memory monitoring")

    def _create_secure_temp_file(self, suffix: str = '.xml') -> str:
        """Create a secure temporary file for scan output"""
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix='nmap_scan_')
            os.close(fd)  # Close the file descriptor, we just need the path
            
            # Set restrictive permissions (owner only)
            os.chmod(temp_path, 0o600)
            
            return temp_path
        except OSError as e:
            raise PortScannerError(f"Failed to create temporary file: {e}")

    def _cleanup_temp_files(self, temp_files: List[str]) -> None:
        """Clean up temporary files securely"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    # Overwrite file content before deletion for security
                    with open(temp_file, 'w') as f:
                        f.write('0' * 1024)  # Overwrite with zeros
                    os.remove(temp_file)
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
            except OSError as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
    
    def vulnerability_summary(self) -> Dict[str, List[str]]:
        """Extract vulnerability information from script results"""
        vulnerabilities = {'high': [], 'medium': [], 'low': [], 'info': []}
        
        for host_ip, host_data in self._scan_result.get('scan', {}).items():
            for protocol in ['tcp', 'udp', 'sctp']:
                if protocol in host_data:
                    for port_num, port_info in host_data[protocol].items():
                        scripts = port_info.get('script', {})
                        for script_name, script_output in scripts.items():
                            if 'vuln' in script_name.lower():
                                # Simple categorization based on keywords
                                output_lower = script_output.lower()
                                vuln_info = f"{host_ip}:{port_num} - {script_name}"
                                
                                if any(keyword in output_lower for keyword in ['critical', 'severe', 'high']):
                                    vulnerabilities['high'].append(vuln_info)
                                elif any(keyword in output_lower for keyword in ['medium', 'moderate']):
                                    vulnerabilities['medium'].append(vuln_info)
                                elif any(keyword in output_lower for keyword in ['low', 'minor']):
                                    vulnerabilities['low'].append(vuln_info)
                                else:
                                    vulnerabilities['info'].append(vuln_info)
        
        return vulnerabilities

# =====================================================================
# ASYNC SCANNER CLASS
# =====================================================================

class PortScannerAsync:
    """
    Asynchronous port scanner with enhanced capabilities.
    Built into the original API without "Enhanced" naming.
    """
    
    def __init__(self):
        self._processes: List[Process] = []
        self._lock = threading.Lock()
    
    def scan(
        self,
        hosts: str,
        ports: Optional[str] = None,
        arguments: str = "-sV",
        callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        sudo: bool = False,
        timeout: Optional[int] = None
    ) -> None:
        """
        Asynchronous scan with callback support.
        
        Args:
            hosts: Host(s) to scan
            ports: Port specification
            arguments: Nmap arguments
            callback: Callback function for results
            sudo: Use sudo
            timeout: Scan timeout
        """
        if callback is None:
            raise PortScannerError("Callback function is required for async scan")
        
        def scan_progressive(hosts: str, ports: Optional[str], arguments: str, callback: Callable[[str, Dict[str, Any]], None], sudo: bool) -> None:
            scanner = PortScanner()
            try:
                result = scanner.scan(hosts, ports, arguments, sudo, timeout)
                for host in result.get('scan', {}):
                    callback(host, result)
            except Exception as e:
                logger.error(f"Async scan failed: {e}")
        
        process = Process(
            target=scan_progressive,
            args=(hosts, ports, arguments, callback, sudo)
        )
        process.start()
        
        with self._lock:
            self._processes.append(process)
    
    def stop(self) -> None:
        """Stop all running async scans"""
        with self._lock:
            for process in self._processes:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=5)
                    if process.is_alive():
                        process.kill()
            self._processes.clear()
    
    def wait(self, timeout: Optional[float] = None) -> None:
        """Wait for all scans to complete"""
        with self._lock:
            for process in self._processes:
                process.join(timeout)
            self._processes = [p for p in self._processes if p.is_alive()]
    
    def still_scanning(self) -> bool:
        """Check if any scans are still running"""
        with self._lock:
            alive_processes = [p for p in self._processes if p.is_alive()]
            self._processes = alive_processes
            return len(alive_processes) > 0

# =====================================================================
# YIELD-BASED SCANNER
# =====================================================================

class PortScannerYield:
    """
    Memory-efficient scanner using yield for large networks.
    Enhanced internally without "Enhanced" naming.
    """
    
    def __init__(self):
        self._scanner = PortScanner()
    
    def scan(
        self,
        hosts: str,
        ports: Optional[str] = None,
        arguments: str = "-sV",
        sudo: bool = False,
        timeout: Optional[int] = None
    ) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
        """
        Yield scan results one host at a time for memory efficiency.
        
        Args:
            hosts: Host(s) to scan
            ports: Port specification
            arguments: Nmap arguments
            sudo: Use sudo
            timeout: Scan timeout
            
        Yields:
            Tuple of (host, scan_result) for each discovered host
        """
        try:
            # For single hosts, scan directly
            if '/' not in hosts and '-' not in hosts and ',' not in hosts:
                result = self._scanner.scan(hosts, ports, arguments, sudo, timeout)
                for host in result.get('scan', {}):
                    yield host, result
                return
            
            # For ranges/networks, expand and scan individually
            expanded_hosts = self._expand_hosts(hosts)
            
            for host in expanded_hosts:
                try:
                    result = self._scanner.scan(host, ports, arguments, sudo, timeout)
                    if result.get('scan'):
                        yield host, result
                except PortScannerError:
                    # Skip hosts that fail to scan
                    continue
                    
        except Exception as e:
            raise PortScannerError(f"Yield scan failed: {e}")
    
    def _expand_hosts(self, hosts: str) -> List[str]:
        """Expand host specifications into individual hosts"""
        expanded = []
        
        # Handle comma-separated hosts
        for host_spec in hosts.split(','):
            host_spec = host_spec.strip()
            
            # CIDR notation
            if '/' in host_spec:
                try:
                    network = ipaddress.ip_network(host_spec, strict=False)
                    expanded.extend([str(ip) for ip in network.hosts()])
                except ValueError:
                    expanded.append(host_spec)
            
            # Range notation (simple: 192.168.1.1-10)
            elif '-' in host_spec and '.' in host_spec:
                try:
                    base, range_part = host_spec.rsplit('.', 1)
                    if '-' in range_part:
                        start, end = range_part.split('-', 1)
                        for i in range(int(start), int(end) + 1):
                            expanded.append(f"{base}.{i}")
                    else:
                        expanded.append(host_spec)
                except (ValueError, AttributeError):
                    expanded.append(host_spec)
            
            else:
                expanded.append(host_spec)
        
        return expanded

# =====================================================================
# HOST DICTIONARY CLASS
# =====================================================================

class PortScannerHostDict(dict):
    """Enhanced host dictionary with convenience methods"""
    
    def __init__(self, scan_result: Dict[str, Any], host: str):
        super().__init__(scan_result.get('scan', {}).get(host, {}))
        self._scan_result = scan_result
        self._host = host
    
    def hostnames(self) -> List[str]:
        """Get all hostnames for this host"""
        hostnames_list = self.get('hostnames', [])
        return [hn.get('name', '') for hn in hostnames_list if hn.get('name')]
    
    def hostname(self) -> str:
        """Get primary hostname"""
        hostnames = self.hostnames()
        return hostnames[0] if hostnames else ''
    
    def state(self) -> str:
        """Get host state"""
        return self.get('status', {}).get('state', 'unknown')
    
    def uptime(self) -> str:
        """Get uptime if available"""
        return self.get('uptime', {}).get('seconds', '')
    
    def all_protocols(self) -> List[str]:
        """Get all protocols found"""
        return [proto for proto in ['tcp', 'udp', 'ip', 'sctp'] if proto in self]
    
    def all_tcp(self) -> Dict[int, Dict[str, Any]]:
        """Get all TCP ports"""
        return self.get('tcp', {})
    
    def all_udp(self) -> Dict[int, Dict[str, Any]]:
        """Get all UDP ports"""
        return self.get('udp', {})
    
    def all_ip(self) -> Dict[int, Dict[str, Any]]:
        """Get all IP protocols"""
        return self.get('ip', {})
    
    def all_sctp(self) -> Dict[int, Dict[str, Any]]:
        """Get all SCTP ports"""
        return self.get('sctp', {})
    
    def has_tcp(self, port: int) -> bool:
        """Check if TCP port exists"""
        return port in self.get('tcp', {})
    
    def has_udp(self, port: int) -> bool:
        """Check if UDP port exists"""
        return port in self.get('udp', {})
    
    def tcp(self, port: int) -> Dict[str, Any]:
        """Get TCP port info"""
        return self.get('tcp', {}).get(port, {})
    
    def udp(self, port: int) -> Dict[str, Any]:
        """Get UDP port info"""
        return self.get('udp', {}).get(port, {})

# =====================================================================
# EXCEPTION CLASSES
# =====================================================================

class PortScannerError(Exception):
    """Enhanced exception with context information"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()

class PortScannerTimeout(PortScannerError):
    """Exception for scan timeouts"""
    pass

# =====================================================================
# CONVENIENCE FUNCTIONS (ENHANCED)
# =====================================================================

def scan_stealth(
    hosts: str,
    ports: Optional[str] = None,
    arguments: str = ""
) -> Dict[str, Any]:
    """
    Convenience function for stealth scanning.
    Enhanced with built-in evasion without separate "enhanced" function.
    """
    scanner = PortScanner()
    return scanner.scan_with_evasion(
        hosts=hosts,
        ports=ports,
        profile=EvasionProfile.STEALTH,
        additional_args=arguments
    )

def scan_ghost(
    hosts: str,
    ports: Optional[str] = None,
    arguments: str = ""
) -> Dict[str, Any]:
    """
    Convenience function for ghost-mode scanning.
    Maximum stealth with all evasion techniques.
    """
    scanner = PortScanner()
    return scanner.scan_with_evasion(
        hosts=hosts,
        ports=ports,
        profile=EvasionProfile.GHOST,
        additional_args=arguments
    )

def scan_progressive(
    hosts: str,
    ports: Optional[str] = None,
    callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
) -> None:
    """Convenience function for progressive/async scanning"""
    if callback is None:
        raise PortScannerError("Callback required for progressive scan")
    
    scanner = PortScannerAsync()
    scanner.scan(hosts, ports, callback=callback)

# =====================================================================
# MODULE CONFIGURATION
# =====================================================================

def enable_performance_monitoring(enabled: bool = True) -> None:
    """Enable performance monitoring globally"""
    global _performance_monitoring
    _performance_monitoring = enabled

def set_cache_max_age(seconds: int) -> None:
    """Set global cache max age"""
    global _cache_max_age
    if seconds < 0:
        raise ValueError("Cache max age must be non-negative")
    _cache_max_age = seconds

def clear_global_cache() -> None:
    """Clear global scan cache"""
    global _scan_cache
    with _scan_lock:
        _scan_cache.clear()

# =====================================================================
# ALIASES FOR COMPATIBILITY
# =====================================================================

# Standard aliases (no "Enhanced" prefixes)
Scanner = PortScanner  # Modern alias
AsyncScanner = PortScannerAsync  # Async alias
YieldScanner = PortScannerYield  # Memory-efficient alias

# =====================================================================
# MODULE EXPORTS
# =====================================================================

__all__ = [
    # Core classes
    'PortScanner', 'PortScannerAsync', 'PortScannerYield', 'PortScannerHostDict',
    
    # Modern aliases
    'Scanner', 'AsyncScanner', 'YieldScanner',
    
    # Exceptions
    'PortScannerError', 'PortScannerTimeout',
    
    # Enums
    'EvasionProfile', 'ScanType',
    
    # Convenience functions
    'scan_stealth', 'scan_ghost', 'scan_progressive',
    
    # Configuration
    'enable_performance_monitoring', 'set_cache_max_age', 'clear_global_cache'
]
