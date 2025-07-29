from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "seppl.io.Reader": [
            "adc.redis.reader",
        ],
        "seppl.io.Filter": [
            "adc.redis.filter",
        ],
        "seppl.io.Writer": [
            "adc.redis.writer",
        ],
    }
