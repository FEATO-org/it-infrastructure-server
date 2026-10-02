FROM nginx:1.30.5
LABEL org.opencontainers.image.source="https://github.com/FEATO-org/it-infrastructure-server"
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/http.d/public.conf /etc/nginx/conf.d/default.conf
COPY nginx/stream.d/minecraft.conf /etc/nginx/stream.conf
