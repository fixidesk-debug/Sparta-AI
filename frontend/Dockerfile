########################################
# Multi-stage build for React frontend #
########################################

FROM node:20-alpine as build
WORKDIR /app
COPY package.json ./
COPY tsconfig.json ./
COPY public ./public
COPY src ./src
RUN npm install --production --legacy-peer-deps && npm run build

# Production stage
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
# Security: use non-root user
RUN addgroup -g 1001 sparta && adduser -D -u 1001 -G sparta sparta
USER sparta
# Copy built files
COPY --from=build /app/build .
# Copy custom nginx config for SSL, caching, security headers
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose HTTP and HTTPS
EXPOSE 80
EXPOSE 443
# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget --spider --no-verbose http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
