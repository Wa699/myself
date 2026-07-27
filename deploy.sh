#!/bin/bash
set -e

echo "========================================"
echo "  个人简历问答智能体 - 一键部署"
echo "========================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo ">>> 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null 2>&1; then
    echo ">>> Docker Compose 不可用，请检查 Docker 版本"
    exit 1
fi

# 环境变量
if [ ! -f .env ]; then
    echo ">>> 创建 .env 文件，请编辑填入真实密钥..."
    cp .env.example .env
    echo ""
    echo "   ⚠️  请先编辑 .env 文件，填入："
    echo "     - PRIMARY_API_KEY  （API 密钥）"
    echo "     - MYSQL_ROOT_PASSWORD （数据库密码）"
    echo ""
    echo "   然后重新运行本脚本"
    exit 0
fi

# 检查简历文件
RESUME_COUNT=$(find resumes/ -maxdepth 1 \( -iname "*.pdf" -o -iname "*.docx" -o -iname "*.txt" \) 2>/dev/null | wc -l)
if [ "$RESUME_COUNT" -eq 0 ]; then
    echo ">>> ⚠️  resumes/ 目录中没有简历文件，请放入 PDF/Word/TXT 后再运行"
    exit 1
fi

# 构建前端
echo ">>> 构建前端..."
if command -v npm &> /dev/null; then
    cd frontend && npm install && npm run build && cd ..
else
    echo ">>> npm 未安装，跳过前端构建（使用已有 dist）"
fi

# 启动
echo ">>> 构建并启动服务..."
docker compose up -d --build

# 等待服务就绪
echo ">>> 等待服务就绪..."
sleep 10

# 检查状态
echo ""
docker compose ps

echo ""
echo "========================================"
echo "  ✅ 部署完成！"
echo "========================================"
echo ""
echo "  访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo '你的服务器IP')"
echo ""
echo "  管理命令："
echo "    docker compose logs -f    查看日志"
echo "    docker compose restart    重启服务"
echo "    docker compose down       停止服务"
echo ""
