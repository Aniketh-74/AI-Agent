FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
# Ensure Vite's index.html is at project root for the build step
COPY . .
RUN if [ -f public/index.html ]; then cp public/index.html index.html; fi
RUN npm run build

# production stage
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# default nginx port 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
