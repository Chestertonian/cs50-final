# game/combat/combat_state.py

class CombatState:

    def __init__(self):
        self.primary_target_id = None   # NPC instance id
        self.attacker_ids = []          # all NPC instance ids attacking the player

    def start_combat(self, npc_id):
        if npc_id not in self.attacker_ids:
            self.attacker_ids.append(npc_id)
        if self.primary_target_id is None:
            self.primary_target_id = npc_id

    def end_combat(self):
        self.primary_target_id = None
        self.attacker_ids = []

    def remove_npc(self, npc_id):
        self.attacker_ids = [id for id in self.attacker_ids if id != npc_id]
        if self.primary_target_id == npc_id:
            self.primary_target_id = self.attacker_ids[0] if self.attacker_ids else None

    def is_in_combat(self):
        return len(self.attacker_ids) > 0

    def switch_target(self, npc_id):
        if npc_id in self.attacker_ids:
            self.primary_target_id = npc_id