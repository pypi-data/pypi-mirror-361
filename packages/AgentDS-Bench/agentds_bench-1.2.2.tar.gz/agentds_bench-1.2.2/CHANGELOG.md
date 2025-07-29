# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-01-27

### Compatibility
- **Backend Integration**: Compatible with Backend v1.8 that includes team_id in /auth/verify response
- **Complete Authentication Fix**: Full end-to-end solution for "Invalid team ID format" errors
  - Backend v1.8: Returns team_id in /auth/verify endpoint response  
  - Package v1.2.1: Captures and uses team_id for competition endpoints
- **Production Ready**: Complete package-backend compatibility for reliable authentication flow

### Technical Notes
- Works with Backend v1.8+ that includes `team_id` field in `/auth/verify` response
- Maintains backward compatibility with earlier backends (graceful fallback)
- No breaking changes to existing API or functionality

## [1.2.0] - 2025-01-27

### Fixed
- **Authentication Headers**: Fixed "Invalid team ID format" errors by properly managing X-Team-ID header
  - Removed hardcoded "placeholder" value from X-Team-ID header
  - Only send X-Team-ID header for `/api/competition/*` endpoints when real team ObjectId is available
  - Use basic headers (X-API-Key, X-Team-Name only) for `/api/submit` endpoint
  - Added endpoint-type parameter to `get_auth_headers()` function for proper header management
- **Improved API Reliability**: Enhanced authentication flow to prevent validation errors during task retrieval and submission

### Changed
- Modified `get_auth_headers()` function to accept `endpoint_type` parameter ("basic" or "competition")
- Updated all API calls to use appropriate header types based on endpoint requirements

### Technical Details
- `/api/submit` endpoint now uses basic authentication (no Team ID required)
- `/api/competition/*` endpoints attempt to retrieve and use real team ObjectId when available
- Automatic fallback mechanism for missing team IDs in competition endpoints

## [1.1.0] - 2025-01-27

### Removed
- **MongoDB Dependencies**: Eliminated all MongoDB-related functionality to support PVC-based dataset hosting
  - Removed `pymongo` dependency from requirements
  - Removed `load_dataset()` and `get_dataset_info()` methods from client
  - Removed MongoDB configuration from auth and client modules
- **Simplified Architecture**: Streamlined package for containerized environments where datasets are mounted as PVCs

### Changed
- Updated package description and documentation to reflect new architecture
- Modified client to work exclusively with API-based task retrieval and submission

## [1.0.2] - 2025-01-27

### Fixed
- **Package Content**: Fixed critical packaging issue where package contained only metadata
  - Corrected MANIFEST.in paths from `src/agentds/*` to `agentds/*`
  - Fixed pyproject.toml package-dir configuration  
  - Resolved license deprecation warnings
- **Package Size**: Package now includes actual source code (35.4 KB vs previous metadata-only)

### Added
- Complete source code now properly included in package distribution
- All client modules and examples now accessible after installation

## [1.0.1] - 2025-01-27

### Added
- Initial PyPI release with corrected packaging configuration

## [1.0.0] - 2025-01-27

### Added
- Initial release (metadata-only due to packaging issues, fixed in 1.0.2) 