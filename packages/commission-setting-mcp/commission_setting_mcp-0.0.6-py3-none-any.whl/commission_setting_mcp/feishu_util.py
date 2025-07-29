import os
import httpx
import asyncio
from typing import Optional, List, Dict, Any
from shared.log_util import log_debug, log_info, log_error


class YXXFeishuSheetUtil:
    """云选象飞书表格操作工具类"""
    
    def __init__(self):
        self.app_id = os.getenv("feishu-app-id")
        self.app_secret = os.getenv("feishu-app-secret")
        self.tenant_access_token: Optional[str] = None
        self.token_expires_at: float = 0
        
        # 固定的表格配置
        self.spreadsheet_id = "EjMLsOBqXhYiKTt0WDwcOjngnqg"
        self.sheet_name = "jOMYW6"
        self.data_range = "A:L"
        
        # 列名到列字母的映射
        self.column_mapping = {
            "序号": "A",
            "商品id": "B", 
            "聚宝赞商品id": "C",
            "商品名称": "D",
            "零售价": "E",
            "机构总佣金比": "F",
            "社群佣金比": "G",
            "平台毛利比": "H",
            "阶梯权重": "I",
            "分润预留": "J",
            "系统配置模版": "K",
            "已配置分润方案": "L"
        }
        
        if not self.app_id or not self.app_secret:
            raise ValueError("需要设置环境变量 feishu-app-id 和 feishu-app-secret")
    
    async def get_tenant_access_token(self) -> str:
        """获取tenant_access_token，如果token未过期则直接返回缓存的token"""
        import time
        
        # 检查token是否还有效（提前5分钟刷新）
        if self.tenant_access_token and time.time() < (self.token_expires_at - 300):
            return self.tenant_access_token
        
        log_info("获取飞书租户访问令牌...")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"获取token失败: {result.get('msg', '未知错误')}")
            
            self.tenant_access_token = result.get("tenant_access_token")
            expires_in = result.get("expire", 7200)  # 默认2小时
            self.token_expires_at = time.time() + expires_in
            
            log_info(f"成功获取token，有效期: {expires_in} 秒")
            return self.tenant_access_token
    
    async def read_sheet_data(self) -> List[List[str]]:
        """读取飞书表格数据"""
        token = await self.get_tenant_access_token()
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_id}/values/{self.sheet_name}!{self.data_range}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        log_info(f"读取表格数据: {self.sheet_name}!{self.data_range}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"读取表格数据失败: {result.get('msg', '未知错误')}")
            
            values = result.get("data", {}).get("valueRange", {}).get("values", [])
            log_info(f"成功读取到 {len(values)} 行数据")
            log_debug(f"读取到的数据: {values[:5]}...")
            return values
    
    def _convert_row_to_dict(self, headers: List[str], row: List[Any], row_index: int) -> Dict[str, Any]:
        """将行数据转换为字典格式，使用表头作为key"""
        row_dict = {"row_index": row_index}
        
        # 确保行数据长度不超过表头长度
        max_len = min(len(headers), len(row))
        
        for i in range(max_len):
            header = str(headers[i]).strip()
            value = row[i] if row[i] is not None else ""
            # 对于数字类型，保持原类型；对于字符串类型，转换为字符串并去除空格
            if isinstance(value, (int, float)):
                row_dict[header] = value
            else:
                row_dict[header] = str(value).strip()
        
        return row_dict

    async def get_filtered_rows(self) -> List[Dict[str, Any]]:
        """获取符合条件的行数据：系统配置模版列不为空，且已配置列为空
        
        返回格式：
        [
            {
                "row_index": 6,
                "序号": 5,
                "商品id": "10000257004966",
                "聚宝赞商品id": 6084467,
                "商品名称": "cs智利无核大西梅干400g/袋测试",
                "零售价": 49.8,
                "机构总佣金比": 0.1,
                "社群佣金比": "J6*30/100",
                "平台毛利比": "J6*45/100",
                "阶梯权重": "J6*60/100",
                "分润预留": "E6*F6",
                "系统配置模版": "云集自营-买手",
                "已配置分润方案": ""
            },
            ...
        ]
        """
        values = await self.read_sheet_data()
        
        if not values:
            log_info("表格为空，没有找到任何数据")
            return []
        
        # 假设第一行是标题行
        headers = values[0] if values else []
        if len(headers) < 12:
            raise Exception(f"表格列数不足，预期至少12列，实际只有{len(headers)}列")
        
        # 系统配置模版和已配置列的名称
        system_config_header = "系统配置模版"
        configured_header = "已配置分润方案"
        
        filtered_rows = []
        
        for row_index, row in enumerate(values[1:], start=2):  # 从第2行开始（跳过标题行）
            # 确保行有足够的列
            if len(row) < len(headers):
                # 补充空值到与表头长度一致
                row = row + [None] * (len(headers) - len(row))
            
            # 转换为字典格式
            row_dict = self._convert_row_to_dict(headers, row, row_index)
            
            # 获取系统配置模版和已配置的值
            system_config_value = row_dict.get(system_config_header, "")
            configured_value = row_dict.get(configured_header, "")
            
            # 系统配置模版不为空，且已配置为空
            if system_config_value and not configured_value:
                filtered_rows.append(row_dict)
        
        log_info(f"找到 {len(filtered_rows)} 行符合条件的数据")
        return filtered_rows
    
    def get_column_letter(self, col_name: str) -> str:
        """根据列名获取列字母
        
        Args:
            col_name: 列名，如"已配置分润方案"
            
        Returns:
            str: 列字母，如"L"
        """
        if col_name not in self.column_mapping:
            raise ValueError(f"未知的列名: {col_name}，支持的列名: {list(self.column_mapping.keys())}")
        return self.column_mapping[col_name]
    
    async def find_row_by_product_id(self, product_id: str) -> Optional[int]:
        """根据商品ID查找对应的行号
        
        Args:
            product_id: 商品ID
            
        Returns:
            Optional[int]: 找到的行号（Excel中的行号），未找到返回None
        """
        values = await self.read_sheet_data()
        
        if not values:
            return None
        
        # 使用表头来找商品ID列
        headers = values[0] if values else []
        
        for row_index, row in enumerate(values[1:], start=2):  # 从第2行开始（跳过标题行）
            # 转换为字典格式
            row_dict = self._convert_row_to_dict(headers, row, row_index)
            
            # 获取商品ID值
            row_product_id = str(row_dict.get("聚宝赞商品id", "")).strip()
            if row_product_id == str(product_id):
                log_info(f"找到商品ID {product_id} 对应的行号: {row_index}")
                return row_index
        
        log_info(f"未找到商品ID {product_id} 对应的行")
        return None
    
    async def update_cell_by_row_and_column(self, row_index: int, col_name: str = "已配置分润方案", value: str = "Y") -> bool:
        """更新指定行和列的单元格值
        
        Args:
            row_index: Excel中的行号（从1开始）
            col_name: 列名，默认为"已配置分润方案"
            value: 要设置的值，默认为"Y"
            
        Returns:
            bool: 更新是否成功
        """
        token = await self.get_tenant_access_token()
        
        # 获取列字母
        col_letter = self.get_column_letter(col_name)
        cell_range = f"{self.sheet_name}!{col_letter}{row_index}:{col_letter}{row_index}"
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_id}/values"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "valueRange": {
                "range": cell_range,
                "values": [[value]]
            }
        }
        
        log_info(f"更新单元格 {cell_range} ({col_name}列) 的值为: {value}")
        
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                log_error(f"更新单元格失败: {result.get('msg', '未知错误')}")
                return False
            
            log_info(f"成功更新单元格 {cell_range}")
            return True
    
    async def update_configured_status(self, row_index: int, value: str = "Y") -> bool:
        """更新指定行的已配置状态（兼容性方法）
        
        Args:
            row_index: Excel中的行号（从1开始）
            value: 要设置的值，默认为"Y"
            
        Returns:
            bool: 更新是否成功
        """
        return await self.update_cell_by_row_and_column(row_index, "已配置分润方案", value)
    
    async def update_by_product_id(self, product_id: str, col_name: str = "已配置分润方案", value: str = "Y") -> bool:
        """根据商品ID更新指定列的值
        
        Args:
            product_id: 商品ID
            col_name: 要更新的列名，默认为"已配置分润方案"
            value: 要设置的值，默认为"Y"
            
        Returns:
            bool: 更新是否成功
        """
        log_debug(f"开始根据商品ID {product_id} 更新列 {col_name} 的值为: {value}")
        # 先根据商品ID找到行号
        row_index = await self.find_row_by_product_id(product_id)
        
        if row_index is None:
            log_error(f"未找到商品ID {product_id} 对应的行，无法更新")
            return False
        
        # 更新指定行和列的值
        return await self.update_cell_by_row_and_column(row_index, col_name, value)
    
    async def batch_update_configured_status(self, row_indices: List[int], value: str = "Y") -> Dict[int, bool]:
        """批量更新多行的已配置状态
        
        Args:
            row_indices: 要更新的行号列表
            value: 要设置的值，默认为"Y"
            
        Returns:
            Dict[int, bool]: 每行的更新结果
        """
        results = {}
        
        for row_index in row_indices:
            try:
                success = await self.update_configured_status(row_index, value)
                results[row_index] = success
                # 添加小延时避免请求过快
                await asyncio.sleep(0.1)
            except Exception as e:
                log_error(f"更新行 {row_index} 失败: {str(e)}")
                results[row_index] = False
        
        return results