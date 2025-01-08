# 构建阶段
FROM node:16 as builder

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./

# 安装依赖
RUN npm install --registry=https://registry.npmmirror.com

# 复制源代码
COPY . .

# 构建项目
RUN npm run build

# 部署阶段
FROM nginx:latest

# 从构建阶段复制构建结果到nginx目录
COPY --from=builder /app/dist /app/html
COPY --from=builder /app/nginx.conf  /etc/nginx/nginx.conf

# 暴露80端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
