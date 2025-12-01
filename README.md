# GreenPulse Home Assistant Addon

Intelligent irrigation planner with OpenWeatherMap integration and local database.

## Installation

1.  Add this repository to your Home Assistant Add-on Store:
    `https://github.com/vinczem/greenpulse`
2.  Install the **GreenPulse** add-on.
3.  Configure the add-on (API key, coordinates, etc.).
4.  Start the add-on.

## Features

-   **Intelligent Irrigation Calculation**: Uses Penman-Monteith evapotranspiration method.
-   **Local Database**: Stores logs and weather history in a local MariaDB.
-   **Web Interface**: View dashboard, logs, and settings via Home Assistant Ingress.
-   **MQTT Integration**: Publishes irrigation commands and receives feedback.
