from typing import List, Dict


def list_classes() -> Dict[str, List[str]]:
    return {
        "seppl.io.Reader": [
            "idc.paddle.reader.imgcls",
            "idc.paddle.reader.imgseg",
        ],
        "seppl.io.Writer": [
            "idc.paddle.writer.imgcls",
            "idc.paddle.writer.imgseg",
        ],
    }
