import math
from game.keybinding import Bindings

class Player:
    def __init__(self, save_data: dict):
        self.max_stamina = save_data['player']['max_stamina']
        self.stamina     = self.max_stamina // 4
        self.max_health  = save_data['player']['max_health']
        self.health      = save_data['player']['health']

        self.xp          = save_data['player']['xp']
        self.location    = [save_data['player']['x'], save_data['player']['y']]
        self.alive       = True

        self.velocity      = [0, 0]
        self.selected_tile = [None, None]
    
    def tick(self, keys_pressed: dict, environment: dict) -> None:
        speed = 0.008 * environment['time_delta']
        self.velocity = [0, 0]
        if keys_pressed.get(Bindings.get("FORWARD"), False):
            self.velocity[1] = -speed
        if keys_pressed.get(Bindings.get("BACKWARD"), False):
            self.velocity[1] = speed
        if keys_pressed.get(Bindings.get("LEFT"), False):
            self.velocity[0] = -speed
        if keys_pressed.get(Bindings.get("RIGHT"), False):
            self.velocity[0] = speed

        if keys_pressed.get(Bindings.get("SPRINT"), False) and (self.velocity[0] != 0 or self.velocity[1] != 0):
            if self.stamina - 0.02 * environment['time_delta'] > 0:
                self.velocity[0] *= 2
                self.velocity[1] *= 2
                self.stamina -= 0.03 * environment['time_delta']

        # make diagonal movement look less like teleporting
        if self.velocity[0] != 0 and self.velocity[1] != 0:
            self.velocity[0] /= math.sqrt(2)
            self.velocity[1] /= math.sqrt(2)

        # update player position
        self.location = (self.location[0] + self.velocity[0], self.location[1] + self.velocity[1])        

                # regenerate stamina if below max
        if self.stamina < self.max_stamina:
            self.stamina += 0.01 * environment['time_delta']
            self.stamina = min(self.max_stamina, self.stamina)