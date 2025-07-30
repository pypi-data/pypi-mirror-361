#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import threading
import sys
import ipaddress
import time
import random
import os
import json

# --- Configuration ---
PORT = 13344
MODEL_PATH = 'gemma3n:e4b' # non-vision model
VISION_PATH = 'qwen2.5vl:3b' # Vision model

# --- Hangman Game Configuration & State ---
HANGMAN_STAGES = [
    # Stage 0: 0 wrong guesses
    """
       +---+
       |   |
           |
           |
           |
           |
    =========
    """,
    # Stage 1: 1 wrong guess
    """
       +---+
       |   |
       O   |
           |
           |
           |
    =========
    """,
    # Stage 2: 2 wrong guesses
    """
       +---+
       |   |
       O   |
       |   |
           |
           |
    =========
    """,
    # Stage 3: 3 wrong guesses
    """
       +---+
       |   |
       O   |
      /|   |
           |
           |
    =========
    """,
    # Stage 4: 4 wrong guesses
    """
       +---+
       |   |
       O   |
      /|\\  |
           |
           |
    =========
    """,
    # Stage 5: 5 wrong guesses
    """
       +---+
       |   |
       O   |
      /|\\  |
      /    |
           |
    =========
    """,
    # Stage 6: 6 wrong guesses (Game Over)
    """
       +---+
       |   |
       O   |
      /|\\  |
      / \\  |
           |
    =========
    """
]

# This dictionary will hold the state of the current hangman game
game_state = {
    'in_progress': False,
    'word': "",
    'word_progress': "",
    'wrong_guesses': 0,
    'guessed_letters': set(),
    'challenger': ""
}

# --- Stick Figure Fight Game Configuration & State ---
FIGHT_POSES = {
    'idle': "  O  \n /|\\ \n / \\ ",
    'punch': "  O-->>\n /|  \n / \\ ",
    'kick': "  O  \n /|\\ \n  / >",
    'block': "  O  \n /|\\ \n | | ",
    'hit': "   O \n  /|\\\n  / \\",
    'win': "  O__\n /|\\ \n / \\ ",
    'lose': "   X \n  /|\\\n  / \\",
    'special': " O<*>\n/|\\ \n/ \\ "
}

# This dictionary will hold the state of the current fight
fight_state = {
    'in_progress': False,
    'players': {},
    'player_names': [],
    'turn': "",
    'pending_challenge': {}
}

# --- EconSim Game Configuration & State ---
ECONSIM_CONFIG = {
    "title": "Lemonade Stand Showdown",
    "starting_cash": 50.00,
    "duration_days": 10,
    "item_costs": {
        "lemons": 0.20,
        "sugar": 0.10,
        "cups": 0.05
    }
}

# This dictionary will hold the state of the active EconSim game
econsim_state = {
    'in_progress': False,
    'phase': None,  # Can be 'LOBBY', 'DECISION', 'PROCESSING'
    'host': "",
    'players': {},  # e.g., {'Alice': {'cash': 50, 'inventory': {...}, 'decision': {...}}}
    'current_day': 0,
    'daily_scenario': "",
    'past_scenarios': []
}


# --- Helper Functions ---

# Econsim funtions start --->

def reset_econsim_state():
    """Resets the EconSim game state."""
    global econsim_state
    econsim_state = {
        'in_progress': False, 'phase': None, 'host': "",
        'players': {}, 'current_day': 0, 'daily_scenario': "",
        'past_scenarios': []
    }

def start_econsim_game(host_username, clients):
    """Starts the lobby for a new game of EconSim."""
    global econsim_state
    reset_econsim_state()
    econsim_state.update({
        'in_progress': True,
        'phase': 'LOBBY',
        'host': host_username,
        'players': {
            host_username: {
                'cash': ECONSIM_CONFIG['starting_cash'],
                'inventory': {'lemons': 0, 'sugar': 0, 'cups': 0},
                'decision': None
            }
        }
    })
    start_message = f"\n--- {host_username} has started a game of {ECONSIM_CONFIG['title']}! ---\nType /join-game to play! The host can type /begin-game to start. Rules 1 lemonade=1 lemon + 1 sugar + 1 cup. Starting Cash is $50 with zero inventory. lemon cost $0.2, sugar cost $0.1 cup cost $0.05. You decide price and marketing spend"
    broadcast(start_message.encode('utf-8'), None, clients)

