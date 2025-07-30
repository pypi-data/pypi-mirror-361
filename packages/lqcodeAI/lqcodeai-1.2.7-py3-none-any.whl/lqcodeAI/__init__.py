"""
名称:绿旗编程AI课程SDK

说明:这个模块提供了与绿旗编程AI服务交互的接口。
现在支持插件化架构，添加新功能更简单！

新的目录结构：
- core/: 核心功能（基础类、配置、插件系统等）
- plugins/: AI功能插件（所有ai_xxx.py文件）
- cli/: 命令行接口
"""

# 导入核心功能
from .core import (
    BaseAI, Config, registry, ai_plugin, 
    DynamicLqcodeAI, LqcodeAI, lq
)

# 自动导入所有插件（这会触发插件注册）
from . import plugins  # 这会自动导入所有插件

# 动态获取所有插件类
def _get_plugin_classes():
    """动态获取所有插件类"""
    plugin_classes = []
    for attr_name in dir(plugins):
        attr = getattr(plugins, attr_name)
        if isinstance(attr, type) and attr_name.endswith('AI'):
            plugin_classes.append(attr_name)
    return plugin_classes

_plugin_classes = _get_plugin_classes()

# 导入CLI功能
from .cli import DynamicCLI, cli, main as cli_main

# 向后兼容 - 保留旧的类名
class LegacyLqcodeAI(LqcodeAI):
    """向后兼容的旧版本接口"""
    pass

# 导出类和实例
__all__ = [
    # 核心功能
    'BaseAI',
    'Config',
    'ai_plugin',
    'registry',
    'lq',
    'LqcodeAI',
    'DynamicLqcodeAI',
    
    # AI插件类（动态生成）
    *_plugin_classes,
    
    # CLI功能
    'DynamicCLI',
    'cli',
    'cli_main',
    
    # 向后兼容
    'LegacyLqcodeAI',
] 