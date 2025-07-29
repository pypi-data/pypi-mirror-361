from loguru import logger

class DataDriver():
    def __init__(self):
        logger.debug("sees")
    def me(self) -> str:
        return 'DUMMY'
    def connect(self, profile: dict) -> int:
        return 1
    def run(self, sql: str, do_return: bool = True, **kwargs):
        return []
    