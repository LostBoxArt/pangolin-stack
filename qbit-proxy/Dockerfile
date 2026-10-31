FROM node:24-slim
WORKDIR /app
COPY index.js healthcheck.js .
EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 CMD ["node", "healthcheck.js"]
CMD ["node", "index.js"]
