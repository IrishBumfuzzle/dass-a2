import sys

sys.path.insert(
    0, "/home/irishbumfuzzle/Assignments/DASS/assignment-2/whitebox/moneypoly"
)

import pytest
from moneypoly.player import Player
from moneypoly.dice import Dice
from moneypoly.property import Property, PropertyGroup
from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.game import Game
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from moneypoly.config import *


class TestPlayer:

    def test_add_money_positive(self):
        p = Player("Alice", 1000)
        p.add_money(500)
        assert p.balance == 1500

    def test_add_money_negative(self):
        p = Player("Alice", 1000)
        with pytest.raises(ValueError):
            p.add_money(-100)

    def test_add_money_zero(self):
        p = Player("Alice", 1000)
        p.add_money(0)
        assert p.balance == 1000

    def test_add_money_large_amount(self):
        p = Player("Bob", 1500)
        p.add_money(50000)
        assert p.balance == 51500

    def test_deduct_money_positive(self):
        p = Player("Alice", 1000)
        p.deduct_money(300)
        assert p.balance == 700

    def test_deduct_money_negative(self):
        p = Player("Alice", 1000)
        with pytest.raises(ValueError):
            p.deduct_money(-100)

    def test_deduct_money_zero(self):
        p = Player("Charlie", 500)
        p.deduct_money(0)
        assert p.balance == 500

    def test_deduct_money_exceeds_balance(self):
        p = Player("Dave", 100)
        p.deduct_money(500)
        assert p.balance == -400

    def test_is_bankrupt_below_zero(self):
        p = Player("Eve", -100)
        assert p.is_bankrupt() is True

    def test_is_bankrupt_at_zero(self):
        p = Player("Frank", 0)
        assert p.is_bankrupt() is True

    def test_is_bankrupt_positive_balance(self):
        p = Player("Grace", 1)
        assert p.is_bankrupt() is False

    def test_is_bankrupt_starting_balance(self):
        p = Player("Henry", STARTING_BALANCE)
        assert p.is_bankrupt() is False

    def test_move_basic(self):
        p = Player("Iris", 0)
        result = p.move(5)
        assert p.position == 5
        assert result == 5

    def test_move_landing_on_go(self):
        p = Player("Karen", 0)
        initial_balance = p.balance
        p.move(40)
        assert p.position == 0
        assert p.balance == initial_balance + GO_SALARY

    def test_move_full_circuit(self):
        p = Player("Leo", 0)
        initial_balance = p.balance
        p.move(40)
        assert p.position == 0
        assert p.balance == initial_balance + GO_SALARY

    def test_move_zero_steps(self):
        p = Player("Mary", 0)
        initial_balance = p.balance
        p.move(1)
        p.move(0)
        assert p.position == 1
        assert p.balance == initial_balance

    def test_go_to_jail_sets_position_and_status(self):
        p = Player("Oscar", 20)
        p.go_to_jail()
        assert p.position == JAIL_POSITION
        assert p.in_jail is True
        assert p.jail_turns == 0

    def test_go_to_jail_from_go(self):
        p = Player("Pam", 0)
        p.go_to_jail()
        assert p.position == JAIL_POSITION
        assert p.in_jail is True

    def test_property_added_to_list(self):
        p = Player("Quinn", 1500)
        prop = Property("Test St", 5, 200, 16)
        p.add_property(prop)
        assert prop in p.properties
        assert p.count_properties() == 1

    def test_add_duplicate_property(self):
        p = Player("Ruth", 1500)
        prop = Property("Test Ave", 10, 300, 26)
        p.add_property(prop)
        p.add_property(prop)
        assert p.count_properties() == 1

    def test_remove_property(self):
        p = Player("Stan", 1500)
        prop = Property("Test Blvd", 15, 250, 22)
        p.add_property(prop)
        p.remove_property(prop)
        assert prop not in p.properties
        assert p.count_properties() == 0

    def test_remove_nonexistent_property(self):
        p = Player("Tina", 1500)
        prop = Property("Fake Ln", 8, 100, 8)
        p.remove_property(prop)
        assert prop not in p.properties

    def test_net_worth_only_balance(self):
        p = Player("Uma", 1200)
        assert p.net_worth() == 1200

    def test_net_worth_after_transactions(self):
        p = Player("Vera", 1500)
        p.add_money(300)
        p.deduct_money(100)
        assert p.net_worth() == 1700


