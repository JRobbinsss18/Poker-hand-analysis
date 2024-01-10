import pydealer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from collections import Counter
import random
import csv
# INITIALIZE FUNCTION
def initialize_game(hand_size, community_card_size):
    global deck, hand, community_cards
    deck = pydealer.Deck()
    deck.shuffle()
    hand = deck.deal(hand_size)
    hand.sort()
    community_cards = deck.deal(community_card_size)
    update_card_completer()
    update_hand_completer()
    update_community_cards_completer()

# FUNCTION TO PRINT ALL (debugging)
def print_cards():
    print("\nYour hand:")
    print(hand)
    print("\nCommunity Cards:")
    print(community_cards)
    print("\nCards in Deck:")
    print(deck)

# UPDATE COMPLETER FUNCTION(DECK)
def update_card_completer():
    global card_completer
    card_names = [card.name for card in deck]
    card_completer = WordCompleter(card_names, ignore_case=True)

# UPDATE COMPLETER FUNCTION(HAND)
def update_hand_completer():
    global hand_completer
    hand_card_names = [card.name for card in hand]
    hand_completer = WordCompleter(hand_card_names, ignore_case=True)

# UPDATE COMPLETER FUNCTION(COMMUNITY_COLLECTION)
def update_community_cards_completer():
    global community_card_completer
    community_card_names = [card.name for card in community_cards]
    community_card_completer = WordCompleter(community_card_names, ignore_case=True)

# PRINT HAND FUNCTION
def print_hand():
        print("\n---Your hand---")
        print(hand)
        print("---------------")    

# PRINT DECK FUNCTION
def print_deck():
        print("\n---Your deck---")
        print(deck)
        print("---------------")

# PRINT COMMUNITY_CARDS FUNCTION
def print_comm_card():
        print("\n---Community cards---")
        print(community_cards)
        print("---------------------")

# ADD CARD TO COLLECTION FUNCTION
def add_card_to_collection(collection, completer):
    match_found = False
    if collection == "hand":
        if hand.size == 2:
            print("\n===>Cannot add more than 2 cards to hand<===")
            return
    if collection == "community_cards":
        if community_cards.size == 5:
            print("\n===>Cannot add more than 5 cards to community cards<===")
            return
        
    while True:
        card_name = prompt(f"Enter card name to add to {collection} or 'exit' to go back to menu (use tab to autocomplete): ", completer=completer).title()
        if card_name.lower() == 'exit':
            break
        for cd in deck:
            if cd.name.lower() == card_name.lower():
                match_found = True
        if match_found:
            card = deck.get(card_name)
            if collection == "hand":
                hand.add(card)
            elif collection == "community_cards":
                community_cards.add(card)
            update_card_completer()
            update_hand_completer()
            update_community_cards_completer()
            print_cards()
            break
        print("ERROR: Match not found, use autocomplete function to confirm matches in formatting or confirm that this card is not in another list\n")

# REMOVE CARD FROM COLLECTION FUNCTION
def remove_card_from_collection(collection, completer):
    match_found = False
    while True:
        card_name = prompt(f"Enter card name to remove from {collection} or 'exit' to go back to menu (use tab to autocomplete): ", completer=completer).title()
        if card_name.lower() == 'exit':
            break
        target_collection = hand if collection == "hand" else community_cards
        for cd in target_collection:
            if cd.name.lower() == card_name.lower():
                match_found = True
        if match_found:
            card = target_collection.get(card_name)
            deck.add(card)
            deck.shuffle()
            update_hand_completer()
            update_card_completer()
            update_community_cards_completer()
            print_cards()
            break
        print("ERROR: Match not found, use autocomplete function to confirm matches in formatting\n")

# COMBINE HAND AND COMMUNITY CARD FUNCTION
def get_combined_hand(hand,community_cards):
    combined = hand + community_cards
    return combined

