
 
 

	





 



	



 




	


 


	




 




	


 




	


 




	


 


import random
import sys
from collections import defaultdict

# ======================
# CONFIGURATION & DATA
# ======================

# Zones (simplified modular board)
ZONES = {
    "Shed": {"resources": ["Wood", "Fibre"]},
    "Grassland": {"resources": ["Fibre", "Nectar"]},
    "Flowerbed": {"resources": ["Fibre", "Nectar"]},
    "Vegetable Patch": {"resources": ["Nectar", "Water"]},
    "Patio": {"resources": ["Wood", "Water"]},
    "Pond": {"resources": ["Water"]},
    "Oak Tree": {"resources": []}  # Victory zone
}

BOARD_PATH = ["Shed", "Grassland", "Flowerbed", "Vegetable Patch", "Patio", "Pond", "Oak Tree"]

# Wee Folk Characters
WEE_FOLK = {
    "Scavenger": {"ability": "Draw 1 extra resource when scavenging"},
    "Scout": {"ability": "Move 3 spaces instead of 2"},
    "Builder": {"ability": "Shelters cost 1 less Wood and Fibre"},
    "Medic": {"ability": "Can heal without items; +1 to healing"}
}

# Blueprint Cards
BLUEPRINTS = {
    "Grass-Blade Sword": {"cost": {"Fibre": 2}, "effect": "Combat: +2 to roll"},
    "Acorn-Cap Helmet": {"cost": {"Wood": 1, "Fibre": 1}, "effect": "Defense: Reduce damage by 1"},
    "Spider-Silk Grappling Hook": {"cost": {"Fibre": 3}, "effect": "Ignore movement penalties in Flowerbed/Pond"},
    "Distraction Lure": {"cost": {"Nectar": 2}, "effect": "Evade Hungry Cat automatically"},
    "Dewdrop Lantern": {"cost": {"Glass": 1, "Nectar": 1}, "effect": "Ignore night penalties (not implemented yet)"}
}

# Danger Deck
DANGER_DECK = [
    # Creatures
    {"type": "creature", "name": "Giant Ant Swarm", "defense": 8, "damage": 2},
    {"type": "creature", "name": "Hunting Spider", "defense": 10, "damage": 3},
    {"type": "creature", "name": "Buzzing Wasp", "defense": 6, "damage": 1},
    {"type": "creature", "name": "Hungry Cat", "defense": 12, "damage": 4, "persistent": True},
    {"type": "creature", "name": "Swooping Bird", "defense": 9, "damage": 3},
    {"type": "creature", "name": "Slithering Snake", "defense": 11, "damage": 3},
    # Environmental
    {"type": "environment", "name": "Sudden Shower", "effect": "All Wood/Fibre unusable next round; movement -1"},
    {"type": "environment", "name": "Weed Killer Spray", "effect": "Lose 1 random resource per player"},
    {"type": "environment", "name": "Falling Acorn", "effect": "One random player takes 2 damage"},
    {"type": "environment", "name": "Cat Stalking", "effect": "Place Hungry Cat near nearest player"}
]

# Resources
ALL_RESOURCES = ["Wood", "Fibre", "Nectar", "Water"]

# ======================
# GAME STATE CLASSES
# ======================

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.zone = "Shed"
        self.health = 5
        self.resources = defaultdict(int)
        self.items = []
        self.shelter_built = False

    def __str__(self):
        return f"{self.name} ({self.role}) - HP: {self.health}, Zone: {self.zone}"