def begin_econsim_day(clients):
    """Starts a new day by generating a unique scenario and asking for decisions."""
    global econsim_state
    if not econsim_state['players']:
        broadcast("[GAME] No players are in the game. EconSim ended.".encode('utf-8'), None, clients)
        reset_econsim_state()
        return

    econsim_state['current_day'] += 1
    econsim_state['phase'] = 'DECISION'
    
    for player in econsim_state['players']:
        econsim_state['players'][player]['decision'] = None

    
    try:
        import ollama
        
        # Create a formatted string of past scenarios to include in the prompt
        past_scenarios_list = "\n".join(f"- {s}" for s in econsim_state['past_scenarios'])
        
        scenario_prompt = f"""
        Generate a new and different one-sentence market scenario for a lemonade stand game.
        Do NOT repeat any of the following scenarios that have already been used:
        {past_scenarios_list}

        Please provide only one new scenario. Examples of new scenarios: a hot sunny day, a surprise rain shower, a storm, a local festival is happening nearby.
        """
        response = ollama.chat(model=MODEL_PATH, messages=[{'role': 'user', 'content': scenario_prompt}])
        new_scenario = response['message']['content'].strip()
        
        # Update the state with the new scenario
        econsim_state['daily_scenario'] = new_scenario
        econsim_state['past_scenarios'].append(new_scenario)

    except Exception as e:
        # Fallback with a random element to ensure it's not always the same
        fallback_scenarios = ["It's a normal, average day.", "The weather is perfectly mild.", "There's a gentle breeze in the air."]
        econsim_state['daily_scenario'] = random.choice(fallback_scenarios)
        print(f"[EconSim] AI scenario generation failed: {e}")

    day_message = f"\n--- Day {econsim_state['current_day']}/{ECONSIM_CONFIG['duration_days']} ---"
    scenario_message = f"Market Report: {econsim_state['daily_scenario']}"
    decision_prompt = "Please submit your decisions with: /decision price=X marketing=Y buy_lemons=Z buy_sugar=A buy_cups=B"
    
    broadcast(f"{day_message}\n{scenario_message}\n{decision_prompt}".encode('utf-8'), None, clients)

    
def extract_json_from_string(text):
    """
    Finds and parses a JSON object from within a larger string of text.
    Returns the parsed JSON object or None if it fails.
    """
    try:
        # Find the first opening curly brace and the last closing curly brace
        start_index = text.find('{')
        end_index = text.rfind('}')
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_string = text[start_index:end_index+1]
            return json.loads(json_string)
    except (json.JSONDecodeError, IndexError):
        # Handle cases where the extraction or parsing fails
        return None
    return None
    
    
