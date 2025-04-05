import random
import time
import os
import json
from datetime import datetime

class TreasureHuntGame:
    """
    A text-based treasure hunt game that demonstrates various Python concepts.
    Players navigate through a grid-based map to find treasure while avoiding traps.
    """
    
    def __init__(self, player_name, grid_size=5):
        """
        Initialize the game with a player name and grid size.
        
        Args:
            player_name (str): Name of the player
            grid_size (int): Size of the square grid (default: 5)
        """
        self.player_name = player_name
        self.grid_size = grid_size
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.start_time = datetime.now()
        
        # Create empty grid
        self.grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Player position starts at random location
        self.player_pos = [random.randint(0, grid_size-1), random.randint(0, grid_size-1)]
        
        # Place treasure, traps, and power-ups
        self._place_items()
        
        # Dictionary to store items the player has collected
        self.inventory = {
            "keys": 0,
            "shields": 0,
            "maps": 0
        }
        
        # Create a log of game events
        self.game_log = []
        self._log_event("Game started")

    def _place_items(self):
        """Place treasure, traps, and power-ups randomly on the grid"""
        # Place treasures (T)
        self._place_random_items('T', 3)
        
        # Place traps (X)
        self._place_random_items('X', 4)
        
        # Place keys (K)
        self._place_random_items('K', 2)
        
        # Place shields (S)
        self._place_random_items('S', 2)
        
        # Place maps (M)
        self._place_random_items('M', 1)
        
        # Place the exit (E)
        self._place_random_items('E', 1)
    
    def _place_random_items(self, item_symbol, count):
        """
        Helper method to place items randomly on the grid.
        
        Args:
            item_symbol (str): Symbol representing the item
            count (int): Number of items to place
        """
        placed = 0
        while placed < count:
            x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            # Only place if cell is empty and not player's position
            if self.grid[y][x] == ' ' and [y, x] != self.player_pos:
                self.grid[y][x] = item_symbol
                placed += 1
    
    def _log_event(self, event):
        """
        Add an event to the game log with timestamp.
        
        Args:
            event (str): Description of the event
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.game_log.append(f"[{timestamp}] {event}")
    
    def display_grid(self, reveal_all=False):
        """
        Display the game grid in the console.
        
        Args:
            reveal_all (bool): Whether to reveal all items on the grid
        """
        # Clear the console (works on most systems)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n{self.player_name}'s Treasure Hunt Adventure")
        print(f"Score: {self.score} | Moves: {self.moves}")
        print(f"Inventory: Keys: {self.inventory['keys']} | Shields: {self.inventory['shields']} | Maps: {self.inventory['maps']}")
        
        # Print column numbers
        print("  " + " ".join(str(i) for i in range(self.grid_size)))
        
        # Print the grid with row numbers
        for i in range(self.grid_size):
            row = f"{i} "
            for j in range(self.grid_size):
                if [i, j] == self.player_pos:
                    row += "P "  # Player
                elif reveal_all:
                    row += self.grid[i][j] + " "  # Show actual item
                else:
                    # Show only adjacent cells or if player has used a map
                    is_adjacent = abs(i - self.player_pos[0]) <= 1 and abs(j - self.player_pos[1]) <= 1
                    if is_adjacent or self.inventory.get("used_map", False):
                        row += self.grid[i][j] + " "
                    else:
                        row += "? "  # Hidden
            print(row)
    
    def move_player(self, direction):
        """
        Move the player in the specified direction.
        
        Args:
            direction (str): One of 'up', 'down', 'left', 'right'
            
        Returns:
            bool: True if the move was successful, False otherwise
        """
        new_pos = self.player_pos.copy()
        
        # Calculate new position based on direction
        if direction == "up" and self.player_pos[0] > 0:
            new_pos[0] -= 1
        elif direction == "down" and self.player_pos[0] < self.grid_size - 1:
            new_pos[0] += 1
        elif direction == "left" and self.player_pos[1] > 0:
            new_pos[1] -= 1
        elif direction == "right" and self.player_pos[1] < self.grid_size - 1:
            new_pos[1] += 1
        else:
            print("You can't move in that direction!")
            self._log_event(f"Invalid move: {direction}")
            return False
        
        # Move is valid, increment moves counter
        self.moves += 1
        
        # Check what's in the new position
        item = self.grid[new_pos[0]][new_pos[1]]
        self._handle_item_interaction(item, new_pos)
        
        # Update player position
        self.player_pos = new_pos
        self._log_event(f"Moved {direction} to position ({new_pos[0]}, {new_pos[1]})")
        return True
    
    def _handle_item_interaction(self, item, position):
        """
        Handle player interaction with items on the grid.
        
        Args:
            item (str): The item symbol
            position (list): [row, col] position of the item
        """
        if item == 'T':  # Treasure
            self.score += 100
            print(f"You found a treasure! +100 points")
            self._log_event(f"Found treasure at ({position[0]}, {position[1]})")
            self.grid[position[0]][position[1]] = ' '  # Remove treasure
            
        elif item == 'X':  # Trap
            if self.inventory["shields"] > 0:
                self.inventory["shields"] -= 1
                print("You triggered a trap, but your shield protected you!")
                self._log_event(f"Shield used against trap at ({position[0]}, {position[1]})")
            else:
                self.score -= 50
                print("Oh no! You triggered a trap! -50 points")
                self._log_event(f"Hit by trap at ({position[0]}, {position[1]})")
            self.grid[position[0]][position[1]] = ' '  # Remove trap
            
        elif item == 'K':  # Key
            self.inventory["keys"] += 1
            print("You found a key! It might be useful later.")
            self._log_event(f"Found key at ({position[0]}, {position[1]})")
            self.grid[position[0]][position[1]] = ' '  # Remove key
            
        elif item == 'S':  # Shield
            self.inventory["shields"] += 1
            print("You found a shield! This will protect you from one trap.")
            self._log_event(f"Found shield at ({position[0]}, {position[1]})")
            self.grid[position[0]][position[1]] = ' '  # Remove shield
            
        elif item == 'M':  # Map
            self.inventory["maps"] += 1
            print("You found a map! Use it to reveal the entire grid.")
            self._log_event(f"Found map at ({position[0]}, {position[1]})")
            self.grid[position[0]][position[1]] = ' '  # Remove map
            
        elif item == 'E':  # Exit
            if self.inventory["keys"] >= 1:
                self.score += 200
                print("You've reached the exit and have a key! +200 points")
                self._log_event("Reached exit with key - Victory!")
                self.game_over = True
            else:
                print("You've found the exit, but you need a key to unlock it!")
                self._log_event("Found exit but no key")
    
    def use_map(self):
        """Allow player to use a map item to reveal the entire grid temporarily"""
        if self.inventory["maps"] > 0:
            self.inventory["maps"] -= 1
            self.inventory["used_map"] = True
            print("You used a map! The entire grid is revealed for this turn.")
            self._log_event("Used map item")
            self.display_grid(reveal_all=True)
            time.sleep(5)  # Give player time to see the map
            self.inventory["used_map"] = False
            return True
        else:
            print("You don't have any maps to use!")
            return False
    
    def get_status(self):
        """Return a dictionary with the current game status"""
        elapsed_time = (datetime.now() - self.start_time).seconds
        return {
            "player_name": self.player_name,
            "score": self.score,
            "moves": self.moves,
            "inventory": self.inventory,
            "elapsed_time": elapsed_time,
            "game_over": self.game_over
        }
    
    def save_game(self, filename="saved_game.json"):
        """
        Save the current game state to a JSON file.
        
        Args:
            filename (str): Name of the file to save the game to
        """
        # Create a dictionary with all the game data
        game_data = {
            "player_name": self.player_name,
            "grid_size": self.grid_size,
            "score": self.score,
            "moves": self.moves,
            "player_pos": self.player_pos,
            "grid": self.grid,
            "inventory": self.inventory,
            "game_log": self.game_log,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=4)
        
        print(f"Game saved to {filename}")
        return True
    
    @classmethod
    def load_game(cls, filename="saved_game.json"):
        """
        Load a game from a JSON file.
        
        Args:
            filename (str): Name of the file to load the game from
            
        Returns:
            TreasureHuntGame: A game instance with the loaded state
        """
        try:
            with open(filename, 'r') as f:
                game_data = json.load(f)
            
            # Create a new game instance
            game = cls(game_data["player_name"], game_data["grid_size"])
            
            # Update the game state
            game.score = game_data["score"]
            game.moves = game_data["moves"]
            game.player_pos = game_data["player_pos"]
            game.grid = game_data["grid"]
            game.inventory = game_data["inventory"]
            game.game_log = game_data["game_log"]
            
            game._log_event(f"Game loaded from {filename}")
            print(f"Game loaded from {filename}")
            return game
            
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Could not load game from {filename}")
            return None
    
    def generate_game_report(self):
        """Generate a detailed report of the game progress"""
        elapsed_time = (datetime.now() - self.start_time).seconds
        minutes, seconds = divmod(elapsed_time, 60)
        
        report = f"\n===== GAME REPORT =====\n"
        report += f"Player: {self.player_name}\n"
        report += f"Final Score: {self.score}\n"
        report += f"Moves Made: {self.moves}\n"
        report += f"Time Played: {minutes}m {seconds}s\n"
        report += f"Items Collected:\n"
        report += f"  - Keys: {self.inventory['keys']}\n"
        report += f"  - Shields: {self.inventory['shields']}\n"
        report += f"  - Maps: {self.inventory['maps']}\n"
        
        # Calculate efficiency (points per move)
        efficiency = self.score / max(1, self.moves)
        report += f"Point Efficiency: {efficiency:.2f} points per move\n"
        
        # Add last 5 game log entries
        report += "\nRecent Events:\n"
        for event in self.game_log[-5:]:
            report += f"  {event}\n"
            
        return report


def play_game():
    """Main function to start and play the game"""
    
    # Display welcome message and instructions
    print("\n" + "="*50)
    print("WELCOME TO THE PYTHON TREASURE HUNT ADVENTURE!")
    print("="*50)
    print("\nIn this game, you'll navigate a grid to find treasures while avoiding traps.")
    print("\nLEGEND:")
    print("P = Player (You)")
    print("T = Treasure (+100 points)")
    print("X = Trap (-50 points)")
    print("K = Key (Needed to exit)")
    print("S = Shield (Protects from one trap)")
    print("M = Map (Reveals the entire grid temporarily)")
    print("E = Exit (Need a key to unlock)")
    print("? = Unexplored area")
    
    print("\nCOMMANDS:")
    print("- up, down, left, right: Move in that direction")
    print("- map: Use a map item to reveal the grid")
    print("- save: Save your current game")
    print("- load: Load a previously saved game")
    print("- quit: Exit the game")
    
    # Get player name
    player_name = input("\nPlease enter your name: ")
    
    # Initialize game
    game = TreasureHuntGame(player_name)
    
    # Main game loop
    while not game.game_over:
        # Display the current state
        game.display_grid()
        
        # Get player command
        command = input("\nEnter command (up/down/left/right/map/save/load/quit): ").lower()
        
        # Process command
        if command in ["up", "down", "left", "right"]:
            game.move_player(command)
        elif command == "map":
            game.use_map()
        elif command == "save":
            game.save_game()
        elif command == "load":
            loaded_game = TreasureHuntGame.load_game()
            if loaded_game:
                game = loaded_game
        elif command == "quit":
            confirm = input("Are you sure you want to quit? (y/n): ").lower()
            if confirm == 'y':
                print("Thanks for playing!")
                break
        else:
            print("Invalid command. Try again.")
    
    # Game over - display final status
    if game.game_over:
        game.display_grid(reveal_all=True)
        print("\nGame Over!")
        print(game.generate_game_report())
        
        # Check high scores and save if it's a high score
        high_score = check_high_scores(game.player_name, game.score)
        if high_score:
            print(f"Congratulations! You got a high score!")
            display_high_scores()


def check_high_scores(player_name, score, filename="high_scores.json"):
    """
    Check if the score is a high score and save it if it is.
    
    Args:
        player_name (str): Player's name
        score (int): Player's score
        filename (str): File to save high scores to
        
    Returns:
        bool: True if it's a high score, False otherwise
    """
    # Load existing high scores
    try:
        with open(filename, 'r') as f:
            high_scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        high_scores = []
    
    # Add new score
    high_scores.append({
        "player": player_name,
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Sort by score (descending)
    high_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Keep only top 5
    high_scores = high_scores[:5]
    
    # Save back to file
    with open(filename, 'w') as f:
        json.dump(high_scores, f, indent=4)
    
    # Check if this score is in the top 5
    return any(score_entry["player"] == player_name and score_entry["score"] == score for score_entry in high_scores)


def display_high_scores(filename="high_scores.json"):
    """Display the high scores from a file"""
    try:
        with open(filename, 'r') as f:
            high_scores = json.load(f)
        
        print("\n===== HIGH SCORES =====")
        for i, score in enumerate(high_scores, 1):
            print(f"{i}. {score['player']}: {score['score']} points ({score['date']})")
            
    except (FileNotFoundError, json.JSONDecodeError):
        print("\nNo high scores yet!")


# Run the game if this script is executed directly
if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\nGame terminated by user. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Sorry about that! The game has been terminated.")
