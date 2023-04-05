class Player:
    def __init__(self):
        self.max_stamina = 100
        self.stamina     = self.max_stamina // 4
        self.health      = 100
        self.max_health  = 100

        self.xp          = 0
        self.location    = [0, 0]
        self.alive       = True

        self.selected_tile = [None, None]