#!/usr/bin/env python3
"""
音乐APP后端启动脚本
"""
import uvicorn
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs("data/music", exist_ok=True)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
