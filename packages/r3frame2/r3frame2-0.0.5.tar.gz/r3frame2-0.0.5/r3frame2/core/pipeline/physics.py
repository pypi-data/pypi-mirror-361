from ..atom import R3atom, R3private
from ..status import R3status
from ..log import R3logger
from ..globals import pg
# from ..utils import 
import r3frame2 as r3

class R3physics(R3atom):
    def __init__(
            self,
            app: "r3.app.R3app",
    ) -> None:
        super().__init__()
        __meta__: dict = {
            "_count": 0,
        }

        self.damp_value = 4
        self.damp_threshold = 0.8
        
        self.app: r3.app.R3app = app
        self.database: r3.resource.R3database = app.database
        
        self.transform_data: dict[r3.resource.R3entity, list] = { k: v for k,v in __meta__.items() }
        self.collision_data: dict[r3.resource.R3entity, r3.resource.R3aabb] = { k: v for k,v in __meta__.items() }
        
        self._freeze()

    def _valid_entity(self, cache: dict, entity: "r3.resource.R3entity") -> int:
        if not isinstance(entity, r3.resource.R3entity):
            return R3status.physics.ENTITY_INVALID
        if not cache.get(entity, 0):
            return R3status.physics.ENTITY_NOT_FOUND
        else: return R3status.physics.ENTITY_FOUND


    def toggle_transform(self, entity: "r3.resource.R3entity") -> int:
        if self._valid_entity(self.transform_data, entity) == R3status.physics.ENTITY_FOUND:
            self.transform_data.pop(entity)
            R3logger.debug(f"[R3physics] toggled entity physics off: (entity){entity.tag}")
            return R3status.physics.ENTITY_FOUND
        elif self._valid_entity(self.transform_data, entity) == R3status.physics.ENTITY_NOT_FOUND:
            self.transform_data[entity] = [entity, [0.0, 0.0]]
            R3logger.debug(f"[R3physics] toggled entity physics on: (entity){entity.tag}")
            return R3status.physics.ENTITY_FOUND
        else:
            R3logger.error(f"[R3physics] entity not found: (entity){entity.tag}")
            return R3status.physics.ENTITY_NOT_FOUND

    def toggle_collision(self, entity: "r3.resource.R3entity", pos: list[int] = None, size: list[int] = None) -> int:
        if self._valid_entity(self.collision_data, entity) == R3status.physics.ENTITY_FOUND:
            self.database.unload_aabb(f"{entity.tag}.aabb")
            self.collision_data.pop(entity)
            R3logger.debug(f"[R3physics] toggled entity collision off: (entity){entity.tag}")
            return R3status.physics.ENTITY_FOUND
        elif self._valid_entity(self.collision_data, entity) == R3status.physics.ENTITY_NOT_FOUND:
            if not isinstance(pos, list) or not isinstance(size, list):
                self.database.unload_aabb(f"{entity.tag}.aabb")
                return R3status.physics.ENTITY_NOT_FOUND

            self.database.load_aabb(f"{entity.tag}.aabb", entity, pos, size)
            self.collision_data[entity] = [entity, self.database.query_aabb(f"{entity.tag}.aabb")]
            R3logger.debug(f"[R3physics] toggled entity collision on: (entity){entity.tag}")
            return R3status.physics.ENTITY_FOUND
        else:
            R3logger.error(f"[R3physics] entity not found: (entity){entity.tag}")
            return R3status.physics.ENTITY_NOT_FOUND


    def get_velocity(self, entity: "r3.resource.R3entity") -> list[float]:
        if self._valid_entity(self.transform_data, entity) != R3status.physics.ENTITY_FOUND:
            R3logger.error(f"[R3physics] entity not found: (entity){entity.tag}")
        else: return self.transform_data[entity][1][0]

    def get_direction(self, entity: "r3.resource.R3entity") -> list[float]:
        if self._valid_entity(self.transform_data, entity) != R3status.physics.ENTITY_FOUND:
            R3logger.error(f"[R3physics] entity not found: (entity){entity.tag}")
        else: return [(self.transform_data[entity][1][0] > 0) - (self.transform_data[entity][1][0] < 0),
                      (self.transform_data[entity][1][1] > 0) - (self.transform_data[entity][1][1] < 0)]


    def set_velocity(self, entity: "r3.resource.R3entity", dx: float = None, dy: float = None) -> bool:
        if self._valid_entity(self.transform_data, entity) != R3status.physics.ENTITY_FOUND:
            R3logger.error(f"[R3physics] entity not found: (entity){entity.tag}")
        else:
            if dx is not None: self.transform_data[entity][1][0] = dx
            if dy is not None: self.transform_data[entity][1][1] = dy


    @R3private
    def _resolve_collision_x(self, entity: "r3.resource.R3entity", neighbors: list["r3.resource.R3entity"]) -> None:
        if self._valid_entity(self.collision_data, entity) != R3status.physics.ENTITY_FOUND:
            return
        vel = self.transform_data[entity][1]
        a1 = self.collision_data[entity][1]
        r1 = a1.rect
        for entity2, a2 in neighbors:
            if entity2 == entity: continue
            r2 = a2.rect
            if r1.colliderect(r2):
                if vel[0] > 0:
                    entity.pos[0] = r2.left - r1.width
                elif vel[0] < 0:
                    entity.pos[0] = r2.right
                vel[0] = 0

    @R3private
    def _resolve_collision_y(self, entity: "r3.resource.R3entity", neighbors: list["r3.resource.R3entity"]) -> None:
        if self._valid_entity(self.collision_data, entity) != R3status.physics.ENTITY_FOUND:
            return
        vel = self.transform_data[entity][1]
        a1 = self.collision_data[entity][1]
        r1 = a1.rect
        for entity2, a2 in neighbors:
            if entity2 == entity: continue
            r2 = a2.rect
            if r1.colliderect(r2):
                if vel[1] > 0:
                    entity.pos[1] = r2.top - r1.height
                elif vel[1] < 0:
                    entity.pos[1] = r2.bottom
                vel[1] = 0

    @R3private
    def update(self, dt: float) -> None:
        entities = [self.transform_data[e] for e in self.transform_data if e != "_count"]
        neighbors = [self.collision_data[e] for e in self.collision_data if e != "_count"]

        for e, v in entities:
            # TODO: implement partitions for spatial queries around each entity!
            e.pos[0] += v[0] * dt
            self._resolve_collision_x(e, neighbors)
            e.pos[1] += v[1] * dt
            self._resolve_collision_y(e, neighbors)
            
            v[0] *= (1 - self.damp_value * dt)
            v[1] *= (1 - self.damp_value * dt)

            if abs(self.transform_data[e][1][0]) < self.damp_threshold: v[0] = 0
            if abs(self.transform_data[e][1][1]) < self.damp_threshold: v[1] = 0
