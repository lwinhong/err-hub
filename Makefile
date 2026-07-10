# ErrHub Makefile
# 所有命令均在 docker/ 目录下执行

DOCKER_DIR := docker
COMPOSE    := docker compose -f $(DOCKER_DIR)/docker-compose.yml

# ─────────────────────────────────────────
#  构建
# ─────────────────────────────────────────

.PHONY: build
build: ## 构建 api 和 web 镜像
	$(COMPOSE) build

.PHONY: build-api
build-api: ## 仅构建 api 镜像
	$(COMPOSE) build api

.PHONY: build-web
build-web: ## 仅构建 web 镜像
	$(COMPOSE) build web

# ─────────────────────────────────────────
#  启动 / 停止
# ─────────────────────────────────────────

.PHONY: up
up: build ## 构建镜像并启动所有服务（后台运行）
	$(COMPOSE) up -d

.PHONY: start
start: ## 启动已构建的容器
	$(COMPOSE) up -d

.PHONY: stop
stop: ## 停止所有容器（保留数据）
	$(COMPOSE) stop

.PHONY: restart
restart: ## 重启所有容器
	$(COMPOSE) restart

.PHONY: down
down: ## 停止并删除容器和网络
	$(COMPOSE) down

# ─────────────────────────────────────────
#  SDK 构建
# ─────────────────────────────────────────

.PHONY: build-sdk
build-sdk: ## 压缩 SDK 生成 error-feedback.min.js
	cd frontend && pnpm run build-sdk

# ─────────────────────────────────────────
#  重建（代码修改后使用）
# ─────────────────────────────────────────

.PHONY: rebuild
rebuild: ## 重建 api 镜像并强制重启 api + gateway（后端/nginx 修改后用）
	$(COMPOSE) build api
	$(COMPOSE) up -d --force-recreate api gateway

.PHONY: rebuild-all
rebuild-all: ## 重建全部镜像并强制重启所有服务（前端修改后用）
	$(COMPOSE) build
	$(COMPOSE) up -d --force-recreate

# ─────────────────────────────────────────
#  日志 / 状态
# ─────────────────────────────────────────

.PHONY: logs
logs: ## 实时查看所有服务日志
	$(COMPOSE) logs -f --tail=100

.PHONY: logs-api
logs-api: ## 仅查看 API 服务日志
	$(COMPOSE) logs -f --tail=100 api

.PHONY: logs-celery
logs-celery: ## 查看 Celery worker + beat 日志
	$(COMPOSE) logs -f --tail=100 celery-worker celery-beat

.PHONY: logs-web
logs-web: ## 仅查看前端服务日志
	$(COMPOSE) logs -f --tail=100 web

.PHONY: logs-gateway
logs-gateway: ## 仅查看网关日志
	$(COMPOSE) logs -f --tail=100 gateway

.PHONY: status
status: ## 查看各容器运行状态
	$(COMPOSE) ps

# ─────────────────────────────────────────
#  清理（慎用）
# ─────────────────────────────────────────

.PHONY: clean
clean: ## 停止容器并删除数据卷（会丢失数据库数据！）
	$(COMPOSE) down -v

# ─────────────────────────────────────────
#  帮助
# ─────────────────────────────────────────

.PHONY: help
help: ## 显示本帮助
	@echo "ErrHub 常用命令："
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

.DEFAULT_GOAL := help
