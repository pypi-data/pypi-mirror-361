
from __future__ import annotations
from dataclasses import dataclass

from typing import List

import betterproto




@dataclass(eq=False, repr=False)
class Payload(betterproto.Message):
    _id: str = betterproto.string_field(1)
    cluster_id: str = betterproto.string_field(2)
    log: str = betterproto.string_field(3)
    masked_log: str = betterproto.string_field(4)
    anomaly_level: str = betterproto.string_field(5)
    log_type: str = betterproto.string_field(6)
    template_matched: str = betterproto.string_field(7)
    template_cluster_id: int = betterproto.int64_field(8)
    inference_model: str = betterproto.string_field(9)
    montylog_confidence: float = betterproto.float_field(10)
    pod_name: str = betterproto.string_field(11)
    namespace_name: str = betterproto.string_field(12)
    deployment: str = betterproto.string_field(13)
    service: str = betterproto.string_field(14)


@dataclass(eq=False, repr=False)
class PayloadList(betterproto.Message):
    items: List[Payload] = betterproto.message_field(1)



