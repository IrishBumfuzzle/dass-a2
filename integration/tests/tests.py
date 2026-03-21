import sys

sys.path.insert(
    0, "/home/irishbumfuzzle/Assignments/DASS/assignment-2/"
)

import pytest
from integration.code import (
    Registration,
    CrewManager,
    Inventory,
    RaceManager,
    Result,
    MissionPlanner,
    ChopShop,
    HeatNotoriety
)


class TestCase1_Valid:
    def test_valid_registration_to_race(self):

        reg = Registration()
        crew = CrewManager(registration=reg)
        inventory = Inventory(cash=50000)
        races = RaceManager(crew_manager=crew, inventory=inventory)

        reg.register("Dom")
        assert reg.is_registered("Dom"), "Driver should be registered"
        assert "Dom" in reg.view(), "Driver should appear in roster"

        crew.assign_role("Dom", "Driver")
        assert crew.has_role("Dom", "Driver"), "Driver role should be assigned"

        inventory.add_car("Skyline", tier=4, status="Pristine")
        assert inventory.is_car_available("Skyline"), "Car should be available"

        race_id = races.create_event("Street Battle", "Downtown", "Hard", required_car_tier=3)
        assert races.get_race_info(race_id) is not None, "Race should be created"

        races.assign_lineup(race_id, "Dom", "Skyline")
        race_info = races.get_race_info(race_id)

        assert race_info["driver"] == "Dom", "Driver should be assigned to race"
        assert race_info["car"] == "Skyline", "Car should be assigned to race"
        assert race_info["status"] == "Ready", "Race should be Ready status"
        assert races.is_race_ready(race_id), "Race should be ready to execute"
    
    def test_race_requires_both_driver_and_car(self):
        reg = Registration()
        crew = CrewManager(registration=reg)
        inventory = Inventory(cash=50000)
        races = RaceManager(crew_manager=crew, inventory=inventory)

        reg.register("Dom")
        crew.assign_role("Dom", "Driver")

        race_id = races.create_event("Test", "Location", "Easy", required_car_tier=1)

        with pytest.raises(ValueError, match="not found"):
            races.assign_lineup(race_id, "Dom", "MissingCar")

        inventory.add_car("ValidCar", tier=5, status="Pristine")
        races.assign_lineup(race_id, "Dom", "ValidCar")
        assert races.is_race_ready(race_id), "Race should be ready"


class TestCase2_MissingPrerequisite:
    
    def test_race_fails_without_registered_driver(self):
        reg = Registration()
        crew = CrewManager(registration=reg)
        inventory = Inventory(cash=50000)
        inventory.add_car("Car1", tier=4, status="Pristine")
        races = RaceManager(crew_manager=crew, inventory=inventory)

        race_id = races.create_event("Test Race", "Location", "Easy", required_car_tier=1)

        with pytest.raises(ValueError, match="does not have the Driver role"):
            races.assign_lineup(race_id, "NonExistentDriver", "Car1")
    
    def test_race_fails_without_driver_role(self):
        reg = Registration()
        reg.register("Sam")
        crew = CrewManager(registration=reg)
        inventory = Inventory(cash=50000)
        inventory.add_car("Car1", tier=4, status="Pristine")
        races = RaceManager(crew_manager=crew, inventory=inventory)

        race_id = races.create_event("Test Race", "Location", "Easy", required_car_tier=1)

        with pytest.raises(ValueError, match="does not have the Driver role"):
            races.assign_lineup(race_id, "Sam", "Car1")
    
    def test_available_drivers_list(self):
        reg = Registration()
        reg.register("Dom")
        reg.register("Brian")
        reg.register("Tej")
        
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        crew.assign_role("Brian", "Driver")
        crew.assign_role("Tej", "Mechanic")

        drivers = crew.get_members_by_role("Driver")
        assert len(drivers) == 2, "Should have 2 drivers"
        assert "Dom" in drivers, "Dom should be a driver"
        assert "Brian" in drivers, "Brian should be a driver"
        assert "Tej" not in drivers, "Tej should not be listed as driver"