# EVALUATION FUNCTION FOR A HAND
def evaluate_hand(cards):
    value_map = {str(i): i for i in range(2, 11)}
    value_map.update({"Jack": 11, "Queen": 12, "King": 13, "Ace": 14})

    def card_value(card):
        return value_map[card.value]

    sorted_cards = sorted(cards, key=card_value, reverse=True)
    ranks = [card.value for card in sorted_cards]
    suits = [card.suit for card in sorted_cards]
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    card_values = [card_value   (card) for card in sorted_cards]

    if set(ranks) == {"Ace", "King", "Queen", "Jack", "10"} and len(set(suits)) == 1:
        hand_score, hand_type = 10, "Royal Flush"
    elif any(len(set(suits[i:i+5])) == 1 and sorted(card_values[i:i+5], reverse=True) == list(range(max(card_values[i:i+5]), max(card_values[i:i+5]) - 5, -1)) for i in range(len(card_values) - 4)):
        hand_score, hand_type = 9, "Straight Flush"
    elif 4 in rank_counts.values():
        hand_score, hand_type = 8, "Four of a Kind"
    elif sorted(rank_counts.values(), reverse=True)[:2] == [3, 2]:
        hand_score, hand_type = 7, "Full House"
    elif 5 in suit_counts.values():
        hand_score, hand_type = 6, "Flush"
    elif any(card_values[i:i+5] == list(range(card_values[i], card_values[i] - 5, -1)) for i in range(len(card_values) - 4)):
        hand_score, hand_type = 5, "Straight"
    elif 3 in rank_counts.values():
        hand_score, hand_type = 4, "Three of a Kind"
    elif list(rank_counts.values()).count(2) == 2:
        hand_score, hand_type = 3, "Two Pair"
    elif 2 in rank_counts.values():
        hand_score, hand_type = 2, "One Pair"
    else:
        high_card_value = max(card_values)
        hand_score, hand_type = 1 + (high_card_value - 2) / 100.0, f"High Card {sorted_cards[0].value}"
    tiebreaker_score = sum(cv * (15 ** idx) for idx, cv in enumerate(sorted(card_values, reverse=True)))
    return hand_score, hand_type, tiebreaker_score


def simulate_win_probability(player_hand, community_cards, simulations=5000, fixed_num_opponents=None):
    wins = 0
    total_opponents = 0

    for _ in range(simulations):
        if fixed_num_opponents is not None:
            num_opponents = fixed_num_opponents
        else:
            num_opponents = random.randint(1, 5)
        
        total_opponents += num_opponents
        total_players = num_opponents + 1

        simulation_deck = pydealer.Deck()
        simulation_deck.shuffle()

        known_cards = player_hand.cards + community_cards.cards
        for card in known_cards:
            if card in simulation_deck:
                simulation_deck.cards.remove(card)

        opponent_hands = [simulation_deck.deal(2) for _ in range(num_opponents)]

        simulated_community = pydealer.Stack()
        for card in community_cards:
            simulated_community.add(card)
        remaining_community_cards = 5 - len(community_cards)
        simulated_community.add(simulation_deck.deal(remaining_community_cards))

        player_combined = player_hand + simulated_community
        player_score, _, player_tiebreaker = evaluate_hand(player_combined)

        player_wins_round = True
        for opponent_hand in opponent_hands:
            opponent_combined = opponent_hand + simulated_community
            opponent_score, _, opponent_tiebreaker = evaluate_hand(opponent_combined)

            if player_score < opponent_score or (player_score == opponent_score and player_tiebreaker < opponent_tiebreaker):
                player_wins_round = False
                break

        if player_wins_round:
            wins += 1

    average_opponents = total_opponents / simulations
    print("Wins: ", wins)
    print("Simulations: ", simulations)
    print ("Average Opponents: ", average_opponents)
    return wins / simulations


def simulate_win_probability_round_by_round(player_hand, initial_community_cards, num_opponents, simulations=5000):
    stages = ['Hand', 'Flop', 'Turn', 'River']
    win_percentages = []

    for stage in stages:
        wins = 0
        for _ in range(simulations):
            simulation_deck = pydealer.Deck()
            simulation_deck.shuffle()

            known_cards = player_hand.cards + initial_community_cards.cards
            for card in known_cards:
                if card in simulation_deck:
                    simulation_deck.cards.remove(card)

            opponent_hands = [simulation_deck.deal(2) for _ in range(num_opponents)]

            simulated_community = pydealer.Stack()
            if initial_community_cards.size > 0:
                for card in initial_community_cards:
                    simulated_community.add(card)

            if stage == 'Flop' and simulated_community.size < 3:
                simulated_community.add(simulation_deck.deal(3 - simulated_community.size))
            elif stage == 'Turn' and simulated_community.size < 4:
                simulated_community.add(simulation_deck.deal(1))
            elif stage == 'River' and simulated_community.size < 5:
                simulated_community.add(simulation_deck.deal(1))

            player_combined = player_hand + simulated_community
            player_score, _, player_tiebreaker = evaluate_hand(player_combined)
            player_wins_round = True

            for opponent_hand in opponent_hands:
                opponent_combined = opponent_hand + simulated_community
                opponent_score, _, opponent_tiebreaker = evaluate_hand(opponent_combined)

                if player_score < opponent_score or (player_score == opponent_score and player_tiebreaker < opponent_tiebreaker):
                    player_wins_round = False
                    break

            if player_wins_round:
                wins += 1

        win_percentage = (wins / simulations) * 100
        win_percentages.append(win_percentage)

    return win_percentages

