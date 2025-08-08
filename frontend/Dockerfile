# Use Node.js 18 Alpine image as base
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Clean any existing builds (defensive cleanup)
RUN rm -rf node_modules .next

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies using npm ci
RUN npm ci

# Copy the application code
COPY . .

# Clean builds again before building (ensure fresh build)
RUN rm -rf .next

# Build the Next.js application
RUN npm run build

# Create a non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose the port the app runs on
EXPOSE 3000

# Command to run the production build
CMD ["npm", "start"]
