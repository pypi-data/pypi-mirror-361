"""
Creation date: 2025/7/10
Creation Time: 22:19
DIR PATH: ZfileSDK/front
Project Name: zfile_sdk
FILE NAME: direct_short_chain_module.py
Editor: cuckoo
"""

from ..utils.base import ApiClient, BaseClass, auto_args_from_model
from ..utils.models import AjaxJsonListBatchGenerateLinkResponse, BatchGenerateLinkRequest


class DirectShortChainModule(BaseClass):
    """直链短链模块，提供直链短链的相关功能。"""
    name = "DirectShortChainModule"

    def __init__(self, api_client: "ApiClient"):
        """初始化直链短链模块。

        Args:
            api_client: API 客户端实例，用于发送请求。
        """
        super().__init__(api_client, name=self.name)

    @auto_args_from_model(model=BatchGenerateLinkRequest)
    def short_link_batch_generate(self, *, data: BatchGenerateLinkRequest) -> AjaxJsonListBatchGenerateLinkResponse:
        """对指定存储源的某文件路径生成短链

        Args:
            data (BatchGenerateLinkRequest): 包含批量生成短链请求数据的模型。

        Returns:
            AjaxJsonListBatchGenerateLinkResponse: 包含生成的短链信息的响应对象。

        Raises:
            CustomException: 当请求失败或 API 返回错误时。
        """
        response = self.api_client.post(
            endpoint="/api/short-link/batch/generate",
            response_model=AjaxJsonListBatchGenerateLinkResponse,
            data=data
        )
        self._logger.info(f"[{response.trace_id}]生成短链: {response.msg}")
        return response
