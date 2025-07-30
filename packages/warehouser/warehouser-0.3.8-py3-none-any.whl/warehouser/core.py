from logging import Logger
import os
from typing import Optional

from sqlalchemy import MetaData
from warehouser.db_config import WarehouserConfig, config_from_dict
from warehouser.manager import Warehouser



def make_warehouser(config: dict|WarehouserConfig, metadata: MetaData, *,
                    partition_size:int = 5000,
                    safe: bool = True,
                    logger: Optional[Logger] = None) -> Warehouser:
    if isinstance(config, dict):
        _config = config_from_dict(config)
    else:
        _config = config
    return Warehouser(_config.database, _config, metadata,
                     partition_size=partition_size,
                     logger=logger,
                     safe=safe)