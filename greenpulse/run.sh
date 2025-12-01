#!/usr/bin/with-contenv bashio

bashio::log.info "Starting GreenPulse Addon..."

# Start S6 services
# The base image handles S6 init if we don't override CMD, but we are overriding CMD to /run.sh
# Actually, HA base images use S6 as entrypoint. /run.sh is usually the main service or we can just let S6 handle it.
# If we want to use S6 for multiple services, we should rely on the base image's init.
# The base image ENTRYPOINT is "/init".
# So we should NOT have CMD ["/run.sh"] in Dockerfile if we want standard S6 behavior for services.d.
# BUT, standard HA addon pattern often uses a single run.sh.
# Since we want multi-process (mariadb + phpmyadmin + python), we MUST use S6.

# We will rely on the base image's /init to start services in /etc/services.d
# So this run.sh might just be a setup script that then execs into s6 or just exits if s6 is already running?
# Wait, if CMD is /run.sh, then /init is NOT running unless we call it.
# The HA base image has ENTRYPOINT ["/init"].
# If we define CMD ["/run.sh"], it executes /init /run.sh.
# S6 will start, run stage 2 (which runs /etc/services.d), and also run our CMD.
# But usually we want our CMD to BE one of the services or just setup.

# Let's make run.sh do setup and then block or exit?
# If we want S6 to manage services, we should put them in /etc/services.d.
# And run.sh can be used for one-time initialization (like config generation).

bashio::log.info "Initializing configuration..."

# Generate MariaDB config if needed
if [ ! -d "/data/mysql" ]; then
    bashio::log.info "Initializing MariaDB data directory..."
    mysql_install_db --user=root --datadir=/data/mysql
fi

# Generate phpMyAdmin config
# (Simplification: we might need to tweak config.inc.php)

bashio::log.info "Configuration complete. Services will be started by S6."

# If this script exits, the container might stop if it's the main CMD.
# But with S6, we usually want to keep running or let S6 handle services.
# If we use services.d, we don't strictly need a long-running run.sh.
# However, to keep it simple and ensure we see logs, we can just sleep or tail logs.
# BETTER APPROACH for HA Addons with S6:
# 1. Use /etc/services.d for long running daemons (mariadb, apache/phpmyadmin, python app).
# 2. Use /etc/cont-init.d for initialization (run.sh logic goes here).
# 3. Leave CMD empty or default.

# Refactoring plan:
# Move this logic to /etc/cont-init.d/00-greenpulse.sh
# Remove CMD from Dockerfile or set it to default.
