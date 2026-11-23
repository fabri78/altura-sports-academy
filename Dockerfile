# Sirve el sitio estático con nginx (alternativa de despliegue del punto n: Docker)
FROM nginx:1.27-alpine
COPY index.html 404.html /usr/share/nginx/html/
COPY paginas /usr/share/nginx/html/paginas
COPY assets /usr/share/nginx/html/assets
EXPOSE 80
