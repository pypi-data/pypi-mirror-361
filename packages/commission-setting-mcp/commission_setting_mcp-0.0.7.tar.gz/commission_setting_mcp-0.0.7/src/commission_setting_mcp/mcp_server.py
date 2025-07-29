from mcp.server.fastmcp import FastMCP

from commission_setting_mcp import playwright_commission
from commission_setting_mcp.feishu_util import YXXFeishuSheetUtil
from shared.error_handler import format_exception_message
from shared.log_util import log_error, log_info

mcp = FastMCP("commission_setting_mcp_server", port=8089)


async def server_log_info(msg: str):
    """发送信息级别的日志消息"""
    log_info(msg)
    await mcp.get_context().session.send_log_message(
        level="info",
        data=msg,
    )


@mcp.tool()
async def query_unconfigured_commission_plan_products() -> str:
    """查询未配置分润方案的商品"""
    try:
        await server_log_info("正在查询未配置分润方案的商品...")

        feishu_util = YXXFeishuSheetUtil()
        filtered_rows = await feishu_util.get_filtered_rows()

        if not filtered_rows:
            result = "当前没有未配置分润方案的商品。"
        else:
            result_lines = ["未配置分润方案的商品列表："]
            for row in filtered_rows:
                product_id = row.get("聚宝赞商品id", "未知")
                system_config = row.get("系统配置模版", "未知")
                result_lines.append(f"聚宝赞商品id:{product_id}，分润系统配置模版：\"{system_config}\"。")

            result = "\n".join(result_lines)

        await server_log_info(f"查询到 {len(filtered_rows)} 个未配置商品")
        return result

    except Exception as e:
        await server_log_info(f"【E】查询未配置商品时出错: {str(e)}")
        return format_exception_message("查询未配置商品时出错", e)

# @mcp.tool()
# async def open_product_settlement_page() -> str:
#     """商品配置分润方案第一步，打开商品结算设置页面，打开成功才能执行后续步骤"""
#     try:
#         await server_log_info("正在打开商品结算页面...")
#         _, result = await playwright_commission.open_commission_setting_page()
#         await server_log_info(f"打开商品结算页面结果: {result}")
#         return result
#     except Exception as e:
#         await server_log_info(f"【E】打开商品结算页面时出错: {str(e)}")
#         return format_exception_message("打开商品结算页面时出错", e)


@mcp.tool()
async def complete_product_settlement_workflow(product_id: str, profit_sharing_plan: str) -> str:
    """商品配置分润方案，成功打开商品结算设置页面之后，为指定商品，设置分润方案。
    如果浏览器已打开，会自动在新标签页中执行任务；如果浏览器未打开，会先打开浏览器再执行任务。
    
    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称
    """
    try:
        log_info(f"complete_product_settlement_workflow start {product_id}")
        finish_update_sheets: bool = False
        await server_log_info(f"开始商品 {product_id} 的完整结算配置流程...")
        
        # 直接调用智能设置方法
        result = await playwright_commission.smart_set_product_commission_plan(
            product_id, profit_sharing_plan
        )
        
        # 如果配置成功且需要更新表格
        if finish_update_sheets and "成功" in result:
            await server_log_info(f"正在更新表格中商品 {product_id} 的已配置状态...")
            try:
                feishu_util = YXXFeishuSheetUtil()
                # 注意：这里使用的是商品id（对应表格中的商品id列），不是聚宝赞商品id
                update_success = await feishu_util.update_by_product_id(product_id, "已配置分润方案", "Y")
                if update_success:
                    result += "\n✓ 已更新表格中的已配置状态为Y"
                    await server_log_info(f"成功更新表格中商品 {product_id} 的已配置状态")
                else:
                    result += "\n⚠ 表格状态更新失败"
                    await server_log_info(f"更新表格中商品 {product_id} 的已配置状态失败")
            except Exception as sheet_error:
                result += f"\n⚠ 表格状态更新异常: {str(sheet_error)}"
                await server_log_info(f"更新表格状态时出错: {str(sheet_error)}")
        
        await server_log_info(f"完整工作流程结果: {result}")
        return result
        
    except Exception as e:
        await server_log_info(f"【E】完整工作流程执行时出错: {str(e)}")
        return format_exception_message("完整工作流程执行时出错", e)


# @mcp.tool()
# async def open_rebate_set_page() -> str:
#     """服务商返点关联商品或检查商品返点方案的第一步，打开服务商返点关联页，打开成功才能执行后续步骤"""
#     try:
#         await server_log_info("正在打开服务商返点关联页...")
#         _, result = await playwright_commission.open_rebate_set_page()
#         await server_log_info(f"打开服务商返点关联页结果: {result}")
#         return result
#     except Exception as e:
#         await server_log_info(f"【E】打开服务商返点关联页时出错: {str(e)}")
#         return format_exception_message("打开服务商返点关联页时出错", e)


@mcp.tool()
async def complete_product_rebate_workflow(product_id: str, profit_sharing_plan: str) -> str:
    """服务商返点关联商品配置，为指定商品设置返点关联。
    会自动打开浏览器执行配置，如果打开浏览器失败，需要提醒用户手动处理，再重新提交本任务。
    
    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称
    """
    try:
        await server_log_info(f"开始商品 {product_id} 的服务商返点关联配置流程...")
        
        # 直接调用智能设置方法
        result = await playwright_commission.smart_set_product_rebate(
            product_id, profit_sharing_plan
        )
        
        await server_log_info(f"服务商返点关联配置结果: {result}")
        return result
        
    except Exception as e:
        await server_log_info(f"【E】服务商返点关联配置时出错: {str(e)}")
        return format_exception_message("服务商返点关联配置时出错", e)


# @mcp.tool()
# async def get_current_time() -> str:
#     """获取当前时间字符串，格式为YYYY-MM-DD HH:MM:SS"""
#     try:
#         from datetime import datetime
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         return f"当前时间: {current_time}"
#     except Exception as e:
#         await server_log_info(f"【E】获取当前时间时出错: {str(e)}")
#         return format_exception_message("获取当前时间时出错", e)


@mcp.tool()
async def check_product_commission_setting(product_id: str, profit_sharing_plan: str) -> str:
    """检查商品聚宝赞分润方案和服务商返点方案配置是否正确
    
    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称
    """
    try:
        await server_log_info(f"开始检查商品 {product_id} 的分润方案和返点方案配置...")
        
        # 调用智能检查方法
        result = await playwright_commission.smart_check_product_commission_setting(
            product_id, profit_sharing_plan
        )
        
        await server_log_info(f"配置检查完成: {result}")
        return result
        
    except Exception as e:
        await server_log_info(f"【E】检查商品配置时出错: {str(e)}")
        return format_exception_message("检查商品配置时出错", e)


@mcp.tool()
async def get_current_version() -> str:
    """获取当前工具的版本号"""
    try:
        import importlib.metadata
        version = importlib.metadata.version("commission-setting-mcp")
        return f"当前版本号: {version}"
    except Exception as e:
        await server_log_info(f"【E】获取版本号时出错: {str(e)}")
        return format_exception_message("获取版本号时出错", e)

def main():
    """佣金设置MCP服务入口函数"""
    log_info(f"佣金设置MCP服务启动")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()