#!/usr/bin/with-contenv bashio

bashio::log.info "Initializing GreenPulse Environment..."

# Initialize MariaDB if not exists
if [ ! -d "/data/mysql" ]; then
    bashio::log.info "Initializing MariaDB data directory..."
    mkdir -p /data/mysql
    chown -R mysql:mysql /data/mysql
    mysql_install_db --user=mysql --datadir=/data/mysql
fi

# Ensure permissions
chown -R mysql:mysql /data/mysql

# Create greenpulse user and grant permissions
bashio::log.info "Setting up database user..."
# Start temporary mysqld
/usr/bin/mysqld_safe --datadir=/data/mysql --user=mysql --skip-networking &
PID=$!

# Wait for it to be ready
bashio::log.info "Waiting for temporary MariaDB..."
for i in {1..30}; do
    if mysql -u root -e "SELECT 1" &> /dev/null; then
        break
    fi
    sleep 1
done

# Create user and database
bashio::log.info "Creating user and database..."
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS greenpulse;
CREATE USER IF NOT EXISTS 'greenpulse'@'%' IDENTIFIED BY 'greenpulse';
GRANT ALL PRIVILEGES ON *.* TO 'greenpulse'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

# Stop temporary mysqld
# Stop temporary mysqld
bashio::log.info "Stopping temporary MariaDB..."
mysqladmin -u root shutdown
wait $PID


# Configure phpMyAdmin (basic)
# We might need to generate a config.inc.php with a random blowfish secret
if [ ! -f "/var/www/localhost/htdocs/phpmyadmin/config.inc.php" ]; then
    bashio::log.info "Configuring phpMyAdmin..."
    cp /var/www/localhost/htdocs/phpmyadmin/config.sample.inc.php /var/www/localhost/htdocs/phpmyadmin/config.inc.php
    # Generate random secret
    SECRET=$(openssl rand -base64 32)
    sed -i "s/\$cfg\['blowfish_secret'\] = '';/\$cfg\['blowfish_secret'\] = '$SECRET';/" /var/www/localhost/htdocs/phpmyadmin/config.inc.php
    # Allow no password for root (for now, or set up a user)
    # Actually, we should probably set a root password for mysql or allow socket auth.
    # For simplicity in this addon, we might allow no password or set one.
fi

bashio::log.info "Initialization complete."
