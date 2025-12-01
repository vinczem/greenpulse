ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
    py3-pip \
    mariadb \
    mariadb-client \
    phpmyadmin \
    php81-apache2 \
    php81-mysqli \
    php81-session \
    php81-json \
    php81-mbstring \
    apache2 \
    nginx

# Copy Python requirements
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy root filesystem
COPY rootfs /

# Copy application source
COPY src /app/src

# Setup phpMyAdmin
RUN \
    mkdir -p /run/apache2 \
    && ln -s /usr/share/webapps/phpmyadmin /var/www/localhost/htdocs/phpmyadmin \
    && sed -i 's/Listen 80/Listen 8081/g' /etc/apache2/httpd.conf

# Fix permissions
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
