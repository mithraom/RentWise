FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_APARTMENT_API_URL=http://localhost:5001
ARG VITE_ADVISOR_API_URL=http://localhost:5002
ENV VITE_APARTMENT_API_URL=$VITE_APARTMENT_API_URL VITE_ADVISOR_API_URL=$VITE_ADVISOR_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
RUN printf 'server { listen 80; root /usr/share/nginx/html; location / { try_files $uri /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 80
