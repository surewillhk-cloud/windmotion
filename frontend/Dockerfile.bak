# ── Build Stage ──────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install --prefer-offline

COPY . .
RUN npm run build

# ── Production Stage ────────────────────────────────────────
FROM nginx:alpine

# Install envsubst for nginx config templating
RUN apk add --no-cache gettext

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config template (nginx official image auto-runs envsubst on /etc/nginx/templates/*.template)
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Default backend URL (overridden by Railway env var)
ENV BACKEND_URL=http://backend:8080

EXPOSE 80

# nginx official image supports envsubst in /etc/nginx/templates/
# It auto-generates config on startup
CMD ["nginx", "-g", "daemon off;"]
