# coding:utf-8
#
# unike/utils/WandbLogger.py
#
# created by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on Jan 1, 2024
# updated by LuYF-Lemon-love <luyanfeng_nlp@qq.com> on Feb 24, 2024
#
# 该脚本定义了 WandbLogger 类.

"""
WandbLogger - 使用 Weights and Biases 记录实验结果。
"""

import typing
import wandb

class WandbLogger:

    """使用 `Weights and Biases <https://docs.wandb.ai/>`_ 记录实验结果。"""

    def __init__(self,
        project: str ="pybind11-ke",
        name: str = "transe",
        config: dict[str, typing.Any] | None = None):

        """创建 WandbLogger 对象。
        
        :param project: wandb 的项目名称
        :type project: str
        :param name: wandb 的 run name
        :type name: str
        :param config: wandb 的项目配置如超参数。
        :type config: dict[str, typing.Any] | None
        """

        wandb.login()
        wandb.init(project=project, name=name, config=config)
        
        #: config 的副本
        self.config: dict = wandb.config
    
    def finish(self):

        """关闭 wandb"""

        wandb.finish()