def simulate_and_record_win_probability(hand, community_cards, num_opponents, simulations=5000):
    hand_description = ', '.join([str(card) for card in hand])
    community_cards_description = ', '.join([str(card) for card in community_cards])
    file_name = f'stats_{num_opponents + 1}_players.csv'
    
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['Simulation', 'Hand', 'Flop', 'Turn', 'River', 'Player Hand', 'Community Cards']
        writer.writerow(header)

        for simulation in range(simulations):
            win_percentages = simulate_win_probability_round_by_round(hand, community_cards, num_opponents, simulations=1)
            record = [simulation + 1] + win_percentages + [hand_description, community_cards_description]
            writer.writerow(record)

def add_specific_card_to_collection(collection, card_name):
    global hand, community_cards, deck
    for cd in deck:
        if cd.name.lower() == card_name.lower():
            if collection == "hand" and hand.size < 2:
                hand.add(deck.get(card_name))
            elif collection == "community_cards" and community_cards.size < 5:
                community_cards.add(deck.get(card_name))
            update_card_completer()
            update_hand_completer()
            update_community_cards_completer()
            return True
    return False

def generate_preset_hand(hand_type):
    global hand, community_cards, deck
    deck = pydealer.Deck()
    deck.shuffle()

    # Reset hand and community cards
    hand.empty()
    community_cards.empty()

    if hand_type == "6 high":
        # Hand: 6 high, rest random
        add_specific_card_to_collection("hand", "6 of Spades")
        add_specific_card_to_collection("hand", "3 of Clubs")
    elif hand_type == "ace high":
        # Hand: Ace high, rest random
        add_specific_card_to_collection("hand", "Ace of Hearts")
        add_specific_card_to_collection("hand", "4 of Diamonds")
    elif hand_type == "one pair":
        # Hand: One pair
        add_specific_card_to_collection("hand", "9 of Hearts")
        add_specific_card_to_collection("hand", "9 of Clubs")
    elif hand_type == "two pair":
        # Hand: Two pair
        add_specific_card_to_collection("hand", "8 of Hearts")
        add_specific_card_to_collection("hand", "8 of Clubs")
        add_specific_card_to_collection("community_cards", "4 of Diamonds")
        add_specific_card_to_collection("community_cards", "4 of Spades")
    elif hand_type == "three of a kind":
        # Hand: Three of a kind
        add_specific_card_to_collection("hand", "7 of Hearts")
        add_specific_card_to_collection("hand", "7 of Diamonds")
        add_specific_card_to_collection("community_cards", "7 of Clubs")
    elif hand_type == "straight":
        # Hand: Straight
        add_specific_card_to_collection("hand", "5 of Hearts")
        add_specific_card_to_collection("hand", "6 of Diamonds")
        add_specific_card_to_collection("community_cards", "7 of Clubs")
        add_specific_card_to_collection("community_cards", "8 of Spades")
        add_specific_card_to_collection("community_cards", "9 of Clubs")
    elif hand_type == "flush":
        # Hand: Flush (all hearts for simplicity)
        add_specific_card_to_collection("community_cards", "2 of Hearts")
        add_specific_card_to_collection("community_cards", "4 of Hearts")
        add_specific_card_to_collection("community_cards", "7 of Hearts")
        add_specific_card_to_collection("community_cards", "8 of Hearts")
        add_specific_card_to_collection("community_cards", "10 of Hearts")
    elif hand_type == "full house":
        # Hand: Full house
        add_specific_card_to_collection("hand", "10 of Diamonds")
        add_specific_card_to_collection("hand", "10 of Clubs")
        add_specific_card_to_collection("community_cards", "10 of Hearts")
        add_specific_card_to_collection("community_cards", "3 of Spades")
        add_specific_card_to_collection("community_cards", "3 of Clubs")
    elif hand_type == "four of a kind":
        # Hand: Four of a kind
        add_specific_card_to_collection("hand", "Queen of Hearts")
        add_specific_card_to_collection("hand", "Queen of Diamonds")
        add_specific_card_to_collection("community_cards", "Queen of Clubs")
        add_specific_card_to_collection("community_cards", "Queen of Spades")
    elif hand_type == "straight flush":
        # Hand: Straight Flush (all spades for simplicity)
        add_specific_card_to_collection("hand", "9 of Spades")
        add_specific_card_to_collection("hand", "10 of Spades")
        add_specific_card_to_collection("community_cards", "Jack of Spades")
        add_specific_card_to_collection("community_cards", "Queen of Spades")
        add_specific_card_to_collection("community_cards", "King of Spades")
    elif hand_type == "royal flush":
        # Hand: Royal Flush (all hearts for simplicity)
        add_specific_card_to_collection("hand", "10 of Hearts")
        add_specific_card_to_collection("hand", "Jack of Hearts")
        add_specific_card_to_collection("community_cards", "Queen of Hearts")
        add_specific_card_to_collection("community_cards", "King of Hearts")
        add_specific_card_to_collection("community_cards", "Ace of Hearts")

    # Deal remaining community cards if necessary
    while community_cards.size < 5:
        community_cards.add(deck.deal(1))

    hand.sort()
    community_cards.sort()
    print("Hand has been set. Returning to main menu.")

