FROM php:8.3-cli-alpine AS php
RUN docker-php-ext-install mysqli

FROM python:3.12-alpine AS python
WORKDIR /var/grid
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM node:20-alpine AS node-builder
WORKDIR /app
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build

FROM node:20-alpine AS nuxt
WORKDIR /app
COPY --from=node-builder /app/.output .output
CMD ["node", ".output/server/index.mjs"]

FROM nginx:alpine-slim AS web
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN sed -i -e '/default_type/a\' -e '    charset utf-8;' /etc/nginx/nginx.conf
