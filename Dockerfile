# Use a nginx Docker image
FROM kevinelg/hugo-asciidoc AS hugo-adoc
WORKDIR /tmp/my-web
COPY ./ /tmp/my-web
RUN hugo -D

FROM nginx
# Copy the static HTMLs to the nginx directory
# Copy the nginx configuration template to the nginx config directory
COPY nginx/default.template /etc/nginx/conf.d/default.template
# Substitute the environment variables and generate the final config
CMD envsubst < /etc/nginx/conf.d/default.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'
ARG CACHEBUST=1
COPY --from=hugo-adoc /tmp/my-web/public /usr/share/nginx/html
