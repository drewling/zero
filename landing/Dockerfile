FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY privacy.html /usr/share/nginx/html/privacy.html
COPY terms.html /usr/share/nginx/html/terms.html
COPY og.png /usr/share/nginx/html/og.png
COPY robots.txt /usr/share/nginx/html/robots.txt
COPY sitemap.xml /usr/share/nginx/html/sitemap.xml
COPY llms.txt /usr/share/nginx/html/llms.txt
COPY assets /usr/share/nginx/html/assets
# These shared bundles are created alongside the homepage by the landing-page
# owner. Keep them explicit so a site image cannot silently omit them.
COPY site.css /usr/share/nginx/html/site.css
COPY site.js /usr/share/nginx/html/site.js

# Adds /install and /install.sh, which redirect to macapp/install-zero.sh in the
# repo. Redirecting rather than baking a copy into this image means the branded
# URL on the homepage can never serve a stale installer: a fix ships as soon as
# it lands on master, with no site redeploy. See the comments in nginx.conf.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
# Check the install redirect too, not just the homepage. If /install ever stops
# responding, the headline call to action on the site is broken, and that should
# fail the container rather than go unnoticed.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 \
   && wget -qS --spider http://127.0.0.1/install 2>&1 | grep -q '302' \
   || exit 1
CMD ["nginx", "-g", "daemon off;"]
