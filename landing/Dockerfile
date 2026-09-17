FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY privacy.html /usr/share/nginx/html/privacy.html
COPY terms.html /usr/share/nginx/html/terms.html
COPY og.png /usr/share/nginx/html/og.png
COPY robots.txt /usr/share/nginx/html/robots.txt
COPY sitemap.xml /usr/share/nginx/html/sitemap.xml
COPY llms.txt /usr/share/nginx/html/llms.txt

# The install script advertised on the homepage as
#   curl -fsSL https://zero.headless.com/install | bash
# It is served from this image so that URL always resolves. `install` is a copy of
# macapp/install-zero.sh placed here by landing/build.sh, because Docker can only
# read files inside the build context.
COPY install /usr/share/nginx/html/install

# Replace the default server block so /install is served as plain text. Without an
# extension nginx would default to application/octet-stream, which works fine for
# `curl | bash` but makes a browser download the file instead of showing it — and
# we explicitly invite people to read the script before running it.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
CMD ["nginx", "-g", "daemon off;"]
