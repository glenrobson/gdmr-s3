FROM nginx
COPY docker-files/default.conf /etc/nginx/conf.d
EXPOSE 80