class GameState:
    def __init__(self, num_players):
        self.players = []
        self.weather_track = 0
        self.max_weather = 10  # Storm hits at 10
        self.danger_deck = DANGER_DECK.copy()
        random.shuffle(self.danger_deck)
        self.hungry_cat_present = False
        self.current_round = 0
        self.game_over = False
        self.victory = False

        # Create players
        roles = list(WEE_FOLK.keys())
        for i in range(num_players):
            name = input(f"Enter name for Player {i+1}: ")
            role = roles[i % len(roles)]
            self.players.append(Player(name, role))

    def advance_weather(self):
        self.weather_track += 1
        if self.weather_track >= self.max_weather:
            print("\n⛈️  THE STORM HAS ARRIVED! The garden is flooded. You failed to reach the Oak Tree in time.")
            self.game_over = True

    def draw_danger(self):
        if not self.danger_deck:
            self.danger_deck = DANGER_DECK.copy()
            random.shuffle(self.danger_deck)
        return self.danger_deck.pop()

    def resolve_danger(self, card):
        print(f"\n⚠️  DANGER: {card['name']}!")
        if card["type"] == "creature":
            self.handle_creature(card)
        elif card["type"] == "environment":
            print(f"Effect: {card['effect']}")
            # Simplified: just notify; full effects would require state flags
            if "Cat Stalking" in card["name"]:
                self.hungry_cat_present = True

    def handle_creature(self, creature):
        print(f"\n{creature['name']} appears! Defense: {creature['defense']}, Damage: {creature['damage']}")
        combatants = [p for p in self.players if p.zone == self.get_current_zone() and p.health > 0]
        if not combatants:
            print("No players in this zone to fight!")
            return

        print("Choose action: (1) Combat, (2) Evade")
        choice = input("> ").strip()
        if choice == "1":
            self.combat(combatants, creature)
        elif choice == "2":
            self.evade(combatants[0], creature)
        else:
            print("Invalid choice. Defaulting to Combat.")
            self.combat(combatants, creature)

    def combat(self, combatants, creature):
        total_roll = 0
        for p in combatants:
            roll = random.randint(1, 6)
            bonus = 0
            if "Grass-Blade Sword" in p.items:
                bonus += 2
            total_roll += roll + bonus
            print(f"{p.name} rolls {roll} +{bonus} = {roll + bonus}")
        print(f"Total combat roll: {total_roll}")
        if total_roll >= creature["defense"]:
            print("✅ You defeated the creature!")
            if creature.get("persistent"):
                self.hungry_cat_present = False
        else:
            damage = creature["damage"]
            print(f"❌ The creature attacks! Each player in zone takes {damage} damage.")
            for p in combatants:
                p.health -= damage
                if p.health <= 0:
                    print(f"{p.name} has been defeated!")

    def evade(self, player, creature):
        roll = random.randint(1, 6)
        target = 4  # Base evade target
        if "Spider-Silk Grappling Hook" in player.items:
            target -= 1
        print(f"{player.name} tries to evade... rolls {roll} (needs {target}+)")
        if roll >= target:
            print("✅ Successfully evaded!")
        else:
            print(f"❌ Failed! Takes {creature['damage']} damage.")
            player.health -= creature["damage"]
            if player.health <= 0:
                print(f"{player.name} has been defeated!")

    def get_current_zone(self):
        # Simplified: assume all players are together (co-op)
        return self.players[0].zone

    def check_victory(self):
        for p in self.players:
            if p.zone == "Oak Tree" and p.health > 0:
                print(f"\n🎉 {p.name} has reached the Oak Tree! The emergency signal is lit. YOU WIN!")
                self.victory = True
                self.game_over = True
                return True
        return False

    def check_defeat(self):
        if all(p.health <= 0 for p in self.players):
            print("\n💀 All Wee Folk have fallen. The garden has claimed you.")
            self.game_over = True
            return True
        return False

# ======================
# ACTION FUNCTIONS
# ======================

def move_player(player, game_state):
    current_index = BOARD_PATH.index(player.zone)
    max_move = 3 if player.role == "Scout" else 2
    print(f"\nCurrent zone: {player.zone}. You can move up to {max_move} steps forward.")
    steps = input(f"How many steps to move (0-{min(max_move, len(BOARD_PATH)-1 - current_index)})? ")
    try:
        steps = int(steps)
        if 0 <= steps <= max_move and current_index + steps < len(BOARD_PATH):
            player.zone = BOARD_PATH[current_index + steps]
            print(f"Moved to {player.zone}.")
        else:
            print("Invalid move.")
    except ValueError:
        print("Invalid input.")

def scavenge(player, game_state):
    zone = ZONES[player.zone]
    draws = 3
    if player.role == "Scavenger":
        draws += 1
    for _ in range(draws):
        resource = random.choice(zone["resources"]) if zone["resources"] else random.choice(ALL_RESOURCES)
        player.resources[resource] += 1
    print(f"Scavenged {draws} resources! Current: {dict(player.resources)}")