class TestCase3_PayoutIntegration:
    
    def test_payout_adds_to_existing_balance(self):

        inventory = Inventory(cash=2000)
        results = Result(inventory=inventory)
        
        assert inventory.get_cash_balance() == 2000, "Should start with $2000"

        result_id = results.record_outcome(
            race_id=1,
            driver_name="Dom",
            car_name="Skyline",
            finishing_position="Win",
            prize_money=5000
        )

        results.process_payout(result_id)

        final_balance = inventory.get_cash_balance()
        assert final_balance == 7000, f"Balance should be $7000, got ${final_balance}"
    
    def test_multiple_payouts_accumulate(self):
        inventory = Inventory(cash=10000)
        results = Result(inventory=inventory)

        result1 = results.record_outcome(1, "Dom", "Car1", "Win", 3000)
        results.process_payout(result1)
        assert inventory.get_cash_balance() == 13000, "After first payout"

        result2 = results.record_outcome(2, "Dom", "Car1", "2nd", 1500)
        results.process_payout(result2)
        assert inventory.get_cash_balance() == 14500, "After second payout"

        result3 = results.record_outcome(3, "Brian", "Car2", "Loss", 0)
        results.process_payout(result3)
        assert inventory.get_cash_balance() == 14500, "After loss (no payout)"
    
    def test_payout_can_only_process_once(self):
        inventory = Inventory(cash=1000)
        results = Result(inventory=inventory)
        
        result_id = results.record_outcome(1, "Dom", "Car", "Win", 500)

        results.process_payout(result_id)
        assert inventory.get_cash_balance() == 1500

        with pytest.raises(ValueError, match="already processed"):
            results.process_payout(result_id)

        assert inventory.get_cash_balance() == 1500


class TestCase4_MissionRoleValidation:
    
    def test_mission_rejects_wrong_role(self):
        reg = Registration()
        reg.register("Tej")
        crew = CrewManager(registration=reg)
        missions = MissionPlanner(crew_manager=crew)

        crew.assign_role("Tej", "Strategist")

        mission_id = missions.create_mission(
            "Engine Rebuild",
            "Repair",
            required_roles={"Mechanic": 1},
            reward=1000
        )

        with pytest.raises(ValueError, match="does not have the Mechanic role"):
            missions.assign_crew(mission_id, {"Mechanic": ["Tej"]})
    
    def test_mission_accepts_correct_role(self):
        reg = Registration()
        reg.register("Tej")
        crew = CrewManager(registration=reg)
        missions = MissionPlanner(crew_manager=crew)

        crew.assign_role("Tej", "Mechanic")

        mission_id = missions.create_mission(
            "Engine Rebuild",
            "Repair",
            required_roles={"Mechanic": 1},
            reward=1000
        )

        missions.assign_crew(mission_id, {"Mechanic": ["Tej"]})

        mission_info = missions.get_mission_info(mission_id)
        assert mission_info["assigned_crew"]["Mechanic"] == ["Tej"]
    
    def test_mission_validates_multiple_roles(self):
        reg = Registration()
        reg.register("Dom")
        reg.register("Tej")
        reg.register("Roman")
        
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        crew.assign_role("Tej", "Mechanic")
        crew.assign_role("Roman", "Strategist")
        
        missions = MissionPlanner(crew_manager=crew)

        mission_id = missions.create_mission(
            "Repo Job",
            "Robbery",
            required_roles={"Driver": 1, "Mechanic": 1, "Strategist": 1},
            reward=5000
        )

        missions.assign_crew(
            mission_id,
            {
                "Driver": ["Dom"],
                "Mechanic": ["Tej"],
                "Strategist": ["Roman"]
            }
        )

        assert missions.is_mission_fully_staffed(mission_id)
    
    def test_mission_rejects_incomplete_assignment(self):
        reg = Registration()
        reg.register("Dom")
        reg.register("Tej")
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        crew.assign_role("Tej", "Mechanic")
        
        missions = MissionPlanner(crew_manager=crew)

        mission_id = missions.create_mission(
            "Complex Job",
            "Transport",
            required_roles={"Driver": 1, "Mechanic": 1},
            reward=3000
        )

        with pytest.raises(ValueError, match="Missing assignment"):
            missions.assign_crew(mission_id, {"Driver": ["Dom"]})


