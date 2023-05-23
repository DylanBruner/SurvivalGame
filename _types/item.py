class Item:
    def __init__(self, item_id: int, count: int):
        self.item_id = item_id
        self.count   = count 
        self.lore: list[str] = []

    def setLore(self, lore: list[str]) -> None:
        self.lore = lore

    def toTuple(self) -> tuple:
        return (self.item_id, self.count)
    
    def __repr__(self) -> str:
        return f"Item(id={self.item_id}, count={self.count})"