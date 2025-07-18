FROM nginx:1.26

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
RUN groupmod -g 102 nginx && usermod -u 102 nginx
ENTRYPOINT ["nginx", "-g", "daemon off;"]