class TestCase5_DominoEffect:
    
    def test_damage_workflow_complete_integration(self):

        reg = Registration()
        reg.register("Dom")
        reg.register("Tej")
        
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        crew.assign_role("Tej", "Mechanic")
        
        inventory = Inventory(cash=50000)
        inventory.add_car("Skyline", tier=5, status="Pristine")
        
        races = RaceManager(crew_manager=crew, inventory=inventory)
        results = Result(inventory=inventory)
        missions = MissionPlanner(crew_manager=crew, inventory=inventory)

        race_id = races.create_event("Battle", "Street", "Hard", required_car_tier=4)
        races.assign_lineup(race_id, "Dom", "Skyline")

        result_id = results.record_outcome(race_id, "Dom", "Skyline", "Win", 5000)
        results.process_payout(result_id)

        results.process_wear_and_tear(result_id, wear_chance=1.0)

        car_status = inventory.get_car_status("Skyline")
        assert car_status == "Damaged", f"Car should be Damaged, got {car_status}"

        mission_id = missions.create_mission(
            "Full Overhaul",
            "Repair",
            required_roles={"Mechanic": 1},
            reward=2000
        )

        missions.assign_crew(mission_id, {"Mechanic": ["Tej"]})

        missions.complete_mission(mission_id, success=True)

        car_status_after = inventory.get_car_status("Skyline")
        assert car_status_after == "Pristine", \
            f"Car should be Pristine after repair, got {car_status_after}"

        final_cash = inventory.get_cash_balance()
        assert final_cash == 57000, f"Cash should be $57000, got ${final_cash}"
    
    def test_damaged_car_prevents_racing(self):
        reg = Registration()
        reg.register("Dom")
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        
        inventory = Inventory(cash=50000)
        inventory.add_car("Car1", tier=3, status="Pristine")
        
        races = RaceManager(crew_manager=crew, inventory=inventory)

        race1 = races.create_event("Race1", "Loc", "Easy", 1)
        races.assign_lineup(race1, "Dom", "Car1")
        assert races.is_race_ready(race1)

        inventory.update_car_status("Car1", "Damaged")

        race2 = races.create_event("Race2", "Loc", "Easy", 1)
        with pytest.raises(ValueError, match="Damaged"):
            races.assign_lineup(race2, "Dom", "Car1")
    
    def test_repair_mission_fixes_all_damaged_cars(self):
        inventory = Inventory(cash=50000)
        inventory.add_car("Car1", tier=3, status="Damaged")
        inventory.add_car("Car2", tier=4, status="Damaged")
        inventory.add_car("Car3", tier=2, status="Pristine")
        
        reg = Registration()
        reg.register("Tej")
        crew = CrewManager(registration=reg)
        crew.assign_role("Tej", "Mechanic")
        
        missions = MissionPlanner(crew_manager=crew, inventory=inventory)

        assert inventory.get_car_status("Car1") == "Damaged"
        assert inventory.get_car_status("Car2") == "Damaged"
        assert inventory.get_car_status("Car3") == "Pristine"

        mission_id = missions.create_mission(
            "Full Fleet Maintenance",
            "Repair",
            required_roles={"Mechanic": 1},
            reward=1000
        )
        missions.assign_crew(mission_id, {"Mechanic": ["Tej"]})
        missions.complete_mission(mission_id, success=True)

        assert inventory.get_car_status("Car1") == "Pristine"
        assert inventory.get_car_status("Car2") == "Pristine"
        assert inventory.get_car_status("Car3") == "Pristine"
    
    def test_failed_mission_does_not_repair_cars(self):
        inventory = Inventory(cash=50000)
        inventory.add_car("DamagedCar", tier=3, status="Damaged")
        
        reg = Registration()
        reg.register("Tej")
        crew = CrewManager(registration=reg)
        crew.assign_role("Tej", "Mechanic")
        
        missions = MissionPlanner(crew_manager=crew, inventory=inventory)

        mission_id = missions.create_mission(
            "Repair Job",
            "Repair",
            required_roles={"Mechanic": 1},
            reward=1000
        )
        missions.assign_crew(mission_id, {"Mechanic": ["Tej"]})

        missions.complete_mission(mission_id, success=False)

        assert inventory.get_car_status("DamagedCar") == "Damaged", \
            "Failed mission should not repair cars"


class TestCase6_ChopShopIntegration:
    
    def test_buy_car_from_shop(self):
        inventory = Inventory(cash=20000)
        shop = ChopShop(inventory=inventory)
        
        initial_balance = inventory.get_cash_balance()
        transaction_id = shop.buy_car("Sedan", quantity=1)
        
        assert transaction_id is not None, "Transaction should be recorded"
        assert inventory.get_cash_balance() == initial_balance - 10000, \
            "Cash should be deducted for car purchase"
        
        available_cars = inventory.get_available_cars()
        assert len(available_cars) == 1, "Should have 1 car"
    
    def test_buy_multiple_cars(self):
        inventory = Inventory(cash=50000)
        shop = ChopShop(inventory=inventory)
        
        transaction_id = shop.buy_car("Sports", quantity=2)
        
        available_cars = inventory.get_available_cars()
        assert len(available_cars) == 2, "Should have 2 sports cars"
        
        final_balance = inventory.get_cash_balance()
        expected_cost = 20000 * 2
        assert final_balance == 50000 - expected_cost, "Cash deducted correctly"
    
    def test_buy_car_insufficient_funds(self):
        inventory = Inventory(cash=5000)
        shop = ChopShop(inventory=inventory)
        
        with pytest.raises(ValueError, match="Insufficient funds"):
            shop.buy_car("Sedan", quantity=1)
    
    def test_buy_invalid_car_type(self):
        inventory = Inventory(cash=50000)
        shop = ChopShop(inventory=inventory)
        
        with pytest.raises(ValueError, match="not available"):
            shop.buy_car("NonExistent", quantity=1)
    
    def test_sell_car_to_shop(self):
        inventory = Inventory(cash=10000)
        inventory.add_car("TestCar", tier=2, status="Pristine")
        shop = ChopShop(inventory=inventory)
        
        initial_balance = inventory.get_cash_balance()
        transaction_id = shop.sell_car("TestCar", resale_percentage=0.5)
        
        assert transaction_id is not None, "Transaction should be recorded"
        assert "TestCar" not in inventory.view_garage(), "Car should be removed"

        assert inventory.get_cash_balance() == initial_balance + 5000, \
            "Cash should be added from car sale"
    
    def test_sell_nonexistent_car(self):
        inventory = Inventory(cash=10000)
        shop = ChopShop(inventory=inventory)
        
        with pytest.raises(ValueError, match="not found"):
            shop.sell_car("NonExistent")
    
    def test_buy_parts_from_shop(self):
        inventory = Inventory(cash=30000)
        shop = ChopShop(inventory=inventory)
        
        initial_balance = inventory.get_cash_balance()
        transaction_id = shop.buy_part("Turbo Boost", quantity=1)
        
        assert transaction_id is not None, "Transaction should be recorded"
        assert inventory.get_cash_balance() == initial_balance - 3000, \
            "Cash should be deducted for part"
        
        equipment = inventory.view_equipment()
        assert len(equipment) > 0, "Should have equipment"
    
    def test_buy_multiple_parts(self):
        inventory = Inventory(cash=50000)
        shop = ChopShop(inventory=inventory)
        
        transaction_id = shop.buy_part("Custom Engine", quantity=2)
        
        equipment = inventory.view_equipment()
        assert len(equipment) == 2, "Should have 2 engines"
        
        final_balance = inventory.get_cash_balance()
        expected_cost = 8000 * 2
        assert final_balance == 50000 - expected_cost, "Cost calculated correctly"
    
    def test_buy_part_insufficient_funds(self):
        inventory = Inventory(cash=2000)
        shop = ChopShop(inventory=inventory)
        
        with pytest.raises(ValueError, match="Insufficient funds"):
            shop.buy_part("Turbo Boost", quantity=1)
    
    def test_sell_part_to_shop(self):
        inventory = Inventory(cash=5000)
        shop = ChopShop(inventory=inventory)

        shop.buy_part("Racing Suspension", quantity=1)
        equipment_list = inventory.view_equipment()
        part_name = equipment_list[0]
        
        initial_balance = inventory.get_cash_balance()
        transaction_id = shop.sell_part(part_name, resale_percentage=0.3)

        assert inventory.get_cash_balance() == initial_balance + 750, \
            "Cash should be added from part sale"
        
        assert part_name not in inventory.view_equipment(), \
            "Part should be removed from equipment"
    
    def test_shop_integrates_with_race_car_purchase(self):
        reg = Registration()
        reg.register("Dom")
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        
        inventory = Inventory(cash=40000)
        shop = ChopShop(inventory=inventory)
        races = RaceManager(crew_manager=crew, inventory=inventory)
        results = Result(inventory=inventory)

        shop.buy_car("Supercar", quantity=1)
        cars = inventory.get_available_cars()
        car_name = cars[0]

        race_id = races.create_event("Challenge", "Street", "Extreme", required_car_tier=4)
        races.assign_lineup(race_id, "Dom", car_name)

        result_id = results.record_outcome(race_id, "Dom", car_name, "Win", 5000)
        results.process_payout(result_id)
        results.process_wear_and_tear(result_id, wear_chance=1.0)

        shop.sell_car(car_name, resale_percentage=0.3)

        final_balance = inventory.get_cash_balance()

        expected = 40000 - 40000 + 5000 + int(40000 * 0.3)
        assert final_balance == expected, f"Balance should be {expected}, got {final_balance}"


