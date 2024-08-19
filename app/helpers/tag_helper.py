class TagHelper:

    @staticmethod
    def extract(value: str | None) -> list:
        tags = []
        if value:
            tags = value.split(",")
            tags = [tag.strip().lower() for tag in tags]
            tags = list(set([tag for tag in tags if tag]))
        return tags