def preset_hand_menu():
    preset_options = {
        "1": "6 high",
        "2": "ace high",
        "3": "one pair",
        "4": "two pair",
        "5": "three of a kind",
        "6": "straight",
        "7": "flush",
        "8": "full house",
        "9": "four of a kind",
        "10": "straight flush",
        "11": "royal flush",
        "12": "Exit"
    }
    while True:
        print("\n---Preset Hand Options---")
        for key, value in preset_options.items():
            print(f"{key}. {value}")

        choice = input("Choose an option: ")
        if choice == "12":
            break
        elif choice in preset_options:
            generate_preset_hand(preset_options[choice])
            #print_cards()
            break
        else:
            print("Invalid option, please choose again.")




# --------------------------------------------------------------------------------- GAME DATA ---------------------------------------------------------------------------------
hand_size = 0
community_card_size = 0
# --------------------------------------------------------------------------------- GAME DATA ---------------------------------------------------------------------------------
# START GAME
initialize_game(hand_size,community_card_size)

# ===>MAIN LOOP <===
while True:
    userInput = prompt("\n\n\n---Show Collections---\n1. Show Hand\n2. Show Deck\n3. Show Community Cards\n\n---Add Cards to Collections---\n4. Add a card to hand\n5. Add Card to Community Cards\n\n---Remove Cards from Collections---\n6. Remove a card from hand\n7. Remove Card from Community Cards\n\n---Functionality---\n8. Reshuffle and Reset\n9. Statistics given current table (random player count)\n10. Statistics given 'N' players with visuals(jupyter notebook code uses csv generated from this option)\n11. Try preset hands\n12. Exit\n")
    
    # 1. Show Hand
    if userInput == '1':
        print_hand()

    # 2. Show Deck
    elif userInput == '2':
        print_deck()

    # 3. Show Community Cards
    elif userInput == '3':
        print_comm_card()

    # 4. Add Card to Hand
    elif userInput == '4':
        add_card_to_collection("hand", card_completer)

    # 5. Add Card to Community Cards
    elif userInput == '5':
        add_card_to_collection("community_cards", card_completer)

    # 6. Remove Card from Hand
    elif userInput == '6':
        remove_card_from_collection("hand", hand_completer)

    # 7. Remove Card from Community Cards
    elif userInput == '7':
        remove_card_from_collection("community_cards", community_card_completer)

    # 8. Reshuffle and Reset
    elif userInput == '8':
        initialize_game(hand_size, community_card_size)
        #print_cards()

    # 9. Statistics
    elif userInput == '9':
        combined = get_combined_hand(hand,community_cards)
        print("Combined hand: \n", combined)
        score, hand_type, tiebreaker_score = evaluate_hand(combined)
        print(f"Hand: {hand_type}, Score: {score}/10")
        win_probability = simulate_win_probability(hand, community_cards) * 100
        print(f"Chance to win: {win_probability:.2f}%")
    elif userInput == '10':
        combined = get_combined_hand(hand, community_cards)
        print("Combined hand: \n", combined)
        score, hand_type, tiebreaker_score = evaluate_hand(combined)
        print(f"Hand: {hand_type}, Score: {score}/10")
        for num_opponents in range(1, 7):
            win_probability = simulate_win_probability(hand, community_cards, fixed_num_opponents=num_opponents) * 100
            simulate_and_record_win_probability(hand, community_cards, num_opponents=num_opponents)
            print(f"Chance to win against {num_opponents + 1} players: {win_probability:.2f}%")
    
    # 11. Preset Menu
    elif userInput == '11':
        preset_hand_menu()

    # 12. Exit
    elif userInput == '12':
        break
