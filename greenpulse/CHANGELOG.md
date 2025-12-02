# Changelog

## [0.1.7] - 2025-12-02

### Added
- **Soil Type Logic**: The irrigation calculation now accounts for soil type.
    - Sandy soil (Homokos): Reduces effective water supply by 20%, triggering earlier watering.
    - Clay soil (Agyagos): Increases effective water supply by 20%, reducing watering frequency.
- **Documentation**: Added a section to the Dashboard explaining how Grass and Soil types affect the system.

### Changed
- **Configuration**: `log_level` is now a dropdown selector in the Home Assistant Add-on configuration, making it easier to use.