def adjudicate_day_results(clients):
    """Processes all player decisions, uses a two-step AI process and JSON parsing."""
    global econsim_state
    
    player_data_string = ""
    player_names = list(econsim_state['players'].keys())
    for name in player_names:
        decision = econsim_state['players'][name].get('decision', {})
        player_data_string += f"- Player '{name}' set price to ${decision.get('price', 2.5):.2f}, spent ${decision.get('marketing', 0):.2f} on marketing.\n"

    prompt = f"""
        You are the simulator for a Lemonade Stand game.
        The market scenario for today is: "{econsim_state['daily_scenario']}"
        Here are the decisions from all competing players:
        {player_data_string}
        Based on the market scenario and their decisions (price, marketing), determine how many cups of lemonade each player sold. A lower price and higher marketing generally lead to more sales, especially on a good day. Players are competing against each other.
        Provide your response ONLY in the following JSON format. It is critical that the `player_name` values in the response list are EXACTLY these names: {player_names}.

        {{
          "analysis": "A brief, one-sentence explanation of the market results. Example: Alice's aggressive pricing stole most of the customers.",
          "results": [
            {{ "player_name": "PlayerName1", "cups_sold": CUPS_SOLD }},
            {{ "player_name": "PlayerName2", "cups_sold": CUPS_SOLD }}
          ]
        }}
        """
    
    parsed_results = None
    try:
        import ollama
        import json
        
        # Step 1: Get the narrative response
        narrative_response = ollama.chat(model=MODEL_PATH, messages=[{'role': 'user', 'content': prompt}])
        narrative_text = narrative_response['message']['content']
        
        print("\n[DEBUG] Raw AI Narrative Response:")
        print(narrative_text)

        # Step 2: Use a second AI call to extract the data into a JSON format
        extraction_prompt = f"""
            Read the following text and extract the number of cups sold for each player. The player names are: {player_names}.
            Respond ONLY with a valid JSON object in the specified format.

            Text to analyze: "{narrative_text}"

            JSON format:
            {{
              "analysis": "A brief summary of the narrative.",
              "results": [
                {{ "player_name": "PlayerName1", "cups_sold": CUPS_SOLD }},
                {{ "player_name": "PlayerName2", "cups_sold": CUPS_SOLD }}
              ]
            }}
            """
        json_response = ollama.chat(model=MODEL_PATH, messages=[{'role': 'user', 'content': extraction_prompt}], format='json')
        ai_json_string = json_response['message']['content']
        
        print("\n[DEBUG] Raw AI JSON Response:")
        print(ai_json_string)

        parsed_results = extract_json_from_string(ai_json_string)
        if not parsed_results:
            raise ValueError("Failed to extract valid JSON from AI response.")

        # --- Check for multiple possible keys to handle AI typos ---
        results_list = []
        possible_keys = ['results', 'reresults', 'reults']
        for key in possible_keys:
            if key in parsed_results:
                results_list = parsed_results[key]
                break
        
        if not results_list:
            raise ValueError("AI JSON response did not contain a recognized results key.")

        ai_player_names = {item.get('player_name') for item in results_list}
        if not set(player_names).issubset(ai_player_names):
            raise ValueError("AI response did not contain all required player names.")

    except Exception as e:
        print(f"[EconSim] AI adjudication failed: {e}. Using fallback.")
        parsed_results = {
            "analysis": "AI simulation failed. Using random results.",
            "results": [{"player_name": name, "cups_sold": random.randint(5, 25)} for name in player_names]
        }

    end_of_day_report = f"\n--- End of Day {econsim_state['current_day']} Report ---\n"
    end_of_day_report += f"Market Analysis: {parsed_results.get('analysis', 'N/A')}\n\n"

    # Parsing results from AI response
    final_results_list = parsed_results.get('results') or parsed_results.get('reresults') or parsed_results.get('reults', [])
    sales_results = {item.get('player_name'): item.get('cups_sold', 0) for item in final_results_list}

    for name, player_data in econsim_state['players'].items():
        decision = player_data.get('decision', {})
        
        lemons_cost = decision.get('buy_lemons', 0) * ECONSIM_CONFIG['item_costs']['lemons']
        sugar_cost = decision.get('buy_sugar', 0) * ECONSIM_CONFIG['item_costs']['sugar']
        cups_cost = decision.get('buy_cups', 0) * ECONSIM_CONFIG['item_costs']['cups']
        marketing_cost = decision.get('marketing', 0)
        total_cost = lemons_cost + sugar_cost + cups_cost + marketing_cost

        player_data['cash'] -= total_cost
        player_data['inventory']['lemons'] += decision.get('buy_lemons', 0)
        player_data['inventory']['sugar'] += decision.get('buy_sugar', 0)
        player_data['inventory']['cups'] += decision.get('buy_cups', 0)

        cups_sold_ai = sales_results.get(name, 0)
        
        max_possible_sales = min(
            player_data['inventory']['lemons'],
            player_data['inventory']['sugar'],
            player_data['inventory']['cups']
        )
        
        actual_sales = min(int(cups_sold_ai), int(max_possible_sales))
        
        revenue = actual_sales * decision.get('price', 0)
        profit = revenue - total_cost

        player_data['inventory']['lemons'] -= actual_sales
        player_data['inventory']['sugar'] -= actual_sales
        player_data['inventory']['cups'] -= actual_sales
        player_data['cash'] += revenue
        
        end_of_day_report += f"Player: {name}\n"
        end_of_day_report += f"  - Sales: {actual_sales} cups @ ${decision.get('price', 0):.2f} each\n"
        end_of_day_report += f"  - Revenue: ${revenue:.2f} | Costs: ${total_cost:.2f} | Daily Profit: ${profit:.2f}\n"
        end_of_day_report += f"  - Final Cash: ${player_data['cash']:.2f}\n"
        inventory_str = f"Lemons: {int(player_data['inventory']['lemons'])}, Sugar: {int(player_data['inventory']['sugar'])}, Cups: {int(player_data['inventory']['cups'])}"
        end_of_day_report += f"  - Inventory: {inventory_str}\n\n"

    broadcast(end_of_day_report.encode('utf-8'), None, clients)

    if econsim_state['current_day'] >= ECONSIM_CONFIG['duration_days']:
        winner = max(econsim_state['players'].items(), key=lambda p: p[1]['cash'])
        winner_report = f"\n--- GAME OVER! The winner is {winner[0]} with a final cash balance of ${winner[1]['cash']:.2f}! ---\n"
        broadcast(winner_report.encode('utf-8'), None, clients)
        reset_econsim_state()
    else:
        begin_econsim_day(clients)

    
# Econsim functions end <-----