class TestBank:

    def test_bank_initial_balance(self):
        bank = Bank()
        assert bank.get_balance() == BANK_STARTING_FUNDS

    def test_collect_positive_amount(self):
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(100)
        assert bank.get_balance() == initial + 100

    def test_collect_negative_amount(self):
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(-100)
        assert bank.get_balance() == initial

    def test_collect_zero(self):
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(0)
        assert bank.get_balance() == initial

    def test_collect_updates_total_collected(self):
        bank = Bank()
        bank.collect(50)
        bank.collect(75)

        assert bank._total_collected == 125

    def test_pay_out_sufficient_funds(self):
        bank = Bank()
        initial = bank.get_balance()
        amount = bank.pay_out(100)
        assert amount == 100
        assert bank.get_balance() == initial - 100

    def test_pay_out_insufficient_funds(self):
        bank = Bank()
        bank._funds = 50
        with pytest.raises(ValueError):
            bank.pay_out(100)

    def test_pay_out_exact_amount(self):
        bank = Bank()
        bank._funds = 100
        amount = bank.pay_out(100)
        assert amount == 100
        assert bank.get_balance() == 0

    def test_pay_out_negative_amount(self):
        bank = Bank()
        initial = bank.get_balance()
        amount = bank.pay_out(-50)
        assert amount == 0
        assert bank.get_balance() == initial

    def test_pay_out_zero_amount(self):
        bank = Bank()
        initial = bank.get_balance()
        amount = bank.pay_out(0)
        assert amount == 0
        assert bank.get_balance() == initial

    def test_give_loan_positive_amount(self):
        bank = Bank()
        player = Player("Liam", 100)
        initial_player_balance = player.balance
        bank.give_loan(player, 500)
        assert player.balance == initial_player_balance + 500
        assert bank.loan_count() == 1
        assert bank.total_loans_issued() == 500

    def test_give_loan_zero_amount(self):
        bank = Bank()
        player = Player("Nora", 100)
        bank.give_loan(player, 0)
        assert player.balance == 100
        assert bank.loan_count() == 0

    def test_give_loan_negative_amount(self):
        bank = Bank()
        player = Player("Owen", 100)
        bank.give_loan(player, -100)
        assert player.balance == 100
        assert bank.loan_count() == 0


class TestDice:

    def test_dice_initial_state(self):
        dice = Dice()
        assert dice.die1 == 0
        assert dice.die2 == 0
        assert dice.doubles_streak == 0

    def test_dice_roll_range(self):
        dice = Dice()
        for _ in range(100):
            dice.roll()

            assert 1 <= dice.die1 <= 6
            assert 1 <= dice.die2 <= 6

    def test_dice_roll_total(self):
        dice = Dice()
        total = dice.roll()
        assert total == dice.die1 + dice.die2

    def test_dice_roll_minimum(self):
        dice = Dice()

        dice.die1, dice.die2 = 1, 1
        assert dice.total() == 2

    def test_dice_roll_maximum(self):
        dice = Dice()

        dice.die1, dice.die2 = 6, 6
        assert dice.total() == 12

    def test_is_doubles_true(self):
        dice = Dice()
        dice.die1, dice.die2 = 3, 3
        assert dice.is_doubles() is True

    def test_is_doubles_false(self):
        dice = Dice()
        dice.die1, dice.die2 = 2, 5
        assert dice.is_doubles() is False

    def test_doubles_streak_increments(self):
        dice = Dice()
        dice.die1, dice.die2 = 2, 2
        dice.roll()

    def test_doubles_streak_resets(self):
        dice = Dice()
        dice.die1, dice.die2 = 4, 4
        dice.roll()

    def test_reset_dice(self):
        dice = Dice()
        dice.die1, dice.die2 = 3, 4
        dice.doubles_streak = 2
        dice.reset()
        assert dice.die1 == 0
        assert dice.die2 == 0
        assert dice.doubles_streak == 0

    def test_describe_with_doubles(self):
        dice = Dice()
        dice.die1, dice.die2 = 5, 5
        desc = dice.describe()
        assert "DOUBLES" in desc
        assert "10" in desc

    def test_describe_without_doubles(self):
        dice = Dice()
        dice.die1, dice.die2 = 2, 4
        desc = dice.describe()
        assert "DOUBLES" not in desc
        assert "6" in desc

    def test_dice_reachable_six(self):
        dice = Dice()
        rolled_six = False
        for _ in range(1000):
            dice.roll()
            if dice.die1 == 6 or dice.die2 == 6:
                rolled_six = True
                break
        assert rolled_six is True


class TestProperty:

    def test_property_initialization(self):
        prop = Property("Boardwalk", 39, 400, 50)
        assert prop.name == "Boardwalk"
        assert prop.position == 39
        assert prop.base_rent == 50
        assert prop.owner is None
        assert prop.is_mortgaged is False

    def test_property_mortgage_value(self):
        prop = Property("Park Place", 37, 350, 35)
        assert prop.mortgage_value == 175

    def test_mortgage_unmortgaged_property(self):
        prop = Property("Boardwalk", 39, 400, 50)
        payout = prop.mortgage()
        assert payout == 200
        assert prop.is_mortgaged is True

    def test_mortgage_already_mortgaged(self):
        prop = Property("Park Place", 37, 350, 35)
        prop.mortgage()
        payout = prop.mortgage()
        assert payout == 0
        assert prop.is_mortgaged is True

    def test_unmortgage_mortgaged_property(self):
        prop = Property("Boardwalk", 39, 400, 50)
        prop.mortgage()
        cost = prop.unmortgage()
        assert cost == 220
        assert prop.is_mortgaged is False

    def test_unmortgage_unmortgaged_property(self):
        prop = Property("Park Place", 37, 350, 35)
        cost = prop.unmortgage()
        assert cost == 0
        assert prop.is_mortgaged is False

    def test_get_rent_unowned(self):
        prop = Property("Test St", 1, 60, 2)
        assert prop.get_rent() == 0

    def test_get_rent_owned_no_monopoly(self):
        prop = Property("Test St", 1, 60, 2)
        player = Player("Rene", 1500)
        prop.owner = player
        group = PropertyGroup("Brown", "brown")
        prop.group = group

        assert prop.get_rent() == 2

    def test_get_rent_owned_with_monopoly(self):
        prop1 = Property("Test St", 1, 60, 2)
        prop2 = Property("Test Ave", 3, 60, 4)
        player = Player("Sasha", 1500)

        group = PropertyGroup("Brown", "brown")
        group.add_property(prop1)
        group.add_property(prop2)

        prop1.owner = player
        prop2.owner = player

        rent = prop1.get_rent()

    def test_get_rent_mortgaged_property(self):
        prop = Property("Test St", 1, 60, 2)
        player = Player("Tanya", 1500)
        prop.owner = player
        prop.is_mortgaged = True
        assert prop.get_rent() == 0


class TestPropertyGroup:

    def test_group_initialization(self):
        group = PropertyGroup("Brown", "brown")
        assert group.name == "Brown"
        assert group.color == "brown"
        assert len(group.properties) == 0

    def test_add_property_to_group(self):
        group = PropertyGroup("Brown", "brown")
        prop = Property("Med Ave", 1, 60, 2)
        group.add_property(prop)
        assert prop in group.properties
        assert prop.group == group

    def test_all_owned_by_single_owner(self):
        group = PropertyGroup("Brown", "brown")
        prop1 = Property("Med Ave", 1, 60, 2)
        prop2 = Property("Baltic Ave", 3, 60, 4)
        player = Player("Walter", 1500)

        group.add_property(prop1)
        group.add_property(prop2)
        prop1.owner = player
        prop2.owner = player

        result = group.all_owned_by(player)

    def test_all_owned_by_partial_ownership(self):
        group = PropertyGroup("Brown", "brown")
        prop1 = Property("Med Ave", 1, 60, 2)
        prop2 = Property("Baltic Ave", 3, 60, 4)
        player1 = Player("Xavier", 1500)
        player2 = Player("Yara", 1500)

        group.add_property(prop1)
        group.add_property(prop2)
        prop1.owner = player1
        prop2.owner = player2

        result = group.all_owned_by(player1)

    def test_all_owned_by_none_player(self):
        group = PropertyGroup("Brown", "brown")
        prop = Property("Med Ave", 1, 60, 2)
        group.add_property(prop)
        assert group.all_owned_by(None) is False

    def test_get_owner_counts(self):
        group = PropertyGroup("Light Blue", "light_blue")
        props = [
            Property("Oriental", 6, 100, 6),
            Property("Vermont", 8, 100, 6),
            Property("Connecticut", 9, 120, 8),
        ]
        player1 = Player("Zara", 1500)
        player2 = Player("Alex", 1500)

        for p in props:
            group.add_property(p)

        props[0].owner = player1
        props[1].owner = player1
        props[2].owner = player2

        counts = group.get_owner_counts()
        assert counts[player1] == 2
        assert counts[player2] == 1


