import argparse
import json
import os
from pathlib import Path
try:
    # 尝试使用新的动态CLI
    from lqcodeAI.lqcodeAI.cli.dynamic_cli import main as dynamic_main
    USE_DYNAMIC_CLI = True
except ImportError:
    # 回退到旧版本
    from lqcodeAI import lq
    USE_DYNAMIC_CLI = False

def create_launch_json():
    """创建VSCode的launch.json配置文件"""
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: 藏头诗",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Python: 天气查询",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Python: B站热榜",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Python: 成语接龙",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            }
        ]
    }
    
    # 创建.vscode目录
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # 写入launch.json
    launch_file = vscode_dir / "launch.json"
    with open(launch_file, "w", encoding="utf-8") as f:
        json.dump(launch_config, f, indent=4, ensure_ascii=False)
    
    return str(launch_file)

def main():
    """主入口函数 - 支持新旧两种CLI模式"""
    if USE_DYNAMIC_CLI:
        # 使用新的动态CLI系统
        dynamic_main()
    else:
        # 使用旧的静态CLI系统（向后兼容）
        legacy_main()

def legacy_main():
    """旧版本的CLI实现（向后兼容）"""
    parser = argparse.ArgumentParser(description='绿旗编程AI功能命令行工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 初始化命令
    subparsers.add_parser('init', help='初始化VSCode配置')

    # 藏头诗命令
    poetry_parser = subparsers.add_parser('poetry', help='生成藏头诗')
    poetry_parser.add_argument('name', help='藏头诗内容')

    # 天气命令
    weather_parser = subparsers.add_parser('weather', help='查询天气')
    weather_parser.add_argument('city', help='城市名称')

    # B站热榜命令
    subparsers.add_parser('bilibili', help='获取B站热榜')

    # 成语接龙命令
    idioms_parser = subparsers.add_parser('idioms', help='成语接龙')
    idioms_parser.add_argument('idiom', help='起始成语')

    args = parser.parse_args()
    password = 'lqcode'  # 默认密码

    if args.command == 'init':
        launch_file = create_launch_json()
        print(f"已创建VSCode配置文件: {launch_file}")
        print("配置包含以下调试选项：")
        print("- Python: 藏头诗")
        print("- Python: 天气查询")
        print("- Python: B站热榜")
        print("- Python: 成语接龙")

    elif args.command == 'poetry':
        result = lq.ai_poetry(password, args.name)
        print(f"诗词：\n{result['poem']}\n")
        print(f"解释：\n{result['explanation']}")

    elif args.command == 'weather':
        result = lq.ai_weather(password, args.city)
        print(f"天气信息：\n{result['weather_info']}\n")
        print(f"解释：\n{result['explanation']}")

    elif args.command == 'bilibili':
        result = lq.ai_biliranking(password)
        print(f"B站热榜：\n{result['ranking']}")

    elif args.command == 'idioms':
        result = lq.ai_idioms(password, args.idiom)
        print(f"接龙成语：{result['idiom']}")
        print(f"解释：\n{result['explanation']}")

    else:
        parser.print_help()

if __name__ == '__main__':
    main() 