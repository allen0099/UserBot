class RuleViolated(Exception):
    default_name: str = "臭臭小不點不喜歡寫規則名稱"
    default_detail: str = "你以為不寫就不知道誰是臭臭小不點了嗎"

    def __init__(self, name: str | None = None, detail: str | None = None):
        if not name:
            name = self.default_name
        if not detail:
            detail = self.default_detail

        self.name = name
        self.detail = detail