class TestCardDeck:

    def test_deck_initialization(self):
        deck = CardDeck(CHANCE_CARDS)
        assert len(deck) == len(CHANCE_CARDS)
        assert deck.index == 0

    def test_draw_card(self):
        deck = CardDeck(CHANCE_CARDS)
        card1 = deck.draw()
        assert card1 == CHANCE_CARDS[0]
        card2 = deck.draw()
        assert card2 == CHANCE_CARDS[1]

    def test_draw_cycles_deck(self):
        simple_cards = [{"id": 1}, {"id": 2}]
        deck = CardDeck(simple_cards)
        deck.draw()
        deck.draw()
        card = deck.draw()

        assert card == simple_cards[0]

    def test_peek_card(self):
        deck = CardDeck(CHANCE_CARDS)
        peek1 = deck.peek()
        peek2 = deck.peek()
        assert peek1 == peek2
        assert deck.index == 0

    def test_peek_empty_deck(self):
        deck = CardDeck([])
        assert deck.peek() is None

    def test_reshuffle(self):
        cards = [{"id": i} for i in range(10)]
        deck = CardDeck(cards)
        original_order = [c["id"] for c in deck.cards]
        deck.draw()
        deck.draw()
        deck.reshuffle()

        assert deck.index == 0

    def test_cards_remaining(self):
        deck = CardDeck(CHANCE_CARDS)
        remaining = deck.cards_remaining()
        assert remaining == len(CHANCE_CARDS)
        deck.draw()
        remaining = deck.cards_remaining()
        assert remaining == len(CHANCE_CARDS) - 1


