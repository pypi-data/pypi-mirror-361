import r3frame2 as r3

class Playground(r3.app.R3scene):
    def __init__(self, app):
        super().__init__(app)

    def init(self):
        # load an R3entity (0.0.1)
        self.database.load_entity("enemy", [200, 200], rgba=[0, 0, 255])
        self.database.load_entity("player", [100, 100], rgba=[255, 0, 0])
        
        # query said entity and toggle physics on it (0.0.5)
        self.enemy = self.database.query_entity("enemy")
        self.player = self.database.query_entity("player")
        
        # configure our entity physics (0.0.5)
        self.physics.toggle_transform(self.enemy)
        self.physics.toggle_transform(self.player)

        self.physics.toggle_collision(self.enemy, [8, 8], [16, 16])
        self.physics.toggle_collision(self.player, [0, 0], [32, 32])

    def exit(self): pass

    def events(self):
        # toggle `show colliders` (0.0.5)
        if self.app.events.key_pressed(self.app.keyboard.C):
            if self.renderer.get_flag(r3.R3flags.renderer.SHOW_COLLIDERS):
                self.renderer.rem_flag(r3.R3flags.renderer.SHOW_COLLIDERS)
            else: self.renderer.set_flag(r3.R3flags.renderer.SHOW_COLLIDERS)
        
        # handle movement along the x-axis (0.0.1)
        if self.app.events.key_held(self.app.keyboard.A):
            self.physics.set_velocity(self.player, dx=-100)
        if self.app.events.key_held(self.app.keyboard.D):
            self.physics.set_velocity(self.player, dx=100)

        # handle movement along the y-axis (0.0.1)
        if self.app.events.key_held(self.app.keyboard.W):
            self.physics.set_velocity(self.player, dy=-100)
        if self.app.events.key_held(self.app.keyboard.S):
            self.physics.set_velocity(self.player, dy=100)

    def update(self, dt: float): pass

    def render(self):
        # queue a render call for our player (0.0.4)
        self.renderer.queue(self.player)
        
        # render our enemy immediately (0.0.4)
        self.renderer.render(self.enemy)

class PlaygroundApp(r3.app.R3app):
    def __init__(self):
        super().__init__(title="R3 Playground", clock_target=144)

    def init(self):
        self.add_scene("player", Playground)
        self.set_scene("player")

    def exit(self): pass

def main() -> None:
    PlaygroundApp().run()
