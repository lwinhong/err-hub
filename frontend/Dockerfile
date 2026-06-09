# frontend
FROM node:lts-alpine AS build

WORKDIR /app

COPY package*.json pnpm-lock.yaml ./
RUN npm install pnpm -global
RUN pnpm install --no-frozen-lockfile --ignore-scripts

COPY . .
RUN pnpm run build

# production
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
