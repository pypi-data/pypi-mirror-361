#!/usr/bin/env python3
"""
Game development example using publishsub library
"""

import publishsub as pubsub
import time
import random

class GameEngine:
    def __init__(self):
        self.players = {}
        self.enemies = []
        self.game_running = False
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup all game event handlers"""
        pubsub.subscribe("player_join", self.on_player_join)
        pubsub.subscribe("player_leave", self.on_player_leave)
        pubsub.subscribe("enemy_spawn", self.on_enemy_spawn)
        pubsub.subscribe("player_attack", self.on_player_attack)
        pubsub.subscribe("enemy_death", self.on_enemy_death)
        pubsub.subscribe("game_over", self.on_game_over)
    
    def on_player_join(self, data):
        player_id = data['id']
        player_name = data['name']
        self.players[player_id] = {
            'name': player_name,
            'health': 100,
            'score': 0
        }
        print(f"🎮 Player {player_name} (ID: {player_id}) joined the game!")
        print(f"   Current players: {len(self.players)}")
    
    def on_player_leave(self, data):
        player_id = data['id']
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            del self.players[player_id]
            print(f"👋 Player {player_name} left the game!")
    
    def on_enemy_spawn(self, data):
        enemy = {
            'id': data['id'],
            'type': data['type'],
            'x': data['x'],
            'y': data['y'],
            'health': data['health']
        }
        self.enemies.append(enemy)
        print(f"👹 Enemy spawned: {enemy['type']} at ({enemy['x']}, {enemy['y']})")
    
    def on_player_attack(self, data):
        player_id = data['player_id']
        enemy_id = data['enemy_id']
        damage = data['damage']
        
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            enemy = next((e for e in self.enemies if e['id'] == enemy_id), None)
            
            if enemy:
                enemy['health'] -= damage
                print(f"⚔️  {player_name} attacks {enemy['type']} for {damage} damage!")
                
                if enemy['health'] <= 0:
                    # Enemy dies
                    pubsub.publish("enemy_death", {
                        'enemy_id': enemy_id,
                        'killer_id': player_id,
                        'enemy_type': enemy['type']
                    })
    
    def on_enemy_death(self, data):
        enemy_id = data['enemy_id']
        killer_id = data['killer_id']
        enemy_type = data['enemy_type']
        
        # Remove enemy from list
        self.enemies = [e for e in self.enemies if e['id'] != enemy_id]
        
        # Award points to player
        if killer_id in self.players:
            self.players[killer_id]['score'] += 100
            killer_name = self.players[killer_id]['name']
            print(f"💀 {killer_name} killed a {enemy_type}! (+100 points)")
            print(f"   {killer_name}'s score: {self.players[killer_id]['score']}")
    
    def on_game_over(self, data):
        reason = data['reason']
        print(f"\n🏁 GAME OVER: {reason}")
        
        if self.players:
            # Show final scores
            print("\n📊 Final Scores:")
            sorted_players = sorted(self.players.items(), 
                                  key=lambda x: x[1]['score'], 
                                  reverse=True)
            
            for i, (player_id, player_data) in enumerate(sorted_players):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
                print(f"   {medal} {player_data['name']}: {player_data['score']} points")
        
        self.game_running = False

def simulate_game():
    """Simulate a simple game scenario"""
    print("=== Game Simulation with publishsub ===\n")
    
    # Create game engine
    game = GameEngine()
    game.game_running = True
    
    # Players join
    pubsub.publish("player_join", {"id": 1, "name": "Alice"})
    pubsub.publish("player_join", {"id": 2, "name": "Bob"})
    pubsub.publish("player_join", {"id": 3, "name": "Charlie"})
    
    time.sleep(1)
    
    # Spawn enemies
    enemies_data = [
        {"id": 101, "type": "Goblin", "x": 50, "y": 100, "health": 30},
        {"id": 102, "type": "Orc", "x": 150, "y": 200, "health": 50},
        {"id": 103, "type": "Dragon", "x": 300, "y": 400, "health": 100}
    ]
    
    for enemy in enemies_data:
        pubsub.publish("enemy_spawn", enemy)
        time.sleep(0.5)
    
    print(f"\n🎯 Battle Phase - {len(game.enemies)} enemies spawned!\n")
    
    # Simulate combat
    combat_actions = [
        {"player_id": 1, "enemy_id": 101, "damage": 20},
        {"player_id": 2, "enemy_id": 102, "damage": 25},
        {"player_id": 1, "enemy_id": 101, "damage": 15},  # Kills goblin
        {"player_id": 3, "enemy_id": 103, "damage": 30},
        {"player_id": 2, "enemy_id": 102, "damage": 30},  # Kills orc
        {"player_id": 3, "enemy_id": 103, "damage": 35},
        {"player_id": 1, "enemy_id": 103, "damage": 40},  # Kills dragon
    ]
    
    for action in combat_actions:
        pubsub.publish("player_attack", action)
        time.sleep(0.8)
    
    time.sleep(1)
    
    # End game
    pubsub.publish("game_over", {"reason": "All enemies defeated!"})
    
    print("\n=== Game Simulation Complete ===")

if __name__ == "__main__":
    simulate_game()