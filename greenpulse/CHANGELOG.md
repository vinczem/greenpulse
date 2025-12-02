# Changelog

## [0.1.10] - 2025-12-02


## [0.1.9] - 2025-12-02

### Changed
- **Configuration Keys**: Switched to simple English keys (slugs) for `grass_type` and `soil_type` to resolve Home Assistant UI issues.
    - Grass: `universal`, `sport`, `ornamental`, `drought`, `other`
    - Soil: `clay`, `sandy`, `loam`, `humus`, `unknown`
- **Documentation**: Updated the Dashboard to map these new keys to their Hungarian descriptions.

## [0.1.8] - 2025-12-02

### Fixed
- **Configuration Schema**: Reverted `log_level`, `grass_type`, and `soil_type` to use `list(...)` syntax as `selector` is not supported in Add-on configuration.
- **UI Formatting**: Added quotes to list options to ensure they are displayed correctly in the Home Assistant UI.

## [0.1.7] - 2025-12-02

### Added
- **Soil Type Logic**: The irrigation calculation now accounts for soil type.
    - Sandy soil (Homokos): Reduces effective water supply by 20%, triggering earlier watering.
    - Clay soil (Agyagos): Increases effective water supply by 20%, reducing watering frequency.
- **Documentation**: Added a section to the Dashboard explaining how Grass and Soil types affect the system.

### Changed
- **Configuration**: `log_level` is now a dropdown selector in the Home Assistant Add-on configuration, making it easier to use.