def clear_screen():
    """Clears the terminal screen for different operating systems."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def reset_game_state():
    """Resets the hangman game state to its initial blank state."""
    global game_state
    game_state = {
        'in_progress': False, 'word': "", 'word_progress': "",
        'wrong_guesses': 0, 'guessed_letters': set(), 'challenger': ""
    }

def broadcast_game_state(clients, recipient_list=None):
    """Constructs and sends the current hangman state to players."""
    if not game_state['in_progress']:
        return
    word_display = " ".join(game_state['word_progress'])
    guessed_display = " ".join(sorted(list(game_state['guessed_letters'])))
    art = HANGMAN_STAGES[game_state['wrong_guesses']]
    message = f"""
{art}
Word: {word_display}
Guessed letters: [{guessed_display}]
"""
    
    if recipient_list:
        for conn in recipient_list:
            try:
                conn.send(message.encode('utf-8'))
            except:
                pass 
    else:
        broadcast(message.encode('utf-8'), None, clients)

def start_hangman_game(challenger_name, word, clients):
    """Initializes the game state for a new game of Hangman."""
    global game_state
    reset_game_state()
    game_state['in_progress'] = True
    game_state['word'] = word.upper()
    game_state['word_progress'] = ['_' if char.isalpha() else char for char in game_state['word']]
    game_state['challenger'] = challenger_name
    start_message = f"\n--- {challenger_name} has started a new game of Hangman! ---\nUse /guess <letter> to play. Use /quitgame to stop."
    broadcast(start_message.encode('utf-8'), None, clients)
    broadcast_game_state(clients)

def reset_fight_state():
    """Resets the fight game state to its initial blank state."""
    global fight_state
    fight_state = {
        'in_progress': False, 'players': {}, 'player_names': [],
        'turn': "", 'pending_challenge': {}
    }

def broadcast_fight_state(clients, p1_pose_key='idle', p2_pose_key='idle', action_text="", recipient_list=None):
    """Constructs and sends the current fight scene to players."""
    if not fight_state['in_progress']:
        return
    p1_name, p2_name = fight_state['player_names']
    p1_hp = fight_state['players'][p1_name]['hp']
    p2_hp = fight_state['players'][p2_name]['hp']
    p1_art_lines = FIGHT_POSES[p1_pose_key].split('\n')
    p2_art_lines = FIGHT_POSES[p2_pose_key].split('\n')
    scene = ""
    for i in range(len(p1_art_lines)):
        scene += f"{p1_art_lines[i]:<15}{p2_art_lines[i]:>15}\n"
    scene += f"{p1_name + ' (' + str(p1_hp) + ' HP)':<15}{p2_name + ' (' + str(p2_hp) + ' HP)':>15}\n"
    full_message = f"\n{scene}\n{action_text}\n"

    if recipient_list:
        for conn in recipient_list:
             try:
                conn.send(full_message.encode('utf-8'))
             except:
                pass
    else:
        broadcast(full_message.encode('utf-8'), None, clients)

def start_fight_game(clients):
    """Initializes the game state for a new fight."""
    global fight_state
    challenger = fight_state['pending_challenge']['challenger']
    opponent = fight_state['pending_challenge']['opponent']
    fight_state['in_progress'] = True
    fight_state['player_names'] = [challenger, opponent]
    fight_state['players'] = {
        challenger: {'hp': 100, 'special_used': False},
        opponent: {'hp': 100, 'special_used': False}
    }
    fight_state['turn'] = challenger
    fight_state['pending_challenge'] = {}
    start_message = f"\n--- {challenger} vs. {opponent}! FIGHT! ---"
    broadcast(start_message.encode('utf-8'), None, clients)
    broadcast_fight_state(clients, 'idle', 'idle', f"It is {challenger}'s turn. Choose your move: /punch, /kick, /block, /special")


def start_server(host_ip):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen()
        print(f"[SERVER] Started. Listening for connections on port {PORT}")
        print(f"[SERVER] Other users can connect using this machine's IP: {host_ip}")
        clients = {}
        while True:
            client_conn, client_addr = server_socket.accept()
            print(f"[SERVER] New connection from {client_addr}")
            thread = threading.Thread(target=handle_client, args=(client_conn, clients))
            thread.daemon = True
            thread.start()
    except OSError as e:
        print(f"[SERVER] Error: {e}. Is port {PORT} already in use?")
    finally:
        server_socket.close()


def handle_client(connection, clients):
    """Receives messages, parses them for commands, and handles game logic."""
    username = ""
    try:
        username = connection.recv(1024).decode('utf-8')
        if not username or username in clients:
            error_msg = "[SYSTEM] Username is empty or already taken. Please reconnect with a different name."
            connection.send(error_msg.encode('utf-8'))
            time.sleep(1)
            connection.close()
            return
        
        clients[username] = connection
        
        connection.send("##CLEAR_SCREEN##".encode('utf-8'))
        time.sleep(0.1)
        welcome_art = f"""
   _____        _____  _____  ______  _____ _____ 
  |  __ \\ /\\   |  __ \\|  __ \\|  ____|/ ____|_   _|
  | |__) /  \\  | |__) | |  | | |__  | (___   | |  
  |  ___/ /\\ \\ |  _  /| |  | |  __|  \\___ \\  | |  
  | |  / ____ \\| | \\ \\| |__| | |____ ____) |_| |_ 
  |_| /_/    \\_\\_|  \\_\\_____/|______|_____/|_____|
                                                  
        --- 🔥 Welcome to Pardesi Chat, {username}! 🔥 ---
        
