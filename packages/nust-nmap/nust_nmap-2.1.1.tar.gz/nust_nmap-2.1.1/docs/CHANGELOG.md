# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.1.1] - 2025-07-10
- Dynamic versioning for pypi deployment

## [2.1.0] - 2025-07-10
## [2.0.0] - 2025-01-10

### Added
- Optimization & architecture recommendations documented in `todo.md` (performance, memory, validation, extensibility, code quality)
- Enhanced `.gitignore` for security, platform, and project-specific artifacts
- Streamlined `README.md` and created `README_PROGRAMMER_GUIDE.md` for technical reference
- Updated TODOs to reflect real gaps and future optimization opportunities
- Provided class-based, extensible design for evasion, port, and script profiles (prebuilt and user-defined)

### Enhanced
- Refined documentation structure for clarity and separation of concerns
- Provided detailed optimization patterns (LRU cache, streaming XML, async/thread pool, resource management, command builder, unified validation)
- Improved contextual error handling and input validation patterns

### Fixed
- Removed redundant and outdated documentation content
- Updated test and CI/CD requirements in TODOs

### Notes
- All changes follow the highest quality standards as defined in `.github/instructions/p.instructions.md`

### Added
- Production-grade Python nmap wrapper with comprehensive feature coverage
- Built-in firewall and IDS evasion capabilities with predefined profiles
- Asynchronous scanning support with callback-based result processing
- Memory-efficient yield-based scanning for large network ranges
- Intelligent caching system with TTL-based result storage
- Performance monitoring and statistics collection
- Complete type annotations with runtime validation
- Cross-platform nmap executable detection and path resolution
- Thread-safe operations with proper resource management
- Modern API aliases for improved developer experience

### Enhanced
- XML parsing engine with comprehensive host, port, and service data extraction
- Error handling with contextual exception hierarchy and recovery mechanisms
- Argument validation and safe parameter construction for nmap commands
- Process lifecycle management with automatic cleanup and termination safeguards
- Memory optimization for enterprise-scale network scanning operations

### Security
- Argument sanitization and validation to prevent command injection
- Safe parameter handling for all nmap command construction
- Built-in stealth scanning profiles for operational security requirements

## [1.0.0] - 2025-01-08

### Added
- Initial release of professional nmap Python wrapper
- Complete nmap feature coverage through argument passthrough
- Type-safe API with comprehensive annotations
- Cross-platform compatibility (Windows, macOS, Linux)
- Comprehensive XML output parsing
- Error handling and logging infrastructure
- Documentation and usage examples