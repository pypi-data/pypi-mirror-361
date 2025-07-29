#!/usr/bin/env python3
"""
Restorant - Terminal Restaurant Roguelike
A text-based restaurant management game with live events and burnout management.
"""

import os
import time
import random
import json
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Game state classes
@dataclass
class Staff:
    name: str
    role: str  # 'chef', 'server', 'manager'
    level: int
    stress: int  # 0-100
    skills: List[str]
    salary: int
    traits: List[str]
    skill_level: int = 1  # New: chef skill level (1-10)
    xp: int = 0           # New: experience points

@dataclass
class Equipment:
    name: str
    condition: int  # 0-100
    last_maintenance: int  # days ago

@dataclass
class Inventory:
    item: str
    quantity: int
    cost: float

@dataclass
class Recipe:
    name: str
    ingredients: List[str]
    difficulty: int  # 1-5
    price: int
    category: str  # 'italian', 'grilling', 'sushi', etc.

@dataclass
class Venue:
    venue_id: str
    name: str
    category: str
    size: str
    staff_capacity: int
    customer_capacity: int
    price_range: str
    purchase_cost: int
    rent_cost: int
    is_owned: bool = False
    description: str = ""

@dataclass
class Loan:
    loan_id: str
    name: str
    amount: int
    interest_rate: float
    term_months: int
    monthly_payment: int
    remaining_balance: int
    days_remaining: int
    collateral: str
    is_active: bool = True

@dataclass
class GameState:
    day: int
    money: int
    rating: int
    owner_burnout: int  # 0-100
    staff: List[Staff]
    equipment: List[Equipment]
    inventory: List[Inventory]
    recipes: List[Recipe]
    unlocked_recipes: List[str]
    activity_counts: Dict[str, int]  # Track habit formation
    current_time: str
    is_service_hours: bool
    customers_present: int
    current_venue: Venue = None
    available_venues: List[Venue] = None
    loans: List[Loan] = None
    credit_score: int = 650
    monthly_revenue: int = 0
    venue_purchase_date: int = 0  # Day when venue was purchased

class RestorantGame:
    def __init__(self):
        self.state = GameState(
            day=1,
            money=5000,
            rating=500,
            owner_burnout=0,
            staff=[],
            equipment=[],
            inventory=[],
            recipes=[],
            unlocked_recipes=[],
            activity_counts={},
            current_time="09:00",
            is_service_hours=False,
            customers_present=0
        )
        self.recipes_data = {}
        self.ingredients_data = {}
        self.events_data = {}
        self.activities_data = {}
        self.venues_data = {}
        self.loans_data = {}
        self.load_data_files()
        self.initialize_game()
    
    def load_data_files(self):
        """Load all YAML data files"""
        try:
            with open('data/recipes.yaml', 'r', encoding='utf-8') as f:
                self.recipes_data = yaml.safe_load(f)
            
            with open('data/ingredients.yaml', 'r', encoding='utf-8') as f:
                self.ingredients_data = yaml.safe_load(f)
            
            with open('data/events.yaml', 'r', encoding='utf-8') as f:
                self.events_data = yaml.safe_load(f)
            
            with open('data/activities.yaml', 'r', encoding='utf-8') as f:
                self.activities_data = yaml.safe_load(f)
            
            with open('data/venues.yaml', 'r', encoding='utf-8') as f:
                self.venues_data = yaml.safe_load(f)
            
            with open('data/loans.yaml', 'r', encoding='utf-8') as f:
                self.loans_data = yaml.safe_load(f)
        except FileNotFoundError as e:
            print(f"Warning: Could not load data file: {e}")
            # Create default data if files don't exist
            self.create_default_data()
    
    def create_default_data(self):
        """Create default data if YAML files are missing"""
        self.recipes_data = {"recipes": {}}
        self.ingredients_data = {"ingredients": {}}
        self.events_data = {"events": {}}
        self.activities_data = {"activities": {}}
        self.venues_data = {"venues": {}}
        self.loans_data = {"loans": {}}
    
    def initialize_game(self):
        """Initialize starting game state"""
        # Starting equipment
        self.state.equipment = [
            Equipment("Stove", 100, 0),
            Equipment("Fridge", 100, 0),
            Equipment("Dishwasher", 100, 0)
        ]
        
        # Starting inventory from YAML data
        self.state.inventory = []
        if self.ingredients_data.get("ingredients"):
            for ingredient_id, ingredient in list(self.ingredients_data["ingredients"].items())[:5]:
                self.state.inventory.append(
                    Inventory(ingredient["name"], 10, ingredient["base_cost"])
                )
        
        # Starting recipes from YAML data
        self.state.recipes = []
        self.state.unlocked_recipes = []
        if self.recipes_data.get("recipes"):
            for recipe_id, recipe in self.recipes_data["recipes"].items():
                recipe_obj = Recipe(
                    recipe["name"],
                    [ing["name"] for ing in recipe["ingredients"]],
                    recipe["difficulty"],
                    recipe["price"],
                    recipe["category"]
                )
                self.state.recipes.append(recipe_obj)
                # Unlock basic recipes
                if recipe["category"] == "basic":
                    self.state.unlocked_recipes.append(recipe["name"])
        
        # Initialize venues
        self.initialize_venues()
        
        # Starting staff (limited by venue capacity)
        self.state.staff = [
            Staff("Maria", "chef", 2, 20, ["italian"], 800, ["creative", "perfectionist"], 2, 0),
            Staff("Alex", "server", 1, 15, ["customer_service"], 600, ["friendly", "efficient"], 1, 0)
        ]
        
        # Initialize loans list
        self.state.loans = []
    
    def initialize_venues(self):
        """Initialize available venues"""
        self.state.available_venues = []
        if self.venues_data.get("venues"):
            for venue_id, venue_data in self.venues_data["venues"].items():
                venue = Venue(
                    venue_id=venue_id,
                    name=venue_data["name"],
                    category=venue_data["category"],
                    size=venue_data["size"],
                    staff_capacity=venue_data["staff_capacity"],
                    customer_capacity=venue_data["customer_capacity"],
                    price_range=venue_data["price_range"],
                    purchase_cost=venue_data["purchase_cost"],
                    rent_cost=venue_data["rent_cost"],
                    description=venue_data["description"]
                )
                self.state.available_venues.append(venue)
        
        # Set starting venue (food truck)
        if self.state.available_venues:
            self.state.current_venue = next((v for v in self.state.available_venues if v.venue_id == "food_truck"), self.state.available_venues[0])
            self.state.current_venue.is_owned = True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the game header"""
        print("┌─────────────────────────────────────┐")
        print("│           🍽️ RESTORANT 🍽️           │")
        print("├─────────────────────────────────────┤")
    
    def print_footer(self):
        """Print the game footer"""
        print("└─────────────────────────────────────┘")
    
    def main_menu(self):
        """Display and handle main menu"""
        while True:
            self.clear_screen()
            self.print_header()
            print("│                                     │")
            print("│  [1] Start New Game                 │")
            print("│  [2] Load Game                      │")
            print("│  [3] View Achievements              │")
            print("│  [4] Settings                       │")
            print("│  [5] Exit                           │")
            print("│                                     │")
            self.print_footer()
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.start_new_game()
            elif choice == "2":
                self.load_game()
            elif choice == "3":
                self.view_achievements()
            elif choice == "4":
                self.settings()
            elif choice == "5":
                print("\nThanks for playing Restorant! 👨‍🍳")
                break
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
    
    def start_new_game(self):
        """Start a new game"""
        self.__init__()  # Reset game state
        self.game_loop()
    
    def load_game(self):
        """Load a saved game"""
        try:
            with open('savegame.json', 'r') as f:
                data = json.load(f)
                # Reconstruct game state from saved data
                print("Game loaded successfully!")
                time.sleep(1)
                self.game_loop()
        except FileNotFoundError:
            print("No saved game found.")
            time.sleep(1)
    
    def view_achievements(self):
        """View achievements screen"""
        self.clear_screen()
        self.print_header()
        print("│           ACHIEVEMENTS               │")
        print("├─────────────────────────────────────┤")
        print("│                                     │")
        print("│  🏆 Coming Soon!                    │")
        print("│                                     │")
        self.print_footer()
        input("\nPress Enter to continue...")
    
    def settings(self):
        """Settings menu"""
        self.clear_screen()
        self.print_header()
        print("│             SETTINGS                 │")
        print("├─────────────────────────────────────┤")
        print("│                                     │")
        print("│  ⚙️  Coming Soon!                    │")
        print("│                                     │")
        self.print_footer()
        input("\nPress Enter to continue...")
    
    def game_loop(self):
        """Main game loop"""
        while True:
            self.clear_screen()
            self.display_game_interface()
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self.start_service_hours()
            elif choice == "2":
                self.manage_staff()
            elif choice == "3":
                self.view_kitchen()
            elif choice == "4":
                self.check_menu()
            elif choice == "5":
                self.view_finances()
            elif choice == "6":
                self.after_hours_activities()
            elif choice == "7":
                self.manage_venue()
            elif choice == "8":
                self.apply_for_loan()
            elif choice == "9":
                self.next_day()
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
    
    def display_game_interface(self):
        """Display the main game interface"""
        self.print_header()
        venue_info = f"{self.state.current_venue.name}" if self.state.current_venue else "No Venue"
        loan_info = f" | Loans: {len([l for l in self.state.loans if l.is_active])}" if self.state.loans else ""
        print(f"│ Day: {self.state.day} | Money: ${self.state.money:,} | Rating: {self.state.rating}│")
        print(f"│ Venue: {venue_info} | Staff: {len(self.state.staff)}/{self.state.current_venue.staff_capacity if self.state.current_venue else 0}{loan_info} │")
        print("├─────────────────────────────────────┤")
        print("│                                     │")
        print("│  [1] Start Service Hours            │")
        print("│  [2] Manage Staff                   │")
        print("│  [3] View Kitchen                   │")
        print("│  [4] Check Menu                     │")
        print("│  [5] View Finances                  │")
        print("│  [6] After Hours Activities         │")
        print("│  [7] Manage Venue                   │")
        print("│  [8] Apply for Loan                 │")
        print("│  [9] Next Day                       │")
        print("│                                     │")
        self.print_footer()
    
    def start_service_hours(self):
        """Start the live service hours simulation"""
        if self.state.is_service_hours:
            print("\nService hours are already running!")
            time.sleep(1)
            return
        
        self.state.is_service_hours = True
        self.state.current_time = "12:00"
        
        print("\n🚀 Starting Service Hours...")
        time.sleep(1)
        
        # Simulate service hours
        self.service_hours_simulation()
    
    def service_hours_simulation(self):
        """Simulate live service hours with events"""
        service_end_time = "22:00"
        
        while self.state.current_time < service_end_time and self.state.is_service_hours:
            self.clear_screen()
            self.display_service_interface()
            
            # Generate random events
            self.generate_service_events()
            
            # Update time
            current_dt = datetime.strptime(self.state.current_time, "%H:%M")
            current_dt += timedelta(minutes=5)
            self.state.current_time = current_dt.strftime("%H:%M")
            
            time.sleep(2)  # Simulate time passing
        
        self.state.is_service_hours = False
        print("\n🏁 Service hours ended!")
        time.sleep(1)
    
    def display_service_interface(self):
        """Display service hours interface"""
        self.print_header()
        print(f"│ Time: {self.state.current_time} | Customers: {self.state.customers_present} | Rating: {self.state.rating}│")
        print("├─────────────────────────────────────┤")
        print("│                                     │")
        print("│  [1] Pause Service                  │")
        print("│  [2] Speed Up Time                  │")
        print("│  [3] Emergency Stop                 │")
        print("│                                     │")
        self.print_footer()
        
        # Display live events
        print("\n┌─────────────────────────────────────┐")
        print("│           LIVE EVENTS               │")
        print("├─────────────────────────────────────┤")
        # Events will be displayed here
        print("└─────────────────────────────────────┘")
    
    def generate_service_events(self):
        """Generate random service events"""
        # Customer arrival (respect venue capacity)
        if random.random() < 0.3:  # 30% chance
            max_new_customers = self.state.current_venue.customer_capacity - self.state.customers_present
            if max_new_customers > 0:
                customers = random.randint(1, min(3, max_new_customers))
                self.state.customers_present += customers
                print(f"{self.state.current_time} - {customers} customer(s) arrive")
            elif self.state.customers_present >= self.state.current_venue.customer_capacity:
                print(f"{self.state.current_time} - Restaurant is full, customers wait outside")
        
        # Customer orders
        if self.state.customers_present > 0 and random.random() < 0.4:
            recipe_name = random.choice(self.state.unlocked_recipes)
            recipe = next((r for r in self.state.recipes if r.name == recipe_name), None)
            chef = self.get_best_chef_for_recipe(recipe)
            if self.check_ingredients(recipe_name):
                print(f"{self.state.current_time} - Order: {recipe_name}")
                # Calculate satisfaction
                satisfaction, xp_gain = self.calculate_satisfaction_and_xp(chef, recipe)
                # Apply XP and skill up
                chef.xp += xp_gain
                self.check_skill_up(chef)
                # Customer will be satisfied or not
                if satisfaction >= 1.0:
                    self.state.rating += 1
                    print(f"{self.state.current_time} - Customer satisfied (+1)")
                    # Chance for review
                    if random.random() < min(0.2 + (satisfaction-1)*0.1, 0.8):
                        self.state.rating += 5
                        print(f"{self.state.current_time} - Customer leaves review (+5)")
                else:
                    self.state.rating -= 1
                    print(f"{self.state.current_time} - Customer leaves dissatisfied (-1)")
                    # Chance for bad review
                    if random.random() < 0.2 + (1-satisfaction)*0.2:
                        self.state.rating -= 5
                        print(f"{self.state.current_time} - Customer leaves bad review (-5)")
            else:
                print(f"{self.state.current_time} - ⚠️  No ingredients for {recipe_name}!")
                self.state.rating -= 1
                print(f"{self.state.current_time} - Customer leaves dissatisfied (-1)")
            self.state.customers_present -= 1
        # Kitchen incidents
        if random.random() < 0.1:  # 10% chance
            print(f"{self.state.current_time} - ⚠️  Kitchen accident!")
            print("      [1] Send help immediately")
            print("      [2] Let staff handle it")
            # For now, auto-choose option 2
            print(f"{self.state.current_time} - Staff handled the incident")
    
    def get_best_chef_for_recipe(self, recipe):
        """Return the chef with the highest skill for the recipe's category"""
        chefs = [s for s in self.state.staff if s.role == 'chef']
        if not chefs:
            return Staff("Temp", "chef", 1, 0, [], 0, [], 1, 0)
        # Prefer chef with matching skill
        best = max(chefs, key=lambda c: (c.skill_level, c.level))
        return best

    def calculate_satisfaction_and_xp(self, chef, recipe):
        """Calculate satisfaction and XP gain based on chef skill and recipe difficulty"""
        skill = chef.skill_level
        difficulty = recipe.difficulty
        # Satisfaction: 1.0 = normal, >1 = bonus, <1 = penalty
        if skill >= difficulty + 2:
            satisfaction = 1.2
            xp_gain = 1
        elif skill >= difficulty:
            satisfaction = 1.0
            xp_gain = 2
        elif skill == difficulty - 1:
            satisfaction = 0.8
            xp_gain = 3
        else:
            satisfaction = 0.6
            xp_gain = 4
        # No XP for easy dishes if skill is much higher
        if skill > difficulty + 3:
            xp_gain = 0
        return satisfaction, xp_gain

    def check_skill_up(self, chef):
        """Increase chef skill level if enough XP"""
        xp_needed = 10 + chef.skill_level * 5
        while chef.xp >= xp_needed and chef.skill_level < 10:
            chef.xp -= xp_needed
            chef.skill_level += 1
            print(f"🎉 {chef.name} leveled up! Skill is now {chef.skill_level}")
            xp_needed = 10 + chef.skill_level * 5

    def check_ingredients(self, recipe_name: str) -> bool:
        """Check if ingredients are available for a recipe"""
        recipe = next((r for r in self.state.recipes if r.name == recipe_name), None)
        if not recipe:
            return False
        
        for ingredient in recipe.ingredients:
            inv_item = next((i for i in self.state.inventory if i.item == ingredient), None)
            if not inv_item or inv_item.quantity <= 0:
                return False
        return True
    
    def manage_staff(self):
        """Staff management screen"""
        while True:
            self.clear_screen()
            self.print_header()
            print("│           STAFF ROSTER              │")
            print("├─────────────────────────────────────┤")
            print("│                                     │")
            
            for i, staff in enumerate(self.state.staff, 1):
                emoji = "👨‍🍳" if staff.role == "chef" else "👩‍💼"
                stress_bar = "█" * (staff.stress // 10) + "░" * (10 - staff.stress // 10)
                status = "⚠️ Needs Break" if staff.stress > 70 else "✅ Ready"
                
                print(f"│  {emoji} {staff.name} (Lv.{staff.level})              │")
                print(f"│     Skill: {staff.skill_level}  XP: {staff.xp}        │")
                print(f"│     Stress: {stress_bar} {staff.stress}%          │")
                print(f"│     Skills: {', '.join(staff.skills)}       │")
                print(f"│     Status: {status}           │")
                print("│                                     │")
            
            print("│  [0] Back to main menu              │")
            print("│                                     │")
            self.print_footer()
            
            choice = input("\nEnter staff number to manage (0 to go back): ").strip()
            if choice == "0":
                break
            else:
                print("Staff management coming soon!")
                time.sleep(1)
    
    def view_kitchen(self):
        """Kitchen management screen"""
        while True:
            self.clear_screen()
            self.print_header()
            print("│           KITCHEN STATUS            │")
            print("├─────────────────────────────────────┤")
            print("│                                     │")
            
            print("│  🔥 Equipment Status:               │")
            for equipment in self.state.equipment:
                condition_bar = "█" * (equipment.condition // 10) + "░" * (10 - equipment.condition // 10)
                print(f"│     {equipment.name}: {condition_bar} {equipment.condition}%           │")
            
            print("│                                     │")
            print("│  📦 Inventory:                      │")
            for item in self.state.inventory:
                status = " (Out of stock!)" if item.quantity <= 0 else f" ({item.quantity} units)"
                print(f"│     {item.item}: {item.quantity}{status}       │")
            
            print("│                                     │")
            print("│  [0] Back to main menu              │")
            print("│                                     │")
            self.print_footer()
            
            choice = input("\nEnter choice (0 to go back): ").strip()
            if choice == "0":
                break
            else:
                print("Kitchen management coming soon!")
                time.sleep(1)
    
    def check_menu(self):
        """Menu management screen"""
        self.clear_screen()
        self.print_header()
        print("│              MENU                    │")
        print("├─────────────────────────────────────┤")
        print("│                                     │")
        
        for recipe in self.state.recipes:
            if recipe.name in self.state.unlocked_recipes:
                available = "✅ Available" if self.check_ingredients(recipe.name) else "❌ No ingredients"
                print(f"│  {recipe.name}: ${recipe.price} - {available} │")
        
        print("│                                     │")
        self.print_footer()
        input("\nPress Enter to continue...")
    
    def view_finances(self):
        """Financial overview screen"""
        self.clear_screen()
        self.print_header()
        print("│           FINANCES                   │")
        print("├─────────────────────────────────────┤")
        print("│                                     │")
        print(f"│  Current Money: ${self.state.money:,}        │")
        print(f"│  Daily Expenses: ${self.calculate_daily_expenses():,}     │")
        print(f"│  Staff Salaries: ${self.calculate_staff_salaries():,}     │")
        print("│                                     │")
        self.print_footer()
        input("\nPress Enter to continue...")
    
    def calculate_daily_expenses(self) -> int:
        """Calculate daily expenses"""
        return 100  # Base daily expenses
    
    def calculate_staff_salaries(self) -> int:
        """Calculate total staff salaries"""
        return sum(staff.salary for staff in self.state.staff)
    
    def after_hours_activities(self):
        """After hours activities menu"""
        while True:
            self.clear_screen()
            self.print_header()
            print("│        AFTER HOURS ACTIVITIES       │")
            print("├─────────────────────────────────────┤")
            print("│                                     │")
            
            # Business Activities
            print("│  💼 Business Activities:            │")
            business_activities = []
            for activity_id, activity in self.activities_data.get("activities", {}).items():
                if activity["category"] == "business":
                    business_activities.append((activity_id, activity))
            
            for i, (activity_id, activity) in enumerate(business_activities[:5], 1):
                cost_text = f"${activity['cost']}" if activity['cost'] > 0 else "Free"
                stress_text = f"+{activity['stress']}" if activity['stress'] > 0 else f"{activity['stress']}"
                print(f"│     [{i}] {activity['name']} ({cost_text}, {stress_text} stress) │")
            
            print("│                                     │")
            
            # Restaurant Activities
            print("│  🏠 Restaurant Activities:          │")
            restaurant_activities = []
            for activity_id, activity in self.activities_data.get("activities", {}).items():
                if activity["category"] == "restaurant":
                    restaurant_activities.append((activity_id, activity))
            
            for i, (activity_id, activity) in enumerate(restaurant_activities[:4], 6):
                cost_text = f"${activity['cost']}" if activity['cost'] > 0 else "Free"
                stress_text = f"+{activity['stress']}" if activity['stress'] > 0 else f"{activity['stress']}"
                print(f"│     [{i}] {activity['name']} ({cost_text}, {stress_text} stress) │")
            
            print("│                                     │")
            
            # Personal Activities
            print("│  🧘 Personal Activities:            │")
            personal_activities = []
            for activity_id, activity in self.activities_data.get("activities", {}).items():
                if activity["category"] == "personal":
                    personal_activities.append((activity_id, activity))
            
            for i, (activity_id, activity) in enumerate(personal_activities[:4], 10):
                cost_text = f"${activity['cost']}" if activity['cost'] > 0 else "Free"
                stress_text = f"+{activity['stress']}" if activity['stress'] > 0 else f"{activity['stress']}"
                print(f"│     [{i}] {activity['name']} ({cost_text}, {stress_text} stress) │")
            
            print("│                                     │")
            print(f"│  Owner Burnout: {self.state.owner_burnout}%      │")
            print(f"│  Money: ${self.state.money:,}                     │")
            print("│                                     │")
            print("│  [0] Back to main menu              │")
            print("│                                     │")
            self.print_footer()
            
            choice = input("\nEnter choice (0-13): ").strip()
            if choice == "0":
                break
            else:
                self.perform_activity(choice)
    
    def perform_activity(self, choice):
        """Perform the selected after-hours activity"""
        try:
            choice_num = int(choice)
            
            # Map choice numbers to activities
            all_activities = []
            for activity_id, activity in self.activities_data.get("activities", {}).items():
                all_activities.append((activity_id, activity))
            
            if 1 <= choice_num <= len(all_activities):
                activity_id, activity = all_activities[choice_num - 1]
                
                # Check if player can afford it
                if self.state.money < activity["cost"]:
                    print(f"\n❌ Not enough money! Need ${activity['cost']}")
                    time.sleep(2)
                    return
                
                # Check if player has enough energy
                if self.state.owner_burnout + activity["stress"] > 100:
                    print(f"\n❌ Too tired! Would exceed 100% burnout")
                    time.sleep(2)
                    return
                
                # Perform the activity
                self.state.money -= activity["cost"]
                self.state.owner_burnout = max(0, min(100, self.state.owner_burnout + activity["stress"]))
                
                # Track activity count for habit formation
                activity_type = activity["category"]
                if activity_type not in self.state.activity_counts:
                    self.state.activity_counts[activity_type] = 0
                self.state.activity_counts[activity_type] += 1
                
                # Apply effects
                self.apply_activity_effects(activity)
                
                print(f"\n✅ {activity['name']} completed!")
                print(f"💰 Cost: ${activity['cost']}")
                print(f"😰 Stress: {activity['stress']}")
                print(f"📊 {activity_type.title()} activities: {self.state.activity_counts[activity_type]}/10")
                
                # Check for habit formation
                if self.state.activity_counts[activity_type] >= 10:
                    print(f"🎉 Mastery achieved! {activity['habit_bonus']['description']}")
                
                time.sleep(3)
            else:
                print("\nInvalid choice!")
                time.sleep(1)
        except ValueError:
            print("\nInvalid choice!")
            time.sleep(1)
    
    def apply_activity_effects(self, activity):
        """Apply the effects of an activity"""
        for effect in activity.get("effects", []):
            effect_type = effect["type"]
            value = effect["value"]
            
            if effect_type == "skill_training":
                # Give XP to all chefs
                for staff in self.state.staff:
                    if staff.role == 'chef':
                        staff.xp += 3
                        self.check_skill_up(staff)
            elif effect_type == "staff_discovery_chance":
                # Increase chance of finding good staff
                pass
            elif effect_type == "supplier_discount":
                # Reduce ingredient costs
                pass
            elif effect_type == "customer_attraction":
                # Increase customer flow
                pass
            elif effect_type == "equipment_repair":
                # Repair equipment
                for equipment in self.state.equipment:
                    if equipment.condition < 100:
                        repair_amount = int(value.replace("%", ""))
                        equipment.condition = min(100, equipment.condition + repair_amount)
                        break
            elif effect_type == "owner_burnout":
                # Reduce owner burnout
                if value.startswith("-"):
                    reduction = int(value[1:])
                    self.state.owner_burnout = max(0, self.state.owner_burnout - reduction)
    
    def manage_venue(self):
        """Venue management screen"""
        while True:
            self.clear_screen()
            self.print_header()
            print("│           VENUE MANAGEMENT          │")
            print("├─────────────────────────────────────┤")
            print("│                                     │")
            
            # Current venue info
            if self.state.current_venue:
                venue = self.state.current_venue
                print(f"│  🏠 Current Venue: {venue.name}        │")
                print(f"│     Size: {venue.size.title()} | Capacity: {venue.customer_capacity} customers │")
                print(f"│     Staff Limit: {len(self.state.staff)}/{venue.staff_capacity} | Price Range: {venue.price_range} │")
                print(f"│     Rent: ${venue.rent_cost:,}/month | Owned: {'Yes' if venue.is_owned else 'No'} │")
                print(f"│     Description: {venue.description} │")
            else:
                print("│  ❌ No venue selected!              │")
            
            print("│                                     │")
            print("│  Available Venues:                  │")
            
            # Show available venues
            for i, venue in enumerate(self.state.available_venues, 1):
                status = "📍 Current" if venue == self.state.current_venue else "🔒 Locked"
                if venue.purchase_cost == 0:
                    cost_text = "Rent Only"
                else:
                    cost_text = f"${venue.purchase_cost:,}" if venue.purchase_cost > 0 else "N/A"
                print(f"│     [{i}] {venue.name} ({cost_text}) {status} │")
            
            print("│                                     │")
            print("│  [0] Back to main menu              │")
            print("│                                     │")
            self.print_footer()
            
            choice = input("\nEnter venue number to select (0 to go back): ").strip()
            if choice == "0":
                break
            else:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.state.available_venues):
                        self.select_venue(choice_num - 1)
                    else:
                        print("\nInvalid venue number!")
                        time.sleep(1)
                except ValueError:
                    print("\nInvalid choice!")
                    time.sleep(1)
    
    def select_venue(self, venue_index):
        """Select a new venue"""
        new_venue = self.state.available_venues[venue_index]
        
        # Check if player can afford it
        if new_venue.purchase_cost > 0 and self.state.money < new_venue.purchase_cost:
            print(f"\n❌ Not enough money! Need ${new_venue.purchase_cost:,}")
            time.sleep(2)
            return
        
        # Check staff capacity
        if len(self.state.staff) > new_venue.staff_capacity:
            print(f"\n❌ Too many staff! New venue can only hold {new_venue.staff_capacity} staff")
            print("Fire some staff first.")
            time.sleep(2)
            return
        
        # Confirm selection
        print(f"\n🏠 Switch to {new_venue.name}?")
        if new_venue.purchase_cost > 0:
            print(f"💰 Purchase cost: ${new_venue.purchase_cost:,}")
        else:
            print(f"💰 Rent cost: ${new_venue.rent_cost:,}/month")
        print(f"👥 Staff capacity: {new_venue.staff_capacity}")
        print(f"🍽️ Customer capacity: {new_venue.customer_capacity}")
        
        confirm = input("\nConfirm? (y/n): ").strip().lower()
        if confirm == 'y':
            # Purchase or rent the venue
            if new_venue.purchase_cost > 0:
                self.state.money -= new_venue.purchase_cost
                new_venue.is_owned = True
                self.state.venue_purchase_date = self.state.day
                print(f"✅ Purchased {new_venue.name}!")
            else:
                new_venue.is_owned = False
                print(f"✅ Rented {new_venue.name}!")
            
            self.state.current_venue = new_venue
            time.sleep(2)
        else:
            print("❌ Venue selection cancelled.")
            time.sleep(1)
    
    def apply_for_loan(self):
        """Loan application system"""
        while True:
            self.clear_screen()
            self.print_header()
            print("│           LOAN APPLICATION           │")
            print("├─────────────────────────────────────┤")
            print("│                                     │")
            
            # Show current financial status
            print(f"│  📊 Financial Status:               │")
            print(f"│     Credit Score: {self.state.credit_score}          │")
            print(f"│     Monthly Revenue: ${self.state.monthly_revenue:,}    │")
            print(f"│     Days in Business: {self.state.day}        │")
            print(f"│     Restaurant Rating: {self.state.rating}        │")
            print(f"│     Active Loans: {len([l for l in self.state.loans if l.is_active])}              │")
            
            print("│                                     │")
            print("│  Available Loan Types:              │")
            
            # Show available loans
            available_loans = []
            for loan_id, loan_data in self.loans_data.get("loans", {}).items():
                if self.check_loan_eligibility(loan_data):
                    available_loans.append((loan_id, loan_data))
            
            for i, (loan_id, loan_data) in enumerate(available_loans, 1):
                max_amount = min(loan_data["max_amount"], self.calculate_max_loan_amount(loan_data))
                print(f"│     [{i}] {loan_data['name']} (${max_amount:,}) │")
            
            if not available_loans:
                print("│     ❌ No loans available           │")
            
            print("│                                     │")
            print("│  [0] Back to main menu              │")
            print("│                                     │")
            self.print_footer()
            
            choice = input("\nEnter loan number to apply (0 to go back): ").strip()
            if choice == "0":
                break
            else:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(available_loans):
                        self.process_loan_application(available_loans[choice_num - 1])
                    else:
                        print("\nInvalid loan number!")
                        time.sleep(1)
                except ValueError:
                    print("\nInvalid choice!")
                    time.sleep(1)
    
    def check_loan_eligibility(self, loan_data):
        """Check if player is eligible for a loan"""
        requirements = loan_data["requirements"]
        
        # Check rating requirement
        if self.state.rating < requirements.get("rating", 0):
            return False
        
        # Check days in business
        if self.state.day < requirements.get("days_in_business", 0):
            return False
        
        # Check monthly revenue
        if self.state.monthly_revenue < requirements.get("monthly_revenue", 0):
            return False
        
        # Check credit score
        if self.state.credit_score < requirements.get("credit_score", 0):
            return False
        
        # Check down payment for commercial mortgage
        if "down_payment" in requirements:
            down_payment = requirements["down_payment"]
            # This would be checked when applying for specific amount
        
        return True
    
    def calculate_max_loan_amount(self, loan_data):
        """Calculate maximum loan amount based on business value"""
        base_amount = loan_data["max_amount"]
        
        # Reduce based on existing debt
        total_debt = sum(loan.remaining_balance for loan in self.state.loans if loan.is_active)
        debt_ratio = total_debt / max(self.state.monthly_revenue, 1)
        
        if debt_ratio > 0.5:  # More than 50% debt-to-income
            base_amount = int(base_amount * 0.5)
        elif debt_ratio > 0.3:  # More than 30% debt-to-income
            base_amount = int(base_amount * 0.7)
        
        return base_amount
    
    def process_loan_application(self, loan_info):
        """Process a loan application"""
        loan_id, loan_data = loan_info
        max_amount = min(loan_data["max_amount"], self.calculate_max_loan_amount(loan_data))
        
        print(f"\n🏦 {loan_data['name']} Application")
        print(f"💰 Maximum amount: ${max_amount:,}")
        print(f"📊 Interest rate: {loan_data['interest_rate']*100:.1f}%")
        print(f"⏰ Term: {loan_data['term_months']} months")
        print(f"📋 Collateral: {loan_data['collateral']}")
        print(f"📝 Description: {loan_data['description']}")
        
        try:
            amount = int(input(f"\nEnter loan amount (${loan_data['min_amount']:,} - ${max_amount:,}): "))
            
            if amount < loan_data["min_amount"] or amount > max_amount:
                print(f"❌ Amount must be between ${loan_data['min_amount']:,} and ${max_amount:,}")
                time.sleep(2)
                return
            
            # Calculate monthly payment
            monthly_rate = loan_data["interest_rate"] / 12
            monthly_payment = int(amount * (monthly_rate * (1 + monthly_rate)**loan_data["term_months"]) / ((1 + monthly_rate)**loan_data["term_months"] - 1))
            
            print(f"\n📋 Loan Summary:")
            print(f"💰 Amount: ${amount:,}")
            print(f"💳 Monthly Payment: ${monthly_payment:,}")
            print(f"📊 Total Interest: ${monthly_payment * loan_data['term_months'] - amount:,}")
            
            confirm = input("\nConfirm application? (y/n): ").strip().lower()
            if confirm == 'y':
                # Create loan
                loan = Loan(
                    loan_id=loan_id,
                    name=loan_data["name"],
                    amount=amount,
                    interest_rate=loan_data["interest_rate"],
                    term_months=loan_data["term_months"],
                    monthly_payment=monthly_payment,
                    remaining_balance=amount,
                    days_remaining=loan_data["term_months"] * 30,
                    collateral=loan_data["collateral"]
                )
                
                self.state.loans.append(loan)
                self.state.money += amount
                
                print(f"✅ Loan approved! ${amount:,} added to your account.")
                time.sleep(2)
            else:
                print("❌ Loan application cancelled.")
                time.sleep(1)
                
        except ValueError:
            print("❌ Invalid amount!")
            time.sleep(1)
    
    def calculate_property_value(self, venue):
        """Calculate current property value with appreciation"""
        if not venue or not venue.is_owned:
            return venue.purchase_cost if venue else 0
        
        base_value = venue.purchase_cost
        appreciation_rate = self.loans_data.get("property_appreciation", {}).get("base_rate", 0.03)
        
        # Add rating boost
        rating_boosts = self.loans_data.get("property_appreciation", {}).get("factors", {}).get("rating_boost", {})
        for rating_threshold, boost in rating_boosts.items():
            if self.state.rating >= int(rating_threshold):
                appreciation_rate += boost
        
        # Add venue type boost
        venue_boosts = self.loans_data.get("property_appreciation", {}).get("factors", {}).get("venue_type_boost", {})
        if venue.category in venue_boosts:
            appreciation_rate += venue_boosts[venue.category]
        
        # Add time owned boost
        days_owned = self.state.day - self.state.venue_purchase_date
        time_boosts = self.loans_data.get("property_appreciation", {}).get("factors", {}).get("time_owned_boost", {})
        for days_threshold, boost in time_boosts.items():
            if days_owned >= int(days_threshold):
                appreciation_rate += boost
        
        # Calculate appreciation
        years_owned = days_owned / 365
        appreciation_multiplier = (1 + appreciation_rate) ** years_owned
        
        return int(base_value * appreciation_multiplier)
    
    def next_day(self):
        """Advance to next day"""
        self.state.day += 1
        self.state.current_time = "09:00"
        
        # Daily expenses
        daily_expenses = self.calculate_daily_expenses()
        staff_salaries = self.calculate_staff_salaries()
        
        # Add venue rent if not owned
        venue_rent = 0
        if self.state.current_venue and not self.state.current_venue.is_owned:
            venue_rent = self.state.current_venue.rent_cost // 30  # Daily rent
            daily_expenses += venue_rent
        
        # Process loan payments
        loan_payments = 0
        for loan in self.state.loans:
            if loan.is_active and loan.days_remaining > 0:
                # Monthly payment (every 30 days)
                if self.state.day % 30 == 0:
                    loan_payments += loan.monthly_payment
                    loan.remaining_balance = max(0, loan.remaining_balance - loan.monthly_payment)
                    loan.days_remaining = max(0, loan.days_remaining - 30)
                    
                    # Mark loan as paid off
                    if loan.remaining_balance <= 0:
                        loan.is_active = False
                        print(f"🎉 {loan.name} paid off!")
        
        total_expenses = daily_expenses + staff_salaries + loan_payments
        
        self.state.money -= total_expenses
        
        # Update monthly revenue (every 30 days)
        if self.state.day % 30 == 0:
            self.state.monthly_revenue = self.calculate_monthly_revenue()
        
        # Equipment degradation
        for equipment in self.state.equipment:
            equipment.condition = max(0, equipment.condition - random.randint(1, 5))
            equipment.last_maintenance += 1
        
        # Staff stress increase
        for staff in self.state.staff:
            staff.stress = min(100, staff.stress + random.randint(5, 15))
        
        print(f"\n📅 Day {self.state.day} begins!")
        print(f"💰 Daily expenses: ${total_expenses:,}")
        if venue_rent > 0:
            print(f"🏠 Venue rent: ${venue_rent:,}")
        if loan_payments > 0:
            print(f"🏦 Loan payments: ${loan_payments:,}")
        print(f"💵 Remaining money: ${self.state.money:,}")
        
        # Show property value appreciation (weekly)
        if self.state.day % 7 == 0 and self.state.current_venue and self.state.current_venue.is_owned:
            current_value = self.calculate_property_value(self.state.current_venue)
            original_value = self.state.current_venue.purchase_cost
            appreciation = current_value - original_value
            if appreciation > 0:
                print(f"📈 Property value: ${current_value:,} (+${appreciation:,})")
        
        time.sleep(2)
    
    def calculate_monthly_revenue(self):
        """Calculate monthly revenue based on recent performance"""
        # This is a simplified calculation - in a real game you'd track daily revenue
        base_revenue = self.state.rating * 10  # Base revenue from rating
        venue_multiplier = 1.0
        
        if self.state.current_venue:
            if self.state.current_venue.price_range == "budget":
                venue_multiplier = 0.8
            elif self.state.current_venue.price_range == "mid_range":
                venue_multiplier = 1.2
            elif self.state.current_venue.price_range == "premium":
                venue_multiplier = 1.5
            elif self.state.current_venue.price_range == "luxury":
                venue_multiplier = 2.0
        
        return int(base_revenue * venue_multiplier)

def main():
    """Main function to start the game"""
    game = RestorantGame()
    game.main_menu()

if __name__ == "__main__":
    main() 