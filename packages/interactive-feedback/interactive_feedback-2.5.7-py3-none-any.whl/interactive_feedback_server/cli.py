# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by pawa (https://github.com/pawaovo) with ideas from https://github.com/noopstudios/interactive-feedback-mcp
import os
import sys
import json
import tempfile
import subprocess
import base64

# from typing import Annotated # Annotated 未在此文件中直接使用 (Annotated not directly used in this file)
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Tuple,
    Union,
)  # 简化导入 (Simplified imports)

from fastmcp import FastMCP, Image
from pydantic import (
    Field,
)  # Field 由 FastMCP 内部使用 (Field is used internally by FastMCP)

from .utils import get_config, resolve_final_options, get_display_mode

# 错误消息常量
ERROR_MESSAGES = {
    "missing_both_params": "[错误] AI必须同时提供message和full_response两个参数，不能为空",
    "no_user_feedback": "[用户未提供反馈]",
}


def _is_valid_param(param: Optional[str]) -> bool:
    """检查参数是否有效（非空且非纯空白）"""
    return param and param.strip()


def _process_ui_output(ui_output_dict: Dict[str, Any]) -> List[Union[str, Image]]:
    """
    处理UI输出内容，提取文本、图片和文件引用

    Args:
        ui_output_dict: UI返回的输出字典

    Returns:
        List[Union[str, Image]]: 处理后的内容列表
    """
    processed_content: List[Union[str, Image]] = []

    if not (
        ui_output_dict
        and "content" in ui_output_dict
        and isinstance(ui_output_dict["content"], list)
    ):
        return processed_content

    for item in ui_output_dict.get("content", []):
        if not isinstance(item, dict):
            print(f"警告: 无效的内容项格式: {item}", file=sys.stderr)
            continue

        item_type = item.get("type")
        if item_type == "text":
            text_content = item.get("text", "")
            if text_content:
                processed_content.append(text_content)
        elif item_type == "image":
            _process_image_item(item, processed_content)
        elif item_type == "file_reference":
            _process_file_reference_item(item, processed_content)
        else:
            print(f"警告: 未知的内容项类型: {item_type}", file=sys.stderr)

    return processed_content


def _process_image_item(
    item: Dict[str, Any], processed_content: List[Union[str, Image]]
) -> None:
    """处理图片项"""
    base64_data = item.get("data")
    mime_type = item.get("mimeType")
    if base64_data and mime_type:
        try:
            image_format_str = mime_type.split("/")[-1].lower()
            if image_format_str == "jpeg":
                image_format_str = "jpg"

            image_bytes = base64.b64decode(base64_data)
            mcp_image = Image(data=image_bytes, format=image_format_str)
            processed_content.append(mcp_image)
        except Exception as e:
            print(f"错误: 处理图像失败: {e}", file=sys.stderr)
            processed_content.append(f"[图像处理失败: {mime_type or 'unknown type'}]")


def _process_file_reference_item(
    item: Dict[str, Any], processed_content: List[Union[str, Image]]
) -> None:
    """处理文件引用项"""
    display_name = item.get("display_name", "")
    file_path = item.get("path", "")
    if display_name and file_path:
        file_info = f"引用文件: {display_name} [路径: {file_path}]"
        processed_content.append(file_info)


def get_system_prompts():
    """
    获取系统提示词（从配置读取，使用config_manager中的默认值）
    Get system prompts (read from config, use defaults from config_manager)

    Returns:
        dict: 包含optimize和reinforce提示词的字典
    """
    try:
        config = get_config()
        optimizer_config = config.get("expression_optimizer", {})
        return optimizer_config.get("prompts", {})
    except Exception:
        # 回退到config_manager中的默认配置
        from .utils.config_manager import DEFAULT_CONFIG

        return DEFAULT_CONFIG["expression_optimizer"]["prompts"]


def format_prompt_for_mode(
    original_text: str, mode: str, reinforcement_prompt: str = None
) -> str:
    """
    根据模式格式化提示词
    Format prompt based on mode

    Args:
        original_text: 原始文本
        mode: 优化模式
        reinforcement_prompt: 强化指令（可选）

    Returns:
        str: 格式化后的提示词
    """
    if mode == "reinforce" and reinforcement_prompt:
        return f"强化指令: '{reinforcement_prompt}'\n\n原始文本: '{original_text}'"
    else:
        return original_text


print(f"Server.py 启动 - Python解释器路径: {sys.executable}")
print(f"Server.py 当前工作目录: {os.getcwd()}")


mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")


def detect_uvx_environment() -> bool:
    """检测是否在 uvx 环境中运行"""
    return (
        'UV_PROJECT_ENVIRONMENT' in os.environ or
        'UV_CACHE_DIR' in os.environ or
        'UV_TOOL_DIR' in os.environ
    )


def detect_mcp_environment() -> bool:
    """检测是否在 MCP 服务环境中运行"""
    return (
        not sys.stdin.isatty() or  # 没有交互式终端
        'MCP_SERVER' in os.environ or
        hasattr(sys.stdin, 'closed') and sys.stdin.closed
    )


def launch_feedback_ui_via_module(
    summary: str, predefined_options_list: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    通过直接模块调用启动 feedback UI（uvx 兼容模式）
    Launch feedback UI via direct module call (uvx compatible mode)
    """
    tmp_file_path = None
    try:
        # 创建输出文件
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp_file_path = tmp.name

        options_str = (
            "|||".join(predefined_options_list) if predefined_options_list else ""
        )

        # 尝试直接导入并调用 feedback_ui
        try:
            # 检查PySide6是否可用
            try:
                import PySide6
                print(f"PySide6 版本: {PySide6.__version__}", file=sys.stderr)

                # 在MCP环境中，即使PySide6可用也不能启动GUI
                if detect_mcp_environment():
                    print("检测到MCP环境，跳过GUI启动", file=sys.stderr)
                    raise ImportError("MCP环境不支持GUI")

            except ImportError as pyside_error:
                print(f"警告: PySide6 不可用或不适用: {pyside_error}", file=sys.stderr)
                print("将使用降级模式", file=sys.stderr)
                raise ImportError("PySide6 不可用")

            from feedback_ui.cli import start_feedback_tool

            options_list = [
                opt.strip() for opt in options_str.split("|||") if opt.strip()
            ] if options_str else None

            print(f"使用模块直接调用模式启动 UI", file=sys.stderr)
            result = start_feedback_tool(summary, options_list, tmp_file_path)

            # 读取结果文件
            with open(tmp_file_path, "r", encoding="utf-8") as f:
                ui_result_data = json.load(f)

            return ui_result_data

        except ImportError as import_error:
            print(f"模块导入失败: {import_error}", file=sys.stderr)
            print("可能原因: PySide6依赖在uvx环境中不完整或MCP环境不支持GUI", file=sys.stderr)
            # 降级到命令行模式
            raise Exception("模块导入失败，需要降级处理")

    except Exception as e:
        print(f"错误: launch_feedback_ui_via_module 异常: {e}", file=sys.stderr)
        raise
    finally:
        # 清理临时文件
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except OSError as e_unlink:
                print(
                    f"警告: 删除临时文件失败 '{tmp_file_path}': {e_unlink}",
                    file=sys.stderr,
                )


def launch_feedback_ui_fallback(
    summary: str, predefined_options_list: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    降级模式：使用简化的命令行交互或MCP兼容模式
    Fallback mode: use simplified command line interaction or MCP compatible mode
    """
    # 检测是否在MCP环境中
    is_mcp = detect_mcp_environment()

    if is_mcp:
        # MCP环境：无法进行交互式输入，返回默认选项或提示
        print("🔄 MCP环境检测：无交互式终端，使用智能默认选择", file=sys.stderr)

        options_list = predefined_options_list or []

        if options_list:
            # 如果有预定义选项，选择第一个作为默认
            user_input = options_list[0]
            print(f"📋 自动选择第一个选项: {user_input}", file=sys.stderr)
        else:
            # 没有预定义选项，返回一个通用的确认
            user_input = "继续执行"
            print(f"📝 AI请求: {summary}", file=sys.stderr)
            print(f"✅ 自动确认: {user_input}", file=sys.stderr)

        result = {
            "content": [
                {
                    "type": "text",
                    "text": user_input
                }
            ],
            "metadata": {
                "mode": "mcp_auto",
                "environment": "mcp_fallback",
                "version": "2.5.6",
                "auto_selected": True
            }
        }

        return result

    # 非MCP环境：使用交互式命令行
    print("\n" + "="*60, file=sys.stderr)
    print("🔄 uvx 兼容模式：简化命令行交互", file=sys.stderr)
    print("💡 提示：GUI界面在uvx环境中不可用，使用命令行交互", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # 解析选项
    options_list = predefined_options_list or []

    # 创建简化的交互
    print(f"\n📝 AI助手请求:", file=sys.stderr)
    print(f"   {summary}", file=sys.stderr)

    if options_list:
        print(f"\n📋 可选选项:", file=sys.stderr)
        for i, option in enumerate(options_list, 1):
            print(f"   {i}. {option}", file=sys.stderr)
        print(f"   {len(options_list) + 1}. 💬 自定义输入", file=sys.stderr)

        try:
            choice = input(f"\n👆 请选择 (1-{len(options_list) + 1}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(options_list):
                user_input = options_list[choice_num - 1]
                print(f"✅ 您选择了: {user_input}", file=sys.stderr)
            else:
                user_input = input("💬 请输入您的反馈: ").strip()
                print(f"✅ 您输入了: {user_input}", file=sys.stderr)
        except (ValueError, KeyboardInterrupt, EOFError):
            user_input = "用户取消操作"
            print("❌ 操作已取消", file=sys.stderr)
    else:
        try:
            user_input = input("\n💬 请输入您的反馈: ").strip()
            if user_input:
                print(f"✅ 您输入了: {user_input}", file=sys.stderr)
        except (KeyboardInterrupt, EOFError):
            user_input = "用户取消操作"
            print("❌ 操作已取消", file=sys.stderr)

    print("="*60 + "\n", file=sys.stderr)

    # 创建结果
    result = {
        "content": [
            {
                "type": "text",
                "text": user_input or "无反馈"
            }
        ],
        "metadata": {
            "mode": "fallback",
            "environment": "uvx_fallback",
            "version": "2.5.6"
        }
    }

    return result


def launch_feedback_ui(
    summary: str, predefined_options_list: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Launches the feedback UI as a separate process using its command-line entry point.
    Collects user input and returns it as a structured dictionary.

    修改版本：添加 uvx 环境检测和兼容性处理
    Modified version: Added uvx environment detection and compatibility handling
    """
    # 检测 uvx 环境
    is_uvx = detect_uvx_environment()

    if is_uvx:
        print("检测到 uvx 环境，使用兼容模式", file=sys.stderr)
        try:
            # 尝试模块直接调用
            return launch_feedback_ui_via_module(summary, predefined_options_list)
        except Exception as module_error:
            print(f"模块调用失败: {module_error}", file=sys.stderr)
            print("降级到简化交互模式", file=sys.stderr)
            return launch_feedback_ui_fallback(summary, predefined_options_list)

    # 原始的命令行调用模式（非 uvx 环境）
    tmp_file_path = None
    try:
        # 创建输出文件
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp_file_path = tmp.name

        options_str = (
            "|||".join(predefined_options_list) if predefined_options_list else ""
        )

        # Build the argument list for the 'feedback-ui' command
        args_list = [
            "feedback-ui",
            "--prompt",
            summary,
            "--output-file",
            tmp_file_path,
            "--predefined-options",
            options_str,
        ]

        # Run the feedback-ui command
        process_result = subprocess.run(
            args_list,
            check=False,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            close_fds=(
                os.name != "nt"
            ),  # close_fds is not supported on Windows when shell=False
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if process_result.returncode != 0:
            print(
                f"错误: 启动反馈UI失败，返回码: {process_result.returncode}",
                file=sys.stderr,
            )
            if process_result.stdout:
                print(f"UI STDOUT:\n{process_result.stdout}", file=sys.stderr)
            if process_result.stderr:
                print(f"UI STDERR:\n{process_result.stderr}", file=sys.stderr)

            # 如果命令行调用失败，尝试降级模式
            print("命令行调用失败，尝试降级模式", file=sys.stderr)
            return launch_feedback_ui_fallback(summary, predefined_options_list)

        with open(tmp_file_path, "r", encoding="utf-8") as f:
            ui_result_data = json.load(f)

        return ui_result_data

    except FileNotFoundError:
        print("错误: 'feedback-ui' 命令未找到", file=sys.stderr)
        print("尝试降级模式", file=sys.stderr)
        return launch_feedback_ui_fallback(summary, predefined_options_list)
    except Exception as e:
        print(f"错误: launch_feedback_ui 异常: {e}", file=sys.stderr)
        print("尝试降级模式", file=sys.stderr)
        return launch_feedback_ui_fallback(summary, predefined_options_list)
    finally:
        # 清理临时文件
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except OSError as e_unlink:
                print(
                    f"警告: 删除临时文件失败 '{tmp_file_path}': {e_unlink}",
                    file=sys.stderr,
                )


@mcp.tool()
def interactive_feedback(
    message: Optional[str] = Field(
        default=None,
        description="[SIMPLE mode] Concise question for user input (AI must display full response in chat first)",
    ),
    full_response: Optional[str] = Field(
        default=None,
        description="[FULL mode] AI's complete response content (AI must display this in chat first)",
    ),
    predefined_options: Optional[List[str]] = Field(
        default=None, description="Predefined options for user selection"
    ),
) -> Tuple[Union[str, Image], ...]:  # 返回字符串和/或 fastmcp.Image 对象的元组
    """
    Requests user input via GUI after AI displays complete response in chat.

    USAGE FLOW:
    1. AI displays complete response in chat dialog
    2. AI calls this tool to collect user input
    3. Tool returns user feedback only

    This tool collects user input, not for displaying AI responses.
    AI responses must appear in chat dialog before calling this tool.

    PARAMETER REQUIREMENTS:
    - AI MUST provide BOTH 'message' and 'full_response' parameters
    - Both parameters cannot be empty or whitespace-only
    - MCP service will automatically select which content to display based on user's display_mode setting

    USAGE PATTERN:

    # Step 1: AI displays complete response in chat
    # Step 2: AI calls tool with BOTH parameters
    interactive_feedback(
        message="你希望我实现这些更改吗？",  # Required: concise question
        full_response="我分析了你的代码，发现了3个问题...",  # Required: complete response
        predefined_options=["修复方案A", "修复方案B", "让我想想"]
    )

    Note: MCP service automatically selects appropriate content based on user's display mode configuration.
    """

    # 严格的双参数验证：AI必须同时提供两个有效参数
    if not _is_valid_param(message) or not _is_valid_param(full_response):
        return (ERROR_MESSAGES["missing_both_params"],)

    # 获取配置（一次性读取，避免重复）
    config = get_config()
    display_mode = get_display_mode(config)

    # 根据用户配置的显示模式选择要展示的内容
    prompt_to_display = full_response if display_mode == "full" else message

    # 解析最终选项
    final_options = resolve_final_options(
        ai_options=predefined_options, text=prompt_to_display, config=config
    )

    # 转换为UI需要的格式（final_options已经是字符串列表，无需转换）
    options_list_for_ui = final_options if final_options else None

    # 启动UI并获取用户输入
    ui_output_dict = launch_feedback_ui(prompt_to_display, options_list_for_ui)

    # 处理UI输出内容
    processed_mcp_content = _process_ui_output(ui_output_dict)

    if not processed_mcp_content:
        return (ERROR_MESSAGES["no_user_feedback"],)

    return tuple(processed_mcp_content)


@mcp.tool()
def optimize_user_input(
    original_text: str = Field(description="用户的原始输入文本"),
    mode: str = Field(description="优化模式: 'optimize' 或 'reinforce'"),
    reinforcement_prompt: Optional[str] = Field(
        default=None, description="在 'reinforce' 模式下用户的自定义指令"
    ),
) -> str:
    """
    使用配置的 LLM API 来优化或强化用户输入的文本。

    此功能可以帮助用户将口语化的、可能存在歧义的输入，转化为更结构化、
    更清晰、更便于 AI 模型理解的文本。

    Args:
        original_text: 用户的原始输入文本
        mode: 优化模式
            - 'optimize': 一键优化，使用预设的通用优化指令
            - 'reinforce': 提示词强化，使用用户自定义的强化指令
        reinforcement_prompt: 在 'reinforce' 模式下用户的自定义指令

    Returns:
        str: 优化后的文本或错误信息
    """
    try:
        # 导入LLM模块
        from .llm.factory import get_llm_provider
        from .llm.performance_manager import get_optimization_manager

        # 获取配置
        config = get_config().get("expression_optimizer", {})

        # 获取LLM provider
        provider, status_message = get_llm_provider(config)

        if not provider:
            return f"[优化功能不可用] {status_message}"

        # 获取系统提示词
        system_prompts = get_system_prompts()

        # 验证模式和参数
        if mode == "optimize":
            system_prompt = system_prompts["optimize"]
        elif mode == "reinforce":
            if not reinforcement_prompt:
                return "[错误] 'reinforce' 模式需要提供强化指令"
            system_prompt = system_prompts["reinforce"]
        else:
            return f"[错误] 无效的优化模式: {mode}。支持的模式: 'optimize', 'reinforce'"

        # 简化逻辑：默认使用性能管理器（包含缓存功能）
        manager = get_optimization_manager(config)

        result = manager.optimize_with_cache(
            provider=provider,
            text=original_text,
            mode=mode,
            system_prompt=system_prompt,
            reinforcement=reinforcement_prompt or "",
        )

        # 检查是否是错误信息
        if result.startswith("[ERROR"):
            return f"[优化失败] {result}"

        return result

    except ImportError as e:
        return f"[配置错误] LLM模块导入失败: {e}"
    except Exception as e:
        return f"[系统错误] 优化过程中发生异常: {e}"


def main():
    """Main function to run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
