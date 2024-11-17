FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=4000
ENV WATCHPACK_POLLING=true

# Start the application
CMD ["npm", "start"] 