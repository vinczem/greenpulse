# Changelog

## [0.1.39] - 2026-05-06

### Fixed
- **Dashboard Hotfix**: Jinja2 sablon hiba javítása a `Statisztika` oldalon, amit a folyamatos vízmérleg adatszerkezetének megváltozása okozott.

## [0.1.38] - 2026-05-06

### Changed
- **Folyamatos vízmérleg számítás**: A rendszer mostantól nem pillanatképeket készít a vízhiányról az előrejelzések alapján, hanem egy folyamatosan vezetett "bankszámlaként" kezeli azt.
  - A vízhiány minden órában növekszik az elmúlt óra párolgásával (ET).
  - A leesett csapadék és a végrehajtott öntözések valós mennyisége azonnal levonódik a hiányból.
  - A vízhiány értéke nem mehet 0 alá (a túltelített talajból a víz kifolyik/elszivárog).
- **Adatbázis bővítés**: Új `system_state` tábla a rendszer aktuális állapotának (vízhiány, utolsó kalkuláció ideje) tartós mentéséhez.

## [0.1.37] - 2026-05-05

### Changed
- **ET (Evapotranszspiráció) számítás finomítása**: A pillanatnyi időjárási adatok helyett a napi előrejelzés átlagaira (középhőmérséklet, átlagos páratartalom és szélsebesség) épül a párolgás becslése. Ez megszünteti a vízhiány értékének irreális esti ingadozását. A csapadék és öntözés levonása továbbra is valós időben történik.

### Added
- **Óránkénti vízhiány grafikon**: A Statisztika (analytics) oldalon megjelent egy új, órás bontású vonaldiagram, amelyen az öntözési küszöb is vízszintes vonallal van ábrázolva, így részletesen követhető a becsült vízhiány napközbeni alakulása.

## [0.1.35] - 2026-05-03

### Fixed
- **Starlette API kompatibilitás**: A `TemplateResponse` hívási formája frissítve Starlette 0.36+ kompatibilisre (`request` első argumentumként, nem a context dict-ben). Ez okozta a 500-as hibát az ingress betöltésekor.
- **requirements.txt**: `fastapi` és `starlette` verzió pinelve a jövőbeli API-változások elkerülésére.

## [0.1.34] - 2026-05-03

### Added
- **ET korrekciós szorzó** (`et_correction_factor`): Új konfigurációs opció, amely a becsült párolgás (ET) értékét skálázza.
  - Alapértelmezés: `1.0` (nincs korrekció)
  - Szeles, nyílt területen ajánlott: `1.2–1.5`
  - Árnyékos, védett területen: `0.7–0.9`
  - Ez lehetővé teszi, hogy a rendszer a helyi mikroklímához igazodjon, és a valóban tapasztalt fűszáradásra reagáljon.
- A dashboard részletes nézetben megjelenik az ET alap, a korrekciós szorzó, a szél hatása és a vízhiány küszöbhöz viszonyítva.

### Fixed
- **Statisztika (analytics) oldal**: Teljesen újraírt grafikonok.
  - Stacked bar chart a napi vízpótláshoz (csapadék + öntözés)
  - Dual-axis időjárás grafikon (hőmérséklet + csapadék)
  - Öntözési esemény histogram (csak öntözési napokat mutat)
  - Donut chart forrás-megoszláshoz
  - KPI összesítő sor (összes csapadék, öntözés, öntözési napok, átlag hőm.)
  - Robusztus null-kezelés és dátumrendezés

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
