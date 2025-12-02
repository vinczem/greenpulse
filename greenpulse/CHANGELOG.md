# Changelog

## [0.1.27]
Kényszerített öntözés logikája:
Mértékegység váltás: A beállításokban a force_watering_minutes helyett mostantól force_watering_amount van, ami mm-ben (liter/m²) várja az értéket. (A régi perc alapú beállítás törlődött).

Új logika:
A rendszer minden kalkulációnál megnézi, hogy történt-e már ma öntözés (akár kézi, akár automatikus).
Ha a "Kényszerített napi öntözés" be van kapcsolva, ÉS még nem volt ma öntözés:
Akkor mindenképpen javasolni fog locsolást.
Ha az időjárás indokolná a locsolást, és az több, mint a kényszerített mennyiség, akkor az időjárás alapú mennyiséget javasolja. (Indoklás: "Időjárás alapú öntözés (több mint a kényszerített X mm)")
Ha az időjárás nem indokolná, vagy kevesebbet indokolna, akkor a kényszerített mennyiséget javasolja. (Indoklás: "Kényszerített napi öntözés.")
Ha már volt ma öntözés, akkor a kényszerítés "kikapcsol" mára, és csak akkor javasol újabb locsolást, ha az időjárás miatt drasztikus vízhiány lépne fel (normál működés).

## [0.1.19] - 2025-12-02

### Fixed
- **Calculation**: Fixed unit conversion for ET0 calculation.

## [0.1.18] - 2025-12-02
Add three dynamic charts:
- Vízmérleg: Shows the water supply history.
- Időjárás trendek: Temperature and rain history.
- Vízforrás megoszlás: Rain vs. Irrigation ratio.

## [0.1.17] - 2025-12-02
### Added
- **Manual Watering History**: It now looks back 3 days (matching the weather history) for any manual watering events.
- This amount is added to the "Available Water" (Rendelkezésre álló víz).
- The dashboard will show this as "Öntözés (múlt)".

### Changed
- **Configuration**: `log_level` is now a dropdown selector in the Home Assistant Add-on configuration, making it easier to use.

## [0.1.16] 

## [0.1.15] 

## [0.1.14] 

## [0.1.13] 

## [0.1.12] 

## [0.1.11]

### Added
- **Configuration**: Added `shade_percentage` to the configuration schema.

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