Type a message to chat, or try a command:
/whisper @<user> <message>
/hangman <word>
/fight @<user>
/ai <prompt>
/start-econsim
"""
        connection.send(welcome_art.encode('utf-8'))
        broadcast(f"[SYSTEM] {username} has joined the chat.".encode('utf-8'), connection, clients)
        
        if game_state['in_progress']:
            broadcast_game_state(clients, recipient_list=[connection])
        elif fight_state['in_progress']:
            broadcast_fight_state(clients, 'idle', 'idle', f"A fight is in progress! It is {fight_state['turn']}'s turn.", recipient_list=[connection])
        elif econsim_state['in_progress'] and econsim_state['phase'] == 'LOBBY':
            connection.send(f"[GAME] An EconSim game is waiting for players. Type /join-game to play!".encode('utf-8'))

        while True:
            full_message = connection.recv(2048).decode('utf-8')
            if full_message:
                sender_username = full_message[full_message.find('<')+1:full_message.find('>')]
                message_content = full_message[full_message.find('>')+2:]

                if message_content.startswith('/'):
                    # --- FIX: New, more robust command parsing logic ---
                    command_parts = message_content.split(' ', 1)
                    command = command_parts[0].lower()
                    args_string = command_parts[1] if len(command_parts) > 1 else ""
                    # --- END FIX ---

                    if command in ['/whisper', '/msg']:
                        whisper_parts = args_string.split(' ', 1)
                        if len(whisper_parts) < 2:
                            connection.send("[SYSTEM] Usage: /whisper @<username> <message>".encode('utf-8'))
                        else:
                            recipient_name = whisper_parts[0][1:] if whisper_parts[0].startswith('@') else whisper_parts[0]
                            if recipient_name in clients:
                                private_message = whisper_parts[1]
                                clients[recipient_name].send(f"[Private from {sender_username}]: {private_message}".encode('utf-8'))
                                connection.send(f"[You whispered to {recipient_name}]: {private_message}".encode('utf-8'))
                            else:
                                connection.send(f"[SYSTEM] Error: User '{recipient_name}' not found.".encode('utf-8'))
                    
                    elif command == '/hangman':
                        hangman_parts = args_string.split()
                        if not hangman_parts or not hangman_parts[0].isalpha():
                            connection.send(f"[GAME] Usage: /hangman <word_to_guess> (e.g., /hangman python)".encode('utf-8'))
                        elif game_state['in_progress'] or fight_state['in_progress'] or econsim_state['in_progress']:
                            connection.send("[GAME] A game is already in progress!".encode('utf-8'))
                        else:
                            start_hangman_game(sender_username, hangman_parts[0], clients)
                    
                    elif command == '/guess':
                        guess_parts = args_string.split()
                        if not game_state['in_progress']:
                            connection.send("[GAME] No hangman game is currently in progress.".encode('utf-8'))
                        elif not guess_parts or len(guess_parts[0]) != 1 or not guess_parts[0].isalpha():
                            connection.send(f"[GAME] Usage: /guess <single_letter>".encode('utf-8'))
                        else:
                            guess = guess_parts[0].upper()
                            if guess in game_state['guessed_letters']:
                                broadcast(f"[GAME] '{guess}' has already been guessed.".encode('utf-8'), None, clients)
                            else:
                                game_state['guessed_letters'].add(guess)
                                if guess in game_state['word']:
                                    for i, letter in enumerate(game_state['word']):
                                        if letter == guess: game_state['word_progress'][i] = guess
                                    broadcast(f"[GAME] {sender_username} guessed '{guess}' correctly!".encode('utf-8'), None, clients)
                                    if '_' not in game_state['word_progress']:
                                        broadcast_game_state(clients)
                                        broadcast(f"\n--- YOU WIN! The word was {game_state['word']}. Congratulations! ---\n".encode('utf-8'), None, clients)
                                        reset_game_state()
                                    else:
                                        broadcast_game_state(clients)
                                else:
                                    game_state['wrong_guesses'] += 1
                                    broadcast(f"[GAME] {sender_username} guessed '{guess}', which is WRONG!".encode('utf-8'), None, clients)
                                    if game_state['wrong_guesses'] >= len(HANGMAN_STAGES) - 1:
                                        broadcast_game_state(clients)
                                        broadcast(f"\n--- GAME OVER! The word was {game_state['word']}. ---\n".encode('utf-8'), None, clients)
                                        reset_game_state()
                                    else:
                                        broadcast_game_state(clients)

                    elif command == '/quitgame':
                        if game_state['in_progress'] and sender_username == game_state['challenger']:
                            broadcast(f"[GAME] {game_state['challenger']} has ended the game. The word was {game_state['word']}".encode('utf-8'), None, clients)
                            reset_game_state()
                        else:
                            connection.send("[GAME] There is no hangman game to quit or you didn't start it.".encode('utf-8'))

                    elif command == '/fight':
                        fight_parts = args_string.split()
                        if not fight_parts or not fight_parts[0].startswith('@'):
                            connection.send("[GAME] Usage: /fight @<username>".encode('utf-8'))
                        elif game_state['in_progress'] or fight_state['in_progress'] or econsim_state['in_progress']:
                            connection.send("[GAME] A game is already in progress!".encode('utf-8'))
                        else:
                            opponent_name = fight_parts[0][1:]
                            if opponent_name == sender_username:
                                connection.send("[GAME] You can't fight yourself!".encode('utf-8'))
                            else:
                                fight_state['pending_challenge'] = {'challenger': sender_username, 'opponent': opponent_name}
                                challenge_msg = f"[GAME] {sender_username} has challenged {opponent_name} to a fight! {opponent_name}, type /accept to fight."
                                broadcast(challenge_msg.encode('utf-8'), None, clients)

                    elif command == '/accept':
                        if fight_state.get('pending_challenge', {}).get('opponent') == sender_username:
                            start_fight_game(clients)
                        else:
                            connection.send("[GAME] You have not been challenged to a fight.".encode('utf-8'))

                    elif command in ['/punch', '/kick', '/block', '/special']:
                        if not fight_state['in_progress']:
                            connection.send("[GAME] No fight is in progress.".encode('utf-8'))
                        elif sender_username != fight_state['turn']:
                            connection.send(f"[GAME] It's not your turn! It's {fight_state['turn']}'s turn.".encode('utf-8'))
                        else:
                            player1_name = sender_username
                            player2_name = fight_state['player_names'][1] if fight_state['player_names'][0] == player1_name else fight_state['player_names'][0]
                            action_text, p1_pose, p2_pose = "", 'idle', 'idle'
                            if command == '/punch':
                                p1_pose = 'punch'
                                if random.random() < 0.8:
                                    damage = 10
                                    fight_state['players'][player2_name]['hp'] -= damage
                                    action_text = f"{player1_name}'s punch connects for {damage} damage!"
                                    p2_pose = 'hit'
                                else:
                                    action_text = f"{player1_name}'s punch misses!"
                            elif command == '/kick':
                                p1_pose = 'kick'
                                if random.random() < 0.6:
                                    damage = 20
                                    fight_state['players'][player2_name]['hp'] -= damage
                                    action_text = f"{player1_name}'s kick lands for {damage} damage!"
                                    p2_pose = 'hit'
                                else:
                                    action_text = f"{player1_name}'s kick misses!"
                            elif command == '/special':
                                if fight_state['players'][player1_name]['special_used']:
                                    action_text = f"{player1_name} tried their special move, but has already used it!"
                                else:
                                    fight_state['players'][player1_name]['special_used'] = True
                                    p1_pose = 'special'
                                    action_text = f"{player1_name} attempts a high-risk special move!\n"
                                    if random.random() < 0.3:
                                        damage = int(fight_state['players'][player2_name]['hp'] * 0.5)
                                        fight_state['players'][player2_name]['hp'] -= damage
                                        action_text += f"IT CONNECTS! A devastating blow deals {damage} damage!"
                                        p2_pose = 'hit'
                                    else:
                                        action_text += f"But it fails, leaving them open!"
                            elif command == '/block':
                                p1_pose = 'block'
                                action_text = f"{player1_name} takes a defensive stance."
                            if fight_state['players'][player2_name]['hp'] <= 0:
                                p1_pose_for_win = 'win' if fight_state['player_names'][0] == player1_name else 'lose'
                                p2_pose_for_win = 'lose' if fight_state['player_names'][0] == player1_name else 'win'
                                broadcast_fight_state(clients, p1_pose_for_win, p2_pose_for_win, f"{action_text}\n--- {player1_name} WINS! ---")
                                reset_fight_state()
                            else:
                                fight_state['turn'] = player2_name
                                next_turn_text = f"It is {player2_name}'s turn. Choose your move: /punch, /kick, /block, /special"
                                if fight_state['player_names'][0] != player1_name:
                                    p1_pose, p2_pose = p2_pose, p1_pose
                                broadcast_fight_state(clients, p1_pose, p2_pose, f"{action_text}\n{next_turn_text}")
                    
                    elif command == '/ai':
                        if not args_string:
                            connection.send("[SYSTEM] Usage: /ai <prompt> or /ai <url> <prompt>".encode('utf-8'))
                        else:
                            try:
                                import ollama
                                import requests
                                from newspaper import Article
                                
                                ai_parts = args_string.split(' ', 1)
                                first_arg = ai_parts[0]
                                question = ai_parts[1] if len(ai_parts) > 1 else ""

                                if first_arg.startswith('http') and first_arg.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                    image_url = first_arg
                                    question = question or "Describe this image in detail."
                                    ai_thinking_msg = f"[AI Bot is analyzing the image with {VISION_PATH}...]"
                                    broadcast(ai_thinking_msg.encode('utf-8'), None, clients)
                                    response = requests.get(image_url)
                                    response.raise_for_status()
                                    ollama_response = ollama.chat(model=VISION_PATH, messages=[{'role': 'user', 'content': question, 'images': [response.content]}])
                                    response_text = ollama_response['message']['content']
                                elif first_arg.startswith('http'):
                                    article_url = first_arg
                                    question = question or "Summarize the key points of this article."
                                    ai_thinking_msg = f"[AI Bot is reading the article with {MODEL_PATH}...]"
                                    broadcast(ai_thinking_msg.encode('utf-8'), None, clients)
                                    article = Article(article_url)
                                    article.download()
                                    article.parse()
                                    full_prompt = f"Based on the following article text, please answer this question: '{question}'\n\n--- ARTICLE TEXT ---\n{article.text}"
                                    ollama_response = ollama.chat(model=MODEL_PATH, messages=[{'role': 'user', 'content': full_prompt}])
                                    response_text = ollama_response['message']['content']
                                else:
                                    question = args_string
                                    ai_thinking_msg = f"[AI Bot is thinking with {MODEL_PATH}...]"
                                    broadcast(ai_thinking_msg.encode('utf-8'), None, clients)
                                    ollama_response = ollama.chat(model=MODEL_PATH, messages=[{'role': 'user', 'content': question}])
                                    response_text = ollama_response['message']['content']
                                
                                ai_response_msg = f"[🤖 AI Bot]: {response_text}"
                                broadcast(ai_response_msg.encode('utf-8'), None, clients)
                            except ImportError:
                                broadcast("[AI] Required libraries for AI are not installed on the server.".encode('utf-8'), None, clients)
                            except Exception as e:
                                broadcast(f"[AI] An error occurred: {e}".encode('utf-8'), None, clients)

                    elif command == '/start-econsim':
                        if econsim_state['in_progress'] or game_state['in_progress'] or fight_state['in_progress']:
                            connection.send("[GAME] Another game is already in progress.".encode('utf-8'))
                        else:
                            start_econsim_game(sender_username, clients)

                    elif command == '/join-game':
                        if not econsim_state['in_progress'] or econsim_state['phase'] != 'LOBBY':
                            connection.send("[GAME] There is no game to join right now.".encode('utf-8'))
                        elif sender_username in econsim_state['players']:
                            connection.send("[GAME] You are already in the game.".encode('utf-8'))
                        else:
                            econsim_state['players'][sender_username] = {
                                'cash': ECONSIM_CONFIG['starting_cash'], 'inventory': {'lemons': 0, 'sugar': 0, 'cups': 0}, 'decision': None
                            }
                            broadcast(f"[GAME] {sender_username} has joined the EconSim game!".encode('utf-8'), None, clients)

                    elif command == '/begin-game':
                        if not econsim_state['in_progress'] or econsim_state['phase'] != 'LOBBY':
                            connection.send("[GAME] There is no game lobby to begin.".encode('utf-8'))
                        elif sender_username != econsim_state['host']:
                            connection.send("[GAME] Only the host can begin the game.".encode('utf-8'))
                        else:
                            broadcast(f"[GAME] The host has closed the lobby. The game begins!".encode('utf-8'), None, clients)
                            begin_econsim_day(clients)

                    elif command == '/decision':
                        if not econsim_state['in_progress'] or econsim_state['phase'] != 'DECISION':
                            connection.send("[GAME] It is not time to make a decision.".encode('utf-8'))
                        elif sender_username not in econsim_state['players']:
                             connection.send("[GAME] You are not in the current EconSim game.".encode('utf-8'))
                        elif econsim_state['players'][sender_username]['decision'] is not None:
                            connection.send("[GAME] You have already submitted your decision for this day.".encode('utf-8'))
                        else:
                            try:
                                # --- Parsing decision key=value pairs ---
                                decision_parts = args_string.split()
                                decision_data = {item.split('=')[0].lower(): float(item.split('=')[1]) for item in decision_parts}
                                econsim_state['players'][sender_username]['decision'] = decision_data
                                connection.send(f"[GAME] Your decision for Day {econsim_state['current_day']} has been locked in.".encode('utf-8'))
                                
                                all_decisions_in = all(p['decision'] is not None for p in econsim_state['players'].values())
                                if all_decisions_in:
                                    econsim_state['phase'] = 'PROCESSING'
                                    broadcast("\n[GAME] All decisions are in! Simulating the day's results...".encode('utf-8'), None, clients)
                                    adjudicate_day_results(clients)
                            except (ValueError, IndexError):
                                connection.send("[GAME] Invalid decision format. Use: /decision price=2.5 marketing=10 ...".encode('utf-8'))
                else:
                    broadcast(full_message.encode('utf-8'), connection, clients)
            else:
                break 
    except Exception as e:
        print(f"[SERVER] Error in handle_client for {username}: {e}")
    finally:
        if username and username in clients:
            del clients[username]
            broadcast(f"[SYSTEM] {username} has left the chat.".encode('utf-8'), None, clients)
            if game_state['in_progress'] and username == game_state['challenger']:
                broadcast(f"[GAME] {game_state['challenger']} disconnected. The hangman game has ended.".encode('utf-8'), None, clients)
                reset_game_state()
            if fight_state['in_progress'] and username in fight_state['player_names']:
                 broadcast(f"[GAME] {username} disconnected. The fight is over.".encode('utf-8'), None, clients)
                 reset_fight_state()
            if econsim_state['in_progress'] and username in econsim_state['players']:
                del econsim_state['players'][username]
                broadcast(f"[GAME] {username} has left the EconSim game.".encode('utf-8'), None, clients)
        connection.close()
        

def broadcast(message, sender_connection, clients):
    """Broadcasts a message to all clients in the dictionary."""
    
    for conn in clients.values():
        if conn != sender_connection:
            try:
                conn.send(message)
            except:
                
                conn.close()


def start_client(host_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host_ip, PORT))
    except socket.error as e:
        print(f"Failed to connect to server: {e}")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        username = input("Enter your username: ")
        client_socket.send(username.encode('utf-8'))
        
        sys.stdout.write('> ')
        sys.stdout.flush()

        while True:
            message = input()
            if message.lower() == 'exit':
                break
            full_message = f"<{username}> {message}"
            client_socket.send(full_message.encode('utf-8'))
            
            sys.stdout.write('> ')
            sys.stdout.flush()
    except (EOFError, KeyboardInterrupt):
        print("\nLeaving chat.")
    finally:
        client_socket.close()
        print("\n--- You have left the chat. ---")

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(2048).decode('utf-8')
            if message:
                if message == "##CLEAR_SCREEN##":
                    clear_screen()
                else:
                    sys.stdout.write('\r' + message + '\n')
                    sys.stdout.write('> ')
                    sys.stdout.flush()
            else:
                print("\r--- Connection to server has been lost. Press Enter to exit. ---")
                break
        except:
            print("\r--- Disconnected from server. Press Enter to exit. ---")
            break

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def check_server(ip, port, open_ips):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        if sock.connect_ex((ip, port)) == 0:
            open_ips.append(ip)
    except socket.error:
        pass
    finally:
        sock.close()

def find_server():
    print(f"Searching for a server on port {PORT}...")
    local_ip = get_local_ip()
    if local_ip == '127.0.0.1' and len(sys.argv) < 2:
        print("Could not determine local network. Can't scan.")
        return None, '127.0.0.1'

    subnet = ipaddress.ip_network(f"{local_ip}/24", strict=False)
    threads = []
    found_servers = []
    
    for ip in subnet.hosts():
        ip = str(ip)
        thread = threading.Thread(target=check_server, args=(ip, PORT, found_servers))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()

    if found_servers:
        return found_servers[0], local_ip
    else:
        return None, local_ip


# In[ ]:


# --- Main Execution Logic ---
def run_app():
    try:
        server_ip, my_ip = find_server()
    
        if server_ip:
            print(f"Server found at {server_ip}. Joining as client.")
            start_client(server_ip)
        else:
            print("No server found. Starting a new chat server...")
            
            server_thread = threading.Thread(target=start_server, args=(my_ip,))
            server_thread.daemon = True
            server_thread.start()
            
            time.sleep(1)
            
            print("Server started. Now starting your client...")
            start_client('127.0.0.1')
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        
    finally:
        print("\n--------------------")
        input("Press ENTER to exit...")


# In[ ]:


if __name__ == "__main__":
    run_app()

