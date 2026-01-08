FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

COPY . .

EXPOSE 5173

# Use --host to bind to all interfaces for Docker
CMD ["npm", "run", "dev", "--", "--host"]