def craft(player, game_state):
    print("\nAvailable Blueprints:")
    for i, (name, bp) in enumerate(BLUEPRINTS.items(), 1):
        cost_str = ", ".join([f"{k}:{v}" for k, v in bp["cost"].items()])
        print(f"{i}. {name} - Cost: {cost_str} | Effect: {bp['effect']}")
    choice = input("Choose a blueprint to craft (or 0 to cancel): ")
    try:
        idx = int(choice) - 1
        if idx < 0:
            return
        name = list(BLUEPRINTS.keys())[idx]
        bp = BLUEPRINTS[name]
        # Check resources
        can_craft = True
        for res, qty in bp["cost"].items():
            if player.resources[res] < qty:
                can_craft = False
        if can_craft:
            for res, qty in bp["cost"].items():
                player.resources[res] -= qty
            player.items.append(name)
            print(f"✅ Crafted {name}!")
        else:
            print("❌ Not enough resources.")
    except (ValueError, IndexError):
        print("Invalid choice.")

def build_shelter(player, game_state):
    wood_cost = 2 if player.role == "Builder" else 3
    fibre_cost = 1 if player.role == "Builder" else 2
    if player.resources["Wood"] >= wood_cost and player.resources["Fibre"] >= fibre_cost:
        player.resources["Wood"] -= wood_cost
        player.resources["Fibre"] -= fibre_cost
        player.shelter_built = True
        print("🏡 Shelter built! You gain +1 defense next danger.")
    else:
        print("❌ Not enough Wood or Fibre.")

def aid_trade(player, game_state):
    allies = [p for p in game_state.players if p != player and p.zone == player.zone and p.health > 0]
    if not allies:
        print("No allies in your zone to aid or trade with.")
        return
    print("\nAllies in zone:")
    for i, ally in enumerate(allies, 1):
        print(f"{i}. {ally}")
    print("Actions: (1) Heal, (2) Trade")
    action = input("> ")
    if action == "1":
        if player.role == "Medic" or "Medic Kit" in player.items:
            target = allies[0]  # Simplified: heal first ally
            heal_amt = 2 if player.role == "Medic" else 1
            target.health = min(5, target.health + heal_amt)
            print(f"❤️  Healed {target.name} for {heal_amt} HP!")
        else:
            print("You need to be Medic or have a healing item.")
    elif action == "2":
        target = allies[0]
        print(f"Your resources: {dict(player.resources)}")
        print(f"{target.name}'s resources: {dict(target.resources)}")
        give = input("Resource to give: ")
        if give in player.resources and player.resources[give] > 0:
            player.resources[give] -= 1
            target.resources[give] += 1
            print(f"Traded 1 {give} to {target.name}.")
        else:
            print("You don't have that resource.")

# ======================
# MAIN GAME LOOP
# ======================

def main():
    print("🌿 Welcome to THE GREAT GARDEN CROSSING! 🌿")
    num = int(input("How many players (1-4)? "))
    if not (1 <= num <= 4):
        print("Invalid player count.")
        return

    game = GameState(num)
    print("\nGame Setup Complete!")
    print("Your goal: Reach the Oak Tree before the storm (10 rounds)!")
    input("Press Enter to begin...")

    while not game.game_over:
        game.current_round += 1
        print(f"\n========== ROUND {game.current_round} ==========")
        print(f"Weather Track: {game.weather_track}/{game.max_weather}")

        # Phase 1: Player Actions
        for player in game.players:
            if player.health <= 0:
                continue
            print(f"\n--- {player.name}'s Turn ---")
            print(player)
            actions = 3
            while actions > 0:
                print(f"\nActions remaining: {actions}")
                print("1. Move\n2. Scavenge\n3. Craft\n4. Build Shelter\n5. Aid/Trade\n6. End Turn")
                choice = input("> ").strip()
                if choice == "1":
                    move_player(player, game)
                elif choice == "2":
                    scavenge(player, game)
                elif choice == "3":
                    craft(player, game)
                elif choice == "4":
                    build_shelter(player, game)
                elif choice == "5":
                    aid_trade(player, game)
                elif choice == "6":
                    break
                else:
                    print("Invalid choice.")
                    continue
                actions -= 1

        # Check victory after actions
        if game.check_victory():
            break
        if game.check_defeat():
            break

        # Phase 2: Garden Strikes Back
        print("\n--- THE GARDEN STRIKES BACK ---")
        game.advance_weather()
        if game.game_over:
            break
        danger = game.draw_danger()
        game.resolve_danger(danger)

        # Check again after danger
        if game.check_victory():
            break
        if game.check_defeat():
            break

    if game.victory:
        print("\n🌟 You survived the Great Garden Crossing! 🌟")
    else:
        print("\n🌧️  Game Over. Better luck next autumn...")

if __name__ == "__main__":
    main()
	



 


	




 
