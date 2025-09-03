# Frontend Dockerfile for React (production build)
FROM node:20 AS build
WORKDIR /app
COPY ./frontend /app
RUN npm install --legacy-peer-deps && npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
