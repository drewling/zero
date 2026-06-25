FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY og.png /usr/share/nginx/html/og.png
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
CMD ["nginx", "-g", "daemon off;"]