class TestCase7_HeatAndNotorietyIntegration:
    
    def test_add_heat_from_race_win(self):
        inventory = Inventory(cash=50000)
        heat = HeatNotoriety()
        
        initial_heat = heat.get_heat_level()
        event_id, new_heat = heat.add_heat(25, source="Won Hard race")
        
        assert event_id is not None, "Event should be recorded"
        assert new_heat == 25, "Heat should increase"
        assert new_heat > initial_heat, "Heat level should increase"
    
    def test_heat_does_not_exceed_maximum(self):
        heat = HeatNotoriety()
        
        event1, heat1 = heat.add_heat(80, source="Major race")
        assert heat1 == 80, "Heat should be 80"
        
        event2, heat2 = heat.add_heat(40, source="Another race")
        assert heat2 == 100, "Heat should cap at 100"
    
    def test_reduce_heat(self):
        heat = HeatNotoriety()
        heat.add_heat(50, source="Initial")
        
        event_id, new_heat = heat.reduce_heat(20, method="Evaded patrol")
        
        assert event_id is not None, "Event should be recorded"
        assert new_heat == 30, "Heat should decrease to 30"
    
    def test_reduce_heat_exceeds_current(self):
        heat = HeatNotoriety()
        heat.add_heat(10, source="Initial")
        
        with pytest.raises(ValueError, match="Cannot reduce heat"):
            heat.reduce_heat(20, method="Too much")
    
    def test_heat_status_levels(self):
        heat = HeatNotoriety()
        
        assert heat.get_heat_status() == "Low", "0-29 should be Low"
        
        heat.add_heat(30, source="Test")
        assert heat.get_heat_status() == "Medium", "30-59 should be Medium"
        
        heat.add_heat(30, source="Test")
        assert heat.get_heat_status() == "High", "60-84 should be High"
        
        heat.add_heat(25, source="Test")
        assert heat.get_heat_status() == "Critical", "85+ should be Critical"
    
    def test_race_blocked_at_critical_heat(self):
        heat = HeatNotoriety()
        
        assert not heat.is_race_blocked("Extreme"), "Should not block at low heat"
        
        heat.add_heat(85, source="Critical")
        assert heat.is_race_blocked("Easy"), "All races blocked at critical"
        assert heat.is_race_blocked("Medium"), "All races blocked at critical"
        assert heat.is_race_blocked("Extreme"), "All races blocked at critical"
    
    def test_race_blocked_at_high_heat(self):
        heat = HeatNotoriety()
        heat.add_heat(65, source="High heat")
        
        assert not heat.is_race_blocked("Easy"), "Easy races allowed at high heat"
        assert heat.is_race_blocked("Medium"), "Medium blocked at high heat"
        assert heat.is_race_blocked("Hard"), "Hard blocked at high heat"
        assert heat.is_race_blocked("Extreme"), "Extreme blocked at high heat"
    
    def test_race_blocked_at_medium_heat(self):
        heat = HeatNotoriety()
        heat.add_heat(35, source="Medium heat")
        
        assert not heat.is_race_blocked("Easy"), "Easy allowed at medium heat"
        assert not heat.is_race_blocked("Medium"), "Medium allowed at medium heat"
        assert heat.is_race_blocked("Hard"), "Hard blocked at medium heat"
        assert heat.is_race_blocked("Extreme"), "Extreme blocked at medium heat"
    
    def test_heat_multiplication_factor(self):
        heat = HeatNotoriety()

        factor = heat.get_race_multiplication_factor("Easy")
        assert factor == 1.0, "At low heat, Easy multiplier should be 1.0"

        heat.add_heat(35, source="Test")
        factor = heat.get_race_multiplication_factor("Extreme")
        assert factor == 3.0 * 1.5, "At medium heat, Extreme multiplier should be 4.5"

        heat.add_heat(30, source="Test")
        factor = heat.get_race_multiplication_factor("Hard")
        assert factor == 2.0 * 2.0, "At high heat, Hard multiplier should be 4.0"
    
    def test_process_race_win_adds_heat(self):
        heat = HeatNotoriety()
        
        event_id, heat_added, new_heat = heat.process_race_heat("Hard", won=True)
        
        assert event_id is not None, "Event should be recorded"
        assert heat_added == 40, f"Hard race should add 40 (20 base * 2.0 multiplier), got {heat_added}"
        assert new_heat == 40, f"Heat should be 40, got {new_heat}"
    
    def test_process_race_loss_no_heat(self):
        heat = HeatNotoriety()
        
        event_id, heat_added, new_heat = heat.process_race_heat("Hard", won=False)
        
        assert event_id is None, "No event for loss"
        assert heat_added == 0, "Losing should not add heat"
        assert new_heat == 0, "Heat should remain 0"
    
    def test_generate_evasion_mission_requires_critical_heat(self):
        mission_planner = MissionPlanner()
        heat = HeatNotoriety(mission_planner=mission_planner)

        heat.add_heat(50, source="Test")
        with pytest.raises(ValueError, match="critical heat"):
            heat.generate_evasion_mission()

        heat.add_heat(40, source="Test")
        mission_id = heat.generate_evasion_mission()
        assert mission_id is not None, "Mission should be created"
        
        mission_info = mission_planner.get_mission_info(mission_id)
        assert mission_info["name"] == "URGENT: Evade the Cops"
        assert "Driver" in mission_info["required_roles"]
        assert "Strategist" in mission_info["required_roles"]
    
    def test_reset_heat_to_zero(self):
        heat = HeatNotoriety()
        heat.add_heat(75, source="Test")
        
        assert heat.get_heat_level() == 75, "Heat should be 75"
        
        event_id = heat.reset_heat()
        
        assert event_id is not None, "Reset should be recorded"
        assert heat.get_heat_level() == 0, "Heat should be reset to 0"
    
    def test_heat_blocks_race_assignment(self):
        reg = Registration()
        reg.register("Dom")
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        
        inventory = Inventory(cash=50000)
        inventory.add_car("Car", tier=5, status="Pristine")
        
        races = RaceManager(crew_manager=crew, inventory=inventory)
        heat = HeatNotoriety()

        race_id = races.create_event("Extreme Race", "Downtown", "Extreme", required_car_tier=5)

        assert not heat.is_race_blocked("Extreme"), "Low heat should not block race"
        races.assign_lineup(race_id, "Dom", "Car")
        assert races.is_race_ready(race_id), "Race should be ready"

        heat.add_heat(75, source="Multiple wins")
        assert heat.is_race_blocked("Extreme"), "High heat should block Extreme race"
    
    def test_complete_heat_workflow(self):
        reg = Registration()
        reg.register("Dom")
        reg.register("Roman")
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        crew.assign_role("Roman", "Strategist")
        
        inventory = Inventory(cash=100000)
        inventory.add_car("Car1", tier=4, status="Pristine")
        inventory.add_car("Car2", tier=5, status="Pristine")
        
        races = RaceManager(crew_manager=crew, inventory=inventory)
        results = Result(inventory=inventory)
        missions = MissionPlanner(crew_manager=crew)
        heat = HeatNotoriety(mission_planner=missions)

        race1 = races.create_event("Race1", "Loc", "Hard", 3)
        races.assign_lineup(race1, "Dom", "Car1")
        result1 = results.record_outcome(race1, "Dom", "Car1", "Win", 3000)
        results.process_payout(result1)
        heat.process_race_heat("Hard", won=True)
        
        race2 = races.create_event("Race2", "Loc", "Extreme", 4)
        races.assign_lineup(race2, "Dom", "Car2")
        result2 = results.record_outcome(race2, "Dom", "Car2", "Win", 5000)
        results.process_payout(result2)
        heat.process_race_heat("Extreme", won=True)

        current_heat = heat.get_heat_level()
        assert current_heat > 0, f"Heat should increase, got {current_heat}"

        heat.add_heat(50, source="Dangerous activities")
        
        assert heat.get_heat_status() == "Critical", "Heat should be critical"

        mission_id = heat.generate_evasion_mission()
        missions.assign_crew(mission_id, {"Driver": ["Dom"], "Strategist": ["Roman"]})
        
        mission_info = missions.get_mission_info(mission_id)
        assert mission_info["status"] == "Assigned"


