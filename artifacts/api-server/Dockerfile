# API Server Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy built dist files
COPY dist ./dist
COPY package.json .

# Install production dependencies
RUN npm install --omit=dev

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3002/api/streamlit-url || exit 1

# Start the server
CMD ["node", "--enable-source-maps", "./dist/index.mjs"]