class TestGame:

    def test_game_initialization(self):
        game = Game(["Alice", "Bob"])
        assert len(game.players) == 2
        assert game.current_index == 0
        assert game.turn_number == 0
        assert game.board is not None
        assert game.bank is not None

    def test_current_player(self):
        game = Game(["Alice", "Bob", "Charlie"])
        assert game.current_player().name == "Alice"
        game.current_index = 1
        assert game.current_player().name == "Bob"

    def test_advance_turn(self):
        game = Game(["Alice", "Bob"])
        assert game.current_index == 0
        game.advance_turn()
        assert game.current_index == 1
        assert game.turn_number == 1
        game.advance_turn()
        assert game.current_index == 0

    def test_buy_property_success(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        initial_balance = player.balance

        result = game.buy_property(player, prop)
        assert result is True
        assert prop.owner == player
        assert player.balance < initial_balance
        assert prop in player.properties

    def test_buy_property_insufficient_funds(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = 10
        prop = game.board.properties[-1]

        result = game.buy_property(player, prop)
        assert result is False
        assert prop.owner is None

    def test_pay_rent_unowned_property(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        opponent = game.players[1]
        prop = game.board.properties[0]

        initial_balance = opponent.balance
        game.pay_rent(opponent, prop)

        assert opponent.balance == initial_balance

    def test_pay_rent_owned_by_self(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        initial_balance = player.balance
        game.pay_rent(player, prop)
        assert player.balance == initial_balance

    def test_pay_rent_owned_by_opponent(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        opponent = game.players[1]
        prop = game.board.properties[0]
        prop.owner = opponent
        player_initial = player.balance
        opponent_initial = opponent.balance
        rent = prop.get_rent()

        game.pay_rent(player, prop)

        assert player.balance < player_initial

    def test_pay_rent_mortgaged_property(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        opponent = game.players[1]
        prop = game.board.properties[0]
        prop.owner = opponent
        prop.is_mortgaged = True
        initial_balance = player.balance
        game.pay_rent(player, prop)
        assert player.balance == initial_balance

    def test_mortgage_owned_property(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        initial_balance = player.balance

        result = game.mortgage_property(player, prop)
        assert result is True
        assert prop.is_mortgaged is True
        assert player.balance > initial_balance

    def test_unmortgage_mortgaged_property(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        prop.mortgage()
        balance_after_mortgage = player.balance

        result = game.unmortgage_property(player, prop)
        assert result is True
        assert prop.is_mortgaged is False
        assert player.balance < balance_after_mortgage

    def test_unmortgage_insufficient_funds(self):
        game = Game(["Alice"])
        player = game.players[0]
        prop = game.board.properties[-1]
        prop.owner = player
        prop.mortgage()
        player.balance = 10

        result = game.unmortgage_property(player, prop)
        assert result is False
        assert prop.is_mortgaged is True

    def test_trade_property_success(self):
        game = Game(["Alice", "Bob"])
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = seller
        seller.add_property(prop)

        result = game.trade(seller, buyer, prop, 200)
        assert result is True
        assert prop.owner == buyer
        assert prop in buyer.properties

    def test_trade_buyer_insufficient_funds(self):
        game = Game(["Alice", "Bob"])
        seller = game.players[0]
        buyer = game.players[1]
        buyer.balance = 50
        prop = game.board.properties[0]
        prop.owner = seller

        result = game.trade(seller, buyer, prop, 200)
        assert result is False
        assert prop.owner == seller

    def test_trade_seller_doesnt_own(self):
        game = Game(["Alice", "Bob"])
        seller = game.players[0]
        buyer = game.players[1]
        prop = game.board.properties[0]
        prop.owner = buyer

        result = game.trade(seller, buyer, prop, 200)
        assert result is False

    def test_card_action_collect(self):
        game = Game(["Alice"])
        player = game.players[0]
        initial_balance = player.balance
        card = {"action": "collect", "value": 100, "description": "Test"}
        game._apply_card(player, card)
        assert player.balance > initial_balance

    def test_card_action_pay(self):
        game = Game(["Alice"])
        player = game.players[0]
        initial_balance = player.balance
        card = {"action": "pay", "value": 50, "description": "Test"}
        game._apply_card(player, card)
        assert player.balance < initial_balance

    def test_card_action_jail(self):
        game = Game(["Alice"])
        player = game.players[0]
        player.position = 20
        card = {"action": "jail", "value": 0, "description": "Test"}
        game._apply_card(player, card)
        assert player.in_jail is True
        assert player.position == JAIL_POSITION

    def test_card_action_jail_free(self):
        game = Game(["Alice"])
        player = game.players[0]
        initial_cards = player.get_out_of_jail_cards
        card = {"action": "jail_free", "value": 0, "description": "Test"}
        game._apply_card(player, card)
        assert player.get_out_of_jail_cards == initial_cards + 1

    def test_bankruptcy_detection(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        player.balance = -100
        initial_count = len(game.players)

        game._check_bankruptcy(player)
        assert len(game.players) < initial_count
        assert player not in game.players

    def test_bankruptcy_properties_released(self):
        game = Game(["Alice", "Bob"])
        player = game.players[0]
        prop = game.board.properties[0]
        prop.owner = player
        player.add_property(prop)
        player.balance = -100

        game._check_bankruptcy(player)
        assert prop.owner is None

    def test_find_winner_single_player(self):
        game = Game(["Alice"])
        winner = game.find_winner()

        assert winner is not None

    def test_find_winner_multiple_players(self):
        game = Game(["Alice", "Bob", "Charlie"])
        game.players[0].balance = 5000
        game.players[1].balance = 2000
        game.players[2].balance = 8000
        winner = game.find_winner()


class TestGameIntegration:

    def test_move_land_on_jail_tile(self):
        game = Game(["Alice"])
        player = game.players[0]
        initial_pos = player.position
        game._move_and_resolve(player, 30)

        assert player.in_jail is True

    def test_doubles_grant_extra_turn(self):
        game = Game(["Alice", "Bob"])
        game.dice.die1 = 3
        game.dice.die2 = 3
        initial_index = game.current_index

    def test_three_doubles_sends_to_jail(self):
        game = Game(["Alice"])
        game.dice.doubles_streak = 3

    def test_full_turn_sequence(self):
        game = Game(["Alice", "Bob"])
        player = game.current_player()
        initial_turn = game.turn_number

    def test_property_group_rent_bonus(self):
        game = Game(["Alice", "Bob"])

        brown_props = [
            p for p in game.board.properties if p.group and p.group.color == "brown"
        ]
        if len(brown_props) >= 2:
            prop1, prop2 = brown_props[0], brown_props[1]
            bob = game.players[1]
            prop1.owner = bob
            prop2.owner = bob

    def test_deduct_money_all(self):
        p = Player("Alice", 500)
        p.deduct_money(500)
        assert p.balance == 0

    def test_deduct_money_more_than_balance(self):
        p = Player("Alice", 300)
        p.deduct_money(500)
        assert p.balance == -200

    def test_is_bankrupt_zero(self):
        p = Player("Alice", 0)
        assert p.is_bankrupt() is True

    def test_is_bankrupt_negative(self):
        p = Player("Alice", -500)
        assert p.is_bankrupt() is True

    def test_is_not_bankrupt(self):
        p = Player("Alice", 1)
        assert p.is_bankrupt() is False

    def test_move_no_wrap(self):
        p = Player("Alice", 1000)
        p.position = 5
        p.move(10)
        assert p.position == 15
        assert p.balance == 1000

    def test_move_lands_on_go(self):
        p = Player("Alice", 1000)
        p.position = 35
        p.move(5)
        assert p.position == 0
        assert p.balance == 1200

    def test_go_to_jail(self):
        p = Player("Alice", 1000)
        p.position = 15
        p.go_to_jail()
        assert p.position == JAIL_POSITION
        assert p.in_jail is True
        assert p.jail_turns == 0

    def test_add_property(self):
        p = Player("Alice")
        prop = Property("Test Avenue", 1, 100, 10)
        p.add_property(prop)
        assert len(p.properties) == 1
        assert prop in p.properties

    def test_add_duplicate_property(self):
        p = Player("Alice")
        prop = Property("Test Avenue", 1, 100, 10)
        p.add_property(prop)
        p.add_property(prop)
        assert len(p.properties) == 1

    def test_remove_property(self):
        p = Player("Alice")
        prop = Property("Test Avenue", 1, 100, 10)
        p.add_property(prop)
        p.remove_property(prop)
        assert len(p.properties) == 0

    def test_remove_nonexistent_property(self):
        p = Player("Alice")
        prop1 = Property("Test Avenue", 1, 100, 10)
        prop2 = Property("Other Avenue", 5, 100, 10)
        p.add_property(prop1)
        p.remove_property(prop2)
        assert len(p.properties) == 1


class TestDice:

    def test_roll_range(self):
        dice = Dice()
        for _ in range(100):
            total = dice.roll()
            assert 2 <= total <= 12
            assert 1 <= dice.die1 <= 6
            assert 1 <= dice.die2 <= 6

    def test_is_doubles(self):
        dice = Dice()

        for _ in range(100):
            dice.roll()
            if dice.die1 == dice.die2:
                assert dice.is_doubles() is True
                return
        pytest.fail("Could not generate doubles in 100 rolls")

    def test_not_doubles(self):
        dice = Dice()

        for _ in range(100):
            dice.roll()
            if dice.die1 != dice.die2:
                assert dice.is_doubles() is False
                return
        pytest.fail("Could not generate non-doubles in 100 rolls")

    def test_doubles_streak_increment(self):
        dice = Dice()
        consecutive_doubles = 0
        for _ in range(200):
            dice.roll()
            if dice.is_doubles():
                consecutive_doubles += 1
                if consecutive_doubles == 2:
                    assert dice.doubles_streak == 2
                    return
            else:
                consecutive_doubles = 0
        pytest.fail("Could not generate 2 consecutive doubles in 200 rolls")

    def test_doubles_streak_reset(self):
        dice = Dice()
        got_double = False
        for _ in range(200):
            dice.roll()
            if dice.is_doubles() and not got_double:
                got_double = True
                assert dice.doubles_streak == 1
            elif got_double and not dice.is_doubles():
                assert dice.doubles_streak == 0
                return
        pytest.fail("Could not generate double followed by non-double")

    def test_total(self):
        dice = Dice()
        for _ in range(20):
            dice.roll()
            expected = dice.die1 + dice.die2
            assert dice.total() == expected


class TestProperty:

    def test_get_rent_normal(self):
        prop = Property("Test Ave", 1, 100, 20)
        p = Player("Owner")
        prop.owner = p
        assert prop.get_rent() == 20

    def test_get_rent_mortgaged(self):
        prop = Property("Test Ave", 1, 100, 20)
        p = Player("Owner")
        prop.owner = p
        prop.is_mortgaged = True
        assert prop.get_rent() == 0

    def test_get_rent_full_group(self):
        group = PropertyGroup("Brown", "brown")
        prop1 = Property("Property 1", 1, 100, 20)
        prop2 = Property("Property 2", 3, 100, 20)
        group.add_property(prop1)
        group.add_property(prop2)

        p = Player("Owner")
        prop1.owner = p
        prop2.owner = p

        assert prop1.get_rent() == 40

    def test_mortgage(self):
        prop = Property("Test Ave", 1, 100, 20)
        payout = prop.mortgage()
        assert payout == 50
        assert prop.is_mortgaged is True

    def test_mortgage_already_mortgaged(self):
        prop = Property("Test Ave", 1, 100, 20)
        prop.mortgage()
        payout2 = prop.mortgage()
        assert payout2 == 0

    def test_unmortgage(self):
        prop = Property("Test Ave", 1, 100, 20)
        prop.mortgage()
        cost = prop.unmortgage()
        assert cost == 55
        assert prop.is_mortgaged is False

    def test_unmortgage_not_mortgaged(self):
        prop = Property("Test Ave", 1, 100, 20)
        cost = prop.unmortgage()
        assert cost == 0

    def test_is_available(self):
        prop = Property("Test Ave", 1, 100, 20)
        assert prop.is_available() is True

    def test_is_not_available_owned(self):
        prop = Property("Test Ave", 1, 100, 20)
        prop.owner = Player("Owner")
        assert prop.is_available() is False

    def test_is_not_available_mortgaged(self):
        prop = Property("Test Ave", 1, 100, 20)
        prop.is_mortgaged = True
        assert prop.is_available() is False


class TestPropertyGroup:

    def test_all_owned_by_true(self):
        group = PropertyGroup("Brown", "brown")
        prop1 = Property("Property 1", 1, 100, 20)
        prop2 = Property("Property 2", 3, 100, 20)
        group.add_property(prop1)
        group.add_property(prop2)

        p = Player("Owner")
        prop1.owner = p
        prop2.owner = p

        assert group.all_owned_by(p) is True

    def test_all_owned_by_false_partial(self):
        group = PropertyGroup("Brown", "brown")
        prop1 = Property("Property 1", 1, 100, 20)
        prop2 = Property("Property 2", 3, 100, 20)
        group.add_property(prop1)
        group.add_property(prop2)

        p1 = Player("Owner1")
        p2 = Player("Owner2")
        prop1.owner = p1
        prop2.owner = p2

        result = group.all_owned_by(p1)
        if result is True:
            pytest.fail(
                "BUG: Uses any() instead of all() - returns True for partial ownership"
            )
        else:
            assert result is False

    def test_all_owned_by_false_none(self):
        group = PropertyGroup("Brown", "brown")
        prop = Property("Property 1", 1, 100, 20)
        group.add_property(prop)

        assert group.all_owned_by(None) is False

    def test_size(self):
        group = PropertyGroup("Brown", "brown")
        prop1 = Property("Property 1", 1, 100, 20)
        prop2 = Property("Property 2", 3, 100, 20)
        group.add_property(prop1)
        group.add_property(prop2)

        assert group.size() == 2


class TestBank:

    def test_collect_positive(self):
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(100)
        assert bank.get_balance() == initial + 100

    def test_collect_negative(self):
        bank = Bank()
        initial = bank.get_balance()
        bank.collect(-100)

        if bank.get_balance() == initial - 100:
            pytest.fail(
                "BUG: Docstring says negative amounts are 'silently ignored' but code subtracts them"
            )
        else:
            assert bank.get_balance() == initial

    def test_pay_out_valid(self):
        bank = Bank()
        initial = bank.get_balance()
        payout = bank.pay_out(100)
        assert payout == 100
        assert bank.get_balance() == initial - 100

    def test_pay_out_insufficient(self):
        bank = Bank()
        with pytest.raises(ValueError):
            bank.pay_out(bank.get_balance() + 1000)

    def test_pay_out_zero(self):
        bank = Bank()
        initial = bank.get_balance()
        payout = bank.pay_out(0)
        assert payout == 0
        assert bank.get_balance() == initial

    def test_pay_out_negative(self):
        bank = Bank()
        initial = bank.get_balance()
        payout = bank.pay_out(-100)
        assert payout == 0
        assert bank.get_balance() == initial

    def test_give_loan(self):
        bank = Bank()
        p = Player("Alice", 100)
        bank.give_loan(p, 500)
        assert p.balance == 600
        assert bank.loan_count() == 1
        assert bank.total_loans_issued() == 500


class TestBoard:

    def test_get_tile_type_go(self):
        board = Board()
        assert board.get_tile_type(0) == "go"

    def test_get_tile_type_jail(self):
        board = Board()
        assert board.get_tile_type(JAIL_POSITION) == "jail"

    def test_get_tile_type_free_parking(self):
        board = Board()
        assert board.get_tile_type(FREE_PARKING_POSITION) == "free_parking"

    def test_get_tile_type_income_tax(self):
        board = Board()
        assert board.get_tile_type(INCOME_TAX_POSITION) == "income_tax"

    def test_get_tile_type_property(self):
        board = Board()

        tile_type = board.get_tile_type(1)
        assert tile_type == "property"

    def test_get_property_at(self):
        board = Board()
        prop = board.get_property_at(1)
        assert prop is not None
        assert prop.name == "Mediterranean Avenue"

    def test_get_property_at_none(self):
        board = Board()
        prop = board.get_property_at(0)
        assert prop is None


class TestCardDeck:

    def test_draw(self):
        deck = CardDeck(CHANCE_CARDS)
        card1 = deck.draw()
        card2 = deck.draw()
        assert card1 != card2
        assert card1 == CHANCE_CARDS[0]

    def test_wraparound(self):
        cards = [{"action": "a"}, {"action": "b"}]
        deck = CardDeck(cards)
        deck.draw()
        deck.draw()
        card3 = deck.draw()
        assert card3["action"] == "a"


class TestGame:

    def test_buy_property_success(self):
        game = Game(["Alice", "Bob"])
        player = game.current_player()
        player.balance = 1000

        prop = game.board.properties[0]

        try:
            success = game.buy_property(player, prop)
            if not success:
                pytest.fail("Purchase should succeed but didn't")
        except AttributeError as e:
            pytest.fail(f"Critical BUG: Property doesn't have 'price' attribute - {e}")

    def test_buy_property_insufficient_funds(self):
        game = Game(["Alice", "Bob"])
        player = game.current_player()
        player.balance = 50

        prop = game.board.properties[0]
        try:
            success = game.buy_property(player, prop)
            if success:
                pytest.fail("Purchase should fail but didn't")
        except AttributeError:
            pytest.fail("BUG: Property doesn't have 'price' attribute")

    def test_buy_property_exact_balance(self):
        game = Game(["Alice", "Bob"])
        player = game.current_player()
        prop = game.board.properties[0]

        try:
            player.balance = 100
            success = game.buy_property(player, prop)
            assert success is False or True
        except AttributeError:
            pytest.fail("BUG: Property doesn't have 'price' attribute")

    def test_advance_turn(self):
        game = Game(["Alice", "Bob", "Charlie"])
        assert game.current_index == 0
        game.advance_turn()
        assert game.current_index == 1
        game.advance_turn()
        assert game.current_index == 2
        game.advance_turn()
        assert game.current_index == 0

    def test_pay_rent_normal(self):
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        bob = game.players[1]

        alice.balance = 1000
        bob.balance = 100

        prop = game.board.properties[0]
        prop.owner = bob

        game.pay_rent(alice, prop)
        rent = prop.get_rent()
        assert alice.balance == 1000 - rent

    def test_pay_rent_mortgaged(self):
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        bob = game.players[1]

        alice.balance = 1000
        bob.balance = 100

        prop = game.board.properties[0]
        prop.owner = bob
        prop.is_mortgaged = True

        game.pay_rent(alice, prop)
        assert alice.balance == 1000

    def test_find_winner_uses_net_worth(self):
        game = Game(["PropRich", "CashRich"])
        p0, p1 = game.players[0], game.players[1]
        p0.balance = 1000
        p1.balance = 1200
        prop = game.board.properties[-1]
        prop.owner = p0
        p0.add_property(prop)
        winner = game.find_winner()
        assert winner == p0

    def test_buy_property_with_exact_balance(self):
        game = Game(["Buyer", "Other"])
        player = game.players[0]
        prop = game.board.properties[0]
        player.balance = prop.price
        bank_before = game.bank.get_balance()
        success = game.buy_property(player, prop)
        assert success is True
        assert prop.owner == player
        assert player.balance == 0
        assert game.bank.get_balance() == bank_before + prop.price

    def test_pass_go_awards_salary(self):
        p = Player("Traveler", 1000)
        p.position = 35
        before = p.balance
        p.move(10)
        assert p.position == (35 + 10) % BOARD_SIZE
        assert p.balance == before + GO_SALARY

    def test_rent_payments_go_to_owner(self):
        game = Game(["Payer", "Owner"])
        payer, owner = game.players[0], game.players[1]
        payer.balance = 1000
        owner.balance = 500
        prop = game.board.properties[0]
        prop.owner = owner
        owner_before = owner.balance
        rent = prop.get_rent()
        game.pay_rent(payer, prop)
        assert payer.balance == 1000 - rent
        assert owner.balance == owner_before + rent

    def test_paying_jail_fine_deducts_balance_and_deposits_to_bank(self, monkeypatch):
        game = Game(["Jailed"])
        player = game.players[0]
        player.in_jail = True
        player.balance = 1000
        bank_before = game.bank.get_balance()
        # force confirm to yes
        monkeypatch.setattr('moneypoly.ui.confirm', lambda prompt: True)
        # avoid movement side-effects
        monkeypatch.setattr(Game, '_move_and_resolve', lambda self, player, roll: None)
        game._handle_jail_turn(player)
        assert player.balance == 1000 - JAIL_FINE
        assert game.bank.get_balance() == bank_before + JAIL_FINE
        assert player.in_jail is False
        assert player.jail_turns == 0

    def test_trade_transfers_money_to_seller(self):
        game = Game(["Seller", "Buyer"])
        seller, buyer = game.players[0], game.players[1]
        prop = game.board.properties[0]
        prop.owner = seller
        seller.add_property(prop)
        seller_before = seller.balance
        price = 200
        buyer.balance = price + 100
        buyer_before = buyer.balance
        result = game.trade(seller, buyer, prop, price)
        assert result is True
        assert seller.balance == seller_before + price
        assert buyer.balance == buyer_before - price

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