class TestCase8_ChopShopAndHeatIntegration:
    
    def test_buy_car_upgrade_to_do_dangerous_race(self):
        inventory = Inventory(cash=80000)
        shop = ChopShop(inventory=inventory)
        
        reg = Registration()
        reg.register("Dom")
        crew = CrewManager(registration=reg)
        crew.assign_role("Dom", "Driver")
        
        races = RaceManager(crew_manager=crew, inventory=inventory)
        results = Result(inventory=inventory)
        heat = HeatNotoriety()

        shop.buy_car("Hypercar", quantity=1)
        cars = inventory.get_available_cars()
        car = cars[0]

        assert inventory.get_cash_balance() == 5000, "Cash reduced after purchase"

        race_id = races.create_event("Extreme", "Downtown", "Extreme", 5)
        races.assign_lineup(race_id, "Dom", car)
        
        result_id = results.record_outcome(race_id, "Dom", car, "Win", 10000)
        results.process_payout(result_id)
        
        heat.process_race_heat("Extreme", won=True)

        assert inventory.get_cash_balance() == 15000, "Cash updated with payout"
        assert heat.get_heat_level() > 0, "Heat should increase from extreme race"
    
    def test_heat_forces_shop_activity_to_reduce_heat(self):
        inventory = Inventory(cash=50000)
        shop = ChopShop(inventory=inventory)
        heat = HeatNotoriety()

        heat.add_heat(70, source="High profile races")


        inventory.add_car("Supercar", tier=4, status="Pristine")

        shop.sell_car("Supercar", resale_percentage=0.5)

        heat.reduce_heat(30, method="Laying low")
        
        assert heat.get_heat_level() == 40, "Heat should decrease"
        assert heat.get_heat_status() == "Medium", "Should be at medium heat now"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
