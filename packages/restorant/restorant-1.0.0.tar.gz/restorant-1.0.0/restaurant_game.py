#!/usr/bin/env python3
"""
Restaurant Roguelike Game
A terminal-based restaurant management game with staff burnout, recipe skill trees, and dynamic events.
"""

import os
import sys
import yaml
import json
import random
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import math

# Clear screen function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Data Classes
@dataclass
class Staff:
    name: str
    role: str
    skill_level: int = 1
    xp: int = 0
    satisfaction: int = 50
    stress: int = 0
    salary: int = 1000
    hired_date: datetime = field(default_factory=datetime.now)
    max_level: int = 20
    days_since_promotion: int = 0
    performance_score: int = 50
    last_pay_raise: datetime = field(default_factory=datetime.now)
    
    def get_skill_bonus(self) -> float:
        return self.skill_level * 0.1
    
    def get_xp_for_next_level(self) -> int:
        return self.skill_level * 100
    
    def get_xp_progress(self) -> float:
        """Get XP progress as percentage (0.0 to 1.0)"""
        xp_needed = self.get_xp_for_next_level()
        return min(1.0, self.xp / xp_needed)
    
    def get_xp_bar(self, width: int = 20) -> str:
        """Get visual XP progress bar"""
        progress = self.get_xp_progress()
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {self.xp}/{self.get_xp_for_next_level()}"
    
    def get_role_xp_multiplier(self) -> float:
        """Get XP multiplier based on role"""
        role_multipliers = {
            "chef": 1.2,        # Chefs learn faster from cooking
            "prep_cook": 1.1,   # Prep cooks learn moderately
            "server": 0.8,      # Servers learn slower from cooking
            "dishwasher": 0.6   # Dishwashers learn slowest from cooking
        }
        return role_multipliers.get(self.role, 1.0)
    
    def get_role_bonus(self) -> Dict[str, float]:
        """Get role-specific bonuses"""
        bonuses = {
            "chef": {"cooking_success": 0.1, "recipe_quality": 0.15},
            "prep_cook": {"prep_speed": 0.2, "ingredient_efficiency": 0.1},
            "server": {"customer_satisfaction": 0.15, "service_speed": 0.1},
            "dishwasher": {"equipment_maintenance": 0.2, "stress_reduction": 0.1}
        }
        return bonuses.get(self.role, {})
    
    def gain_xp(self, amount: int, activity_type: str = "cooking"):
        """Gain XP with role-based multipliers"""
        if self.skill_level >= self.max_level:
            return False
        
        # Apply role multiplier
        base_xp = amount
        if activity_type == "cooking":
            base_xp = int(amount * self.get_role_xp_multiplier())
        elif activity_type == "training":
            base_xp = amount  # Training gives same XP to all roles
        
        self.xp += base_xp
        leveled_up = False
        
        while self.xp >= self.get_xp_for_next_level() and self.skill_level < self.max_level:
            self.xp -= self.get_xp_for_next_level()
            self.skill_level += 1
            leveled_up = True
        
        return leveled_up
    
    def can_be_promoted(self) -> bool:
        return self.skill_level >= 5 and self.satisfaction >= 70
    
    def get_promotion_cost(self) -> int:
        return self.skill_level * 200
    
    def update_burnout_factors(self):
        """Update staff burnout factors based on stagnation and performance"""
        # Increase days since promotion
        self.days_since_promotion += 1
        
        # Calculate burnout factors
        level_stagnation = max(0, self.days_since_promotion - 30)  # Start affecting after 30 days
        low_satisfaction = max(0, 50 - self.satisfaction)
        high_stress = max(0, self.stress - 50)
        
        # Burnout increases with stagnation, low satisfaction, and high stress
        burnout_increase = (level_stagnation * 0.5) + (low_satisfaction * 0.3) + (high_stress * 0.2)
        
        # Reduce satisfaction based on burnout factors
        if burnout_increase > 0:
            self.satisfaction = max(0, self.satisfaction - int(burnout_increase))
        
        # Performance decreases with low satisfaction
        if self.satisfaction < 30:
            self.performance_score = max(0, self.performance_score - 2)
        elif self.satisfaction > 80:
            self.performance_score = min(100, self.performance_score + 1)
    
    def can_quit(self) -> bool:
        """Check if staff member might quit due to poor conditions"""
        if self.satisfaction < 20:
            return random.random() < 0.1  # 10% chance per day when very unhappy
        elif self.satisfaction < 40:
            return random.random() < 0.05  # 5% chance per day when unhappy
        return False
    
    def get_pay_raise_cost(self) -> int:
        """Calculate cost to give a pay raise"""
        return int(self.salary * 0.2)  # 20% raise

@dataclass
class Recipe:
    id: str
    name: str
    category: str
    difficulty: int
    price: int
    ingredients: List[str]
    unlocks: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    description: str = ""
    
    def get_xp_reward(self, staff_level: int) -> int:
        """Calculate XP reward based on recipe difficulty vs staff level"""
        if staff_level == self.difficulty:
            return 10
        elif staff_level > self.difficulty:
            return random.choice([1, 2, 5])
        else:
            return max(1, self.difficulty - staff_level)
    
    def calculate_ingredient_cost(self, ingredients_dict: Dict[str, 'Ingredient']) -> float:
        """Calculate total ingredient cost for this recipe"""
        total_cost = 0
        for ingredient_id in self.ingredients:
            if ingredient_id in ingredients_dict:
                total_cost += ingredients_dict[ingredient_id].base_cost
        return total_cost
    
    def get_profit_margin(self, ingredients_dict: Dict[str, 'Ingredient']) -> float:
        """Calculate profit margin percentage"""
        ingredient_cost = self.calculate_ingredient_cost(ingredients_dict)
        if ingredient_cost > 0:
            return ((self.price - ingredient_cost) / ingredient_cost) * 100
        return 0

@dataclass
class Ingredient:
    id: str
    name: str
    category: str
    base_cost: float
    suppliers: List[str]
    shelf_life: int
    description: str = ""

@dataclass
class Event:
    id: str
    name: str
    category: str
    probability: float
    description: str
    choices: List[Dict[str, Any]]

@dataclass
class Activity:
    id: str
    name: str
    category: str
    cost: int
    duration: int
    description: str
    effects: Dict[str, int]
    habit_bonus: Dict[str, Any]

@dataclass
class Venue:
    id: str
    name: str
    category: str
    purchase_cost: int
    rent_cost: int
    staff_capacity: int
    customer_capacity: int
    price_range: str
    description: str
    theme: str
    location: str

@dataclass
class Loan:
    id: str
    name: str
    category: str
    amount: int
    interest_rate: float
    term_months: int
    requirements: Dict[str, Any]
    description: str

@dataclass
class CustomerReview:
    rating: int  # 1-5 stars
    food_quality: int  # 1-5
    service_quality: int  # 1-5
    atmosphere: int  # 1-5
    value_for_money: int  # 1-5
    comment: str
    tip_amount: int
    
    def get_overall_score(self) -> float:
        """Calculate overall review score"""
        return (self.food_quality + self.service_quality + self.atmosphere + self.value_for_money) / 4.0
    
    def get_tip_percentage(self) -> float:
        """Calculate tip percentage based on service quality"""
        base_tip = 15.0  # 15% base tip
        if self.service_quality >= 4:
            base_tip += 5  # +5% for good service
        if self.food_quality >= 4:
            base_tip += 3  # +3% for good food
        if self.overall_experience >= 4:
            base_tip += 2  # +2% for overall experience
        return min(25.0, base_tip)  # Cap at 25%
    
    @property
    def overall_experience(self) -> int:
        return int(self.get_overall_score())

class GameState:
    def __init__(self):
        self.money = 10000
        self.rating = 500
        self.day = 1
        self.time = "morning"
        self.staff: List[Staff] = []
        self.unlocked_recipes: List[str] = ["r_001", "r_002", "r_003"]  # Only one list needed
        self.inventory: Dict[str, int] = {}
        self.current_venue = "v_001"
        self.venues_owned: List[str] = ["v_001"]
        self.loans: List[Dict[str, Any]] = []
        self.habits: Dict[str, int] = {}
        self.stress = 0
        self.events_log: List[str] = []
        self.customer_reviews: List[CustomerReview] = []
        self.game_over = False
        self.game_over_reason = ""
        
        # Load data
        self.load_game_data()
        
        # Initialize starting staff
        self.hire_staff("Chef", "chef")
        self.hire_staff("Server", "server")
        
        # Initialize inventory
        self.restock_inventory()
    
    def load_game_data(self):
        """Load all YAML data files"""
        try:
            # Load recipes
            with open('data/recipes.yaml', 'r', encoding='utf-8') as f:
                recipes_data = yaml.safe_load(f)
                self.recipes = {k: Recipe(id=k, **v) for k, v in recipes_data['recipes'].items()}
            
            # Load ingredients
            with open('data/ingredients.yaml', 'r', encoding='utf-8') as f:
                ingredients_data = yaml.safe_load(f)
                self.ingredients = {k: Ingredient(id=k, **v) for k, v in ingredients_data['ingredients'].items()}
            
            # Load events
            with open('data/events.yaml', 'r', encoding='utf-8') as f:
                events_data = yaml.safe_load(f)
                self.events = {k: Event(id=k, **v) for k, v in events_data['events'].items()}
            
            # Load activities
            with open('data/activities.yaml', 'r', encoding='utf-8') as f:
                activities_data = yaml.safe_load(f)
                self.activities = {k: Activity(id=k, **v) for k, v in activities_data['activities'].items()}
            
            # Load venues
            with open('data/venues.yaml', 'r', encoding='utf-8') as f:
                venues_data = yaml.safe_load(f)
                self.venues = {k: Venue(id=k, **v) for k, v in venues_data['venues'].items()}
            
            # Load loans
            with open('data/loans.yaml', 'r', encoding='utf-8') as f:
                loans_data = yaml.safe_load(f)
                self.loans_available = {k: Loan(id=k, **v) for k, v in loans_data['loans'].items()}
                
        except FileNotFoundError as e:
            print(f"Error: Could not find data file: {e}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in data file: {e}")
            sys.exit(1)
    
    def hire_staff(self, name: str, role: str):
        """Hire a new staff member"""
        venue = self.get_venue()
        if len(self.staff) >= venue.staff_capacity:
            return False
        
        staff = Staff(name=name, role=role)
        self.staff.append(staff)
        self.log_event(f"👥 Hired {name} as {role}")
        return True
    
    def can_hire_staff(self) -> bool:
        """Check if we can hire more staff"""
        venue = self.get_venue()
        return len(self.staff) < venue.staff_capacity
    
    def enforce_staff_capacity(self):
        """Enforce staff capacity limits"""
        venue = self.get_venue()
        if len(self.staff) > venue.staff_capacity:
            # Remove excess staff (keep the highest level ones)
            excess_count = len(self.staff) - venue.staff_capacity
            self.staff.sort(key=lambda s: s.skill_level, reverse=True)
            removed_staff = self.staff[venue.staff_capacity:]
            self.staff = self.staff[:venue.staff_capacity]
            
            for staff in removed_staff:
                self.log_event(f"👋 {staff.name} left due to venue capacity limits")
            
            return True
        return False
    
    def get_staff_hire_cost(self) -> int:
        """Get cost to hire new staff"""
        return 1000 + (len(self.staff) * 200)  # More expensive as you have more staff
    
    def train_staff(self, staff_index: int, training_type: str):
        """Train a staff member"""
        if staff_index >= len(self.staff):
            return False
        
        staff = self.staff[staff_index]
        training_costs = {
            "basic": 50,
            "advanced": 150,
            "expert": 300
        }
        
        training_xp = {
            "basic": 25,
            "advanced": 50,
            "expert": 100
        }
        
        cost = training_costs.get(training_type, 50)
        xp_gain = training_xp.get(training_type, 25)
        
        if not self.can_afford(cost):
            return False
        
        self.spend_money(cost)
        leveled_up = staff.gain_xp(xp_gain, "training")
        
        if leveled_up:
            self.log_event(f"🎉 {staff.name} leveled up to {staff.skill_level}!")
            staff.satisfaction += 10
        else:
            self.log_event(f"📚 {staff.name} gained {xp_gain} XP from {training_type} training")
        
        return True
    
    def promote_staff(self, staff_index: int):
        """Promote a staff member"""
        if staff_index >= len(self.staff):
            return False
        
        staff = self.staff[staff_index]
        
        if not staff.can_be_promoted():
            return False
        
        cost = staff.get_promotion_cost()
        if not self.can_afford(cost):
            return False
        
        self.spend_money(cost)
        staff.salary += 200
        staff.satisfaction += 20
        staff.stress -= 10
        staff.days_since_promotion = 0  # Reset stagnation
        
        self.log_event(f"🎖️ {staff.name} promoted! New salary: ${staff.salary}")
        return True
    
    def restock_inventory(self):
        """Restock basic ingredients"""
        for ingredient_id in self.ingredients:
            if ingredient_id not in self.inventory:
                self.inventory[ingredient_id] = 10
    
    def buy_ingredients(self, ingredient_id: str, amount: int):
        """Buy ingredients"""
        if ingredient_id not in self.ingredients:
            return False
        
        ingredient = self.ingredients[ingredient_id]
        cost = int(ingredient.base_cost * amount)
        
        if not self.can_afford(cost):
            return False
        
        self.spend_money(cost)
        self.inventory[ingredient_id] = self.inventory.get(ingredient_id, 0) + amount
        self.log_event(f"📦 Bought {amount} {ingredient.name} for ${cost}")
        return True
    
    def pay_daily_expenses(self):
        """Pay daily expenses (staff salaries, rent, etc.)"""
        venue = self.get_venue()
        
        # Staff salaries
        total_salary = sum(staff.salary for staff in self.staff)
        self.spend_money(total_salary)
        
        # Venue rent
        self.spend_money(venue.rent_cost)
        
        # Loan payments
        for loan in self.loans:
            payment = loan['monthly_payment'] / 30  # Daily payment
            self.spend_money(int(payment))
        
        # Check for ingredient spoilage
        spoiled_items = []
        for ingredient_id, amount in list(self.inventory.items()):
            if ingredient_id in self.ingredients:
                ingredient = self.ingredients[ingredient_id]
                # Simple spoilage: 1% chance per day for items past half shelf life
                if amount > 0 and random.random() < 0.01:  # 1% daily spoilage chance
                    spoiled_amount = min(amount, 1)  # Spoil 1 unit
                    self.inventory[ingredient_id] -= spoiled_amount
                    spoiled_items.append(f"{ingredient.name} ({spoiled_amount})")
        
        if spoiled_items:
            self.log_event(f"🗑️ Spoiled ingredients: {', '.join(spoiled_items)}")
        
        self.log_event(f"💸 Daily expenses: Staff ${total_salary}, Rent ${venue.rent_cost}")
    
    def get_inventory_value(self) -> float:
        """Calculate total inventory value"""
        total_value = 0
        for ingredient_id, amount in self.inventory.items():
            if ingredient_id in self.ingredients:
                ingredient = self.ingredients[ingredient_id]
                total_value += ingredient.base_cost * amount
        return total_value
    
    def save_game(self, filename: str = "savegame.json"):
        """Save the current game state"""
        try:
            save_data = {
                'money': self.money,
                'rating': self.rating,
                'day': self.day,
                'time': self.time,
                'current_venue': self.current_venue,
                'venues_owned': self.venues_owned,
                'unlocked_recipes': self.unlocked_recipes,
                'inventory': self.inventory,
                'loans': self.loans,
                'habits': self.habits,
                'stress': self.stress,
                'events_log': self.events_log[-20:],  # Save last 20 events
                'staff': []
            }
            
            # Convert staff objects to dictionaries
            for staff in self.staff:
                staff_data = asdict(staff)
                # Convert datetime to string for JSON serialization
                staff_data['hired_date'] = staff.hired_date.isoformat()
                save_data['staff'].append(staff_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.log_event(f"💾 Game saved to {filename}")
            return True
            
        except Exception as e:
            self.log_event(f"❌ Failed to save game: {e}")
            return False
    
    def load_game(self, filename: str = "savegame.json"):
        """Load a saved game state"""
        try:
            if not os.path.exists(filename):
                self.log_event(f"❌ Save file {filename} not found")
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Load basic data
            self.money = save_data.get('money', 10000)
            self.rating = save_data.get('rating', 500)
            self.day = save_data.get('day', 1)
            self.time = save_data.get('time', 'morning')
            self.current_venue = save_data.get('current_venue', 'v_001')
            self.venues_owned = save_data.get('venues_owned', ['v_001'])
            self.unlocked_recipes = save_data.get('unlocked_recipes', ['r_001', 'r_002', 'r_003'])
            self.inventory = save_data.get('inventory', {})
            self.loans = save_data.get('loans', [])
            self.habits = save_data.get('habits', {})
            self.stress = save_data.get('stress', 0)
            self.events_log = save_data.get('events_log', [])
            
            # Load staff
            self.staff = []
            for staff_data in save_data.get('staff', []):
                # Convert string back to datetime
                hired_date_str = staff_data.get('hired_date', '')
                if hired_date_str:
                    try:
                        staff_data['hired_date'] = datetime.fromisoformat(hired_date_str)
                    except:
                        staff_data['hired_date'] = datetime.now()
                
                staff = Staff(**staff_data)
                self.staff.append(staff)
            
            self.log_event(f"📂 Game loaded from {filename}")
            return True
            
        except Exception as e:
            self.log_event(f"❌ Failed to load game: {e}")
            return False
    
    def has_save_file(self, filename: str = "savegame.json") -> bool:
        """Check if a save file exists"""
        return os.path.exists(filename)
    
    def log_event(self, message: str):
        """Add event to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.events_log.append(f"[{timestamp}] {message}")
        if len(self.events_log) > 50:  # Keep only last 50 events
            self.events_log.pop(0)
    
    def get_venue(self) -> Venue:
        return self.venues[self.current_venue]
    
    def can_afford(self, cost: int) -> bool:
        return self.money >= cost
    
    def spend_money(self, amount: int):
        self.money -= amount
        self.log_event(f"💰 Spent ${amount}")
    
    def earn_money(self, amount: int):
        self.money += amount
        self.log_event(f"💰 Earned ${amount}")
    
    def check_game_over(self):
        """Check for game over conditions"""
        if self.money < -5000:
            self.game_over = True
            self.game_over_reason = "Bankruptcy - too much debt"
            return True
        
        if self.rating < 100:
            self.game_over = True
            self.game_over_reason = "Restaurant reputation destroyed"
            return True
        
        if len(self.staff) == 0:
            self.game_over = True
            self.game_over_reason = "No staff remaining"
            return True
        
        if self.stress >= 100:
            self.game_over = True
            self.game_over_reason = "Complete burnout"
            return True
        
        return False
    
    def unlock_recipe(self, recipe_id: str):
        """Unlock a new recipe"""
        if recipe_id not in self.unlocked_recipes and recipe_id in self.recipes:
            self.unlocked_recipes.append(recipe_id)
            recipe = self.recipes[recipe_id]
            self.log_event(f"📚 Unlocked new recipe: {recipe.name}")
            return True
        return False
    
    def check_recipe_unlocks(self):
        """Check if any new recipes can be unlocked"""
        for recipe_id, recipe in self.recipes.items():
            if recipe_id not in self.unlocked_recipes:
                # Check if all required recipes are unlocked
                can_unlock = True
                for required_recipe in recipe.requires:
                    if required_recipe not in self.unlocked_recipes:
                        can_unlock = False
                        break
                
                if can_unlock:
                    self.unlock_recipe(recipe_id)
    
    def update_staff_burnout(self):
        """Update staff burnout factors and check for quits"""
        for staff in self.staff:
            staff.update_burnout_factors()
            
            # Check if staff might quit
            if staff.can_quit():
                self.staff.remove(staff)
                self.log_event(f"👋 {staff.name} quit due to poor working conditions")
                return True
        return False
    
    def give_staff_pay_raise(self, staff_index: int) -> bool:
        """Give a staff member a pay raise"""
        if 0 <= staff_index < len(self.staff):
            staff = self.staff[staff_index]
            raise_cost = staff.get_pay_raise_cost()
            
            if self.can_afford(raise_cost):
                self.spend_money(raise_cost)
                staff.salary = int(staff.salary * 1.2)  # 20% raise
                staff.satisfaction += 20
                staff.days_since_promotion = 0  # Reset stagnation
                staff.last_pay_raise = datetime.now()
                self.log_event(f"💰 Gave {staff.name} a pay raise to ${staff.salary}")
                return True
            else:
                self.log_event(f"❌ Cannot afford pay raise for {staff.name} (${raise_cost})")
        return False
    
    def generate_customer_review(self, order_success: bool, food_quality: int, service_quality: int) -> CustomerReview:
        """Generate a customer review based on their experience"""
        venue = self.get_venue()
        
        # Base ratings
        food_rating = food_quality if order_success else 1
        service_rating = service_quality
        atmosphere_rating = min(5, max(1, int(self.rating / 200) + random.randint(-1, 1)))
        value_rating = min(5, max(1, int((self.rating / 1000) * 5) + random.randint(-1, 1)))
        
        # Overall rating
        overall_rating = int((food_rating + service_rating + atmosphere_rating + value_rating) / 4)
        
        # Generate comment based on experience
        if order_success:
            if overall_rating >= 4:
                comments = [
                    "Excellent experience! Will definitely return.",
                    "Amazing food and service. Highly recommended!",
                    "Great atmosphere and delicious food.",
                    "Outstanding service and quality."
                ]
            elif overall_rating >= 3:
                comments = [
                    "Good food, decent service.",
                    "Nice atmosphere, food was okay.",
                    "Satisfactory experience overall.",
                    "Decent value for money."
                ]
            else:
                comments = [
                    "Food was okay but service could be better.",
                    "Not impressed with the experience.",
                    "Expected better for the price.",
                    "Disappointing overall."
                ]
        else:
            comments = [
                "Order was not prepared correctly.",
                "Very disappointed with the service.",
                "Won't be coming back.",
                "Poor experience overall."
            ]
        
        comment = random.choice(comments)
        
        # Calculate tip based on service quality
        base_bill = 20  # Assume average bill
        tip_percentage = 15.0  # Base 15%
        if service_rating >= 4:
            tip_percentage += 5
        if food_rating >= 4:
            tip_percentage += 3
        
        tip_amount = int(base_bill * (tip_percentage / 100))
        
        review = CustomerReview(
            rating=overall_rating,
            food_quality=food_rating,
            service_quality=service_rating,
            atmosphere=atmosphere_rating,
            value_for_money=value_rating,
            comment=comment,
            tip_amount=tip_amount
        )
        
        return review

class GameUI:
    def __init__(self, game: GameState):
        self.game = game
    
    def draw_panel(self, title: str, content: List[str], width: int = 40):
        """Draw a simple panel with title and content"""
        print("┌" + "─" * (width - 2) + "┐")
        print("│" + title.center(width - 2) + "│")
        print("├" + "─" * (width - 2) + "┤")
        
        for line in content:
            if len(line) > width - 4:
                line = line[:width - 7] + "..."
            print("│ " + line.ljust(width - 4) + " │")
        
        # Fill remaining space
        remaining = 15 - len(content)
        for _ in range(remaining):
            print("│" + " " * (width - 2) + "│")
        
        print("└" + "─" * (width - 2) + "┘")
    
    def render_main_screen(self):
        """Render the main game screen"""
        clear_screen()
        
        venue = self.game.get_venue()
        
        # Header
        print("=" * 80)
        print("🍽️  RESTAURANT ROGUELIKE 🍽️".center(80))
        print("=" * 80)
        
        # Main layout - two columns
        print("TERMINAL LOG".ljust(40) + "STATS".ljust(40))
        print("-" * 40 + "-" * 40)
        
        # Left column - Terminal/Events
        terminal_content = []
        for event in self.game.events_log[-10:]:  # Last 10 events
            terminal_content.append(event)
        
        while len(terminal_content) < 10:
            terminal_content.append("")
        
        # Right column - Stats
        stats_content = [
            f"💰 Money: ${self.game.money:,}",
            f"⭐ Rating: {self.game.rating}",
            f"📅 Day: {self.game.day}",
            f"🕐 Time: {self.game.time}",
            f"",
            f"🏢 Venue: {venue.name}",
            f"👥 Staff: {len(self.game.staff)}/{venue.staff_capacity}",
            f"🪑 Capacity: {venue.customer_capacity}",
            f"💲 Price Range: {venue.price_range}",
            f"",
            f"📚 Recipes: {len(self.game.unlocked_recipes)}",
            f"📦 Inventory: {len(self.game.inventory)} items",
            f"🏦 Loans: {len(self.game.loans)}",
            f"😰 Stress: {self.game.stress}/100",
            f"🎯 Habits: {len(self.game.habits)}"
        ]
        
        # Display in two columns
        for i in range(max(len(terminal_content), len(stats_content))):
            left = terminal_content[i] if i < len(terminal_content) else ""
            right = stats_content[i] if i < len(stats_content) else ""
            print(f"{left:<40}{right:<40}")
        
        print("-" * 80)
        
        # Menu
        menu_content = [
            "1. Start Service Hours",
            "2. View Kitchen",
            "3. Manage Staff",
            "4. View Recipes",
            "5. Manage Inventory",
            "6. View Venues",
            "7. Apply for Loans",
            "8. After-Hours Activities",
            "9. View Customer Reviews",
            "0. Save Game",
            "Q. Quit Game"
        ]
        
        print("MENU:")
        for item in menu_content:
            print(f"  {item}")
        
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_kitchen_screen(self):
        """Render the kitchen management screen"""
        clear_screen()
        
        venue = self.game.get_venue()
        
        print("=" * 80)
        print("🏠 KITCHEN MANAGEMENT".center(80))
        print("=" * 80)
        
        kitchen_content = [
            f"🏢 Current Venue: {venue.name}",
            f"👥 Staff Capacity: {len(self.game.staff)}/{venue.staff_capacity}",
            f"🪑 Customer Capacity: {venue.customer_capacity}",
            f"",
            "Equipment Status:",
            "✅ Stove - Operational",
            "✅ Refrigerator - Operational", 
            "✅ Sink - Operational",
            "✅ Prep Station - Operational",
            f"",
            f"📦 Inventory Items: {len(self.game.inventory)}",
            f"📚 Available Recipes: {len(self.game.unlocked_recipes)}",
            f"",
            "1. View Staff Details",
            "2. Manage Inventory",
            "3. Equipment Maintenance",
            "4. Back to Main Menu"
        ]
        
        self.draw_panel("KITCHEN", kitchen_content)
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_staff_screen(self):
        """Render the staff management screen"""
        clear_screen()
        
        print("=" * 80)
        print("👥 STAFF MANAGEMENT".center(80))
        print("=" * 80)
        
        # Show staff overview
        for i, staff in enumerate(self.game.staff, 1):
            promotion_status = "🎖️" if staff.can_be_promoted() else "  "
            burnout_warning = "🔥" if staff.satisfaction < 30 else "⚠️" if staff.satisfaction < 50 else "  "
            role_icon = {"chef": "👨‍🍳", "server": "👨‍💼", "prep_cook": "🔪", "dishwasher": "🧽"}.get(staff.role, "👤")
            print(f"{i}. {promotion_status} {burnout_warning} {role_icon} {staff.name} ({staff.role})")
            print(f"   Level: {staff.skill_level}/{staff.max_level} | XP: {staff.get_xp_bar(15)}")
            print(f"   Satisfaction: {staff.satisfaction}% | Stress: {staff.stress} | Performance: {staff.performance_score}%")
            print(f"   Salary: ${staff.salary} | Days since promotion: {staff.days_since_promotion}")
            
            # Show burnout warnings
            if staff.satisfaction < 30:
                print(f"   ⚠️  BURNOUT RISK: Very low satisfaction!")
            elif staff.satisfaction < 50:
                print(f"   ⚠️  WARNING: Low satisfaction")
            
            # Show role bonuses
            role_bonus = staff.get_role_bonus()
            if role_bonus:
                bonus_text = ", ".join([f"{k.replace('_', ' ').title()}: +{int(v*100)}%" for k, v in role_bonus.items()])
                print(f"   Bonuses: {bonus_text}")
            print()
        
        print("=" * 80)
        print("STAFF ACTIONS:")
        print("1. Train Staff")
        print("2. Promote Staff")
        print("3. Give Pay Raise")
        print("4. Hire New Staff")
        print("5. Fire Staff")
        print("5. Back to Kitchen")
        
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_staff_training_screen(self):
        """Render staff training selection screen"""
        clear_screen()
        
        print("=" * 80)
        print("📚 STAFF TRAINING".center(80))
        print("=" * 80)
        
        print("Select staff member to train:")
        print()
        
        for i, staff in enumerate(self.game.staff, 1):
            print(f"{i}. {staff.name} ({staff.role}) - Level {staff.skill_level}")
            print(f"   Current XP: {staff.get_xp_bar(20)}")
            print()
        
        print("Training Options:")
        print("1. Basic Training ($50) - +25 XP")
        print("2. Advanced Training ($150) - +50 XP")
        print("3. Expert Training ($300) - +100 XP")
        print("4. Back to Staff Management")
        
        print("\nEnter staff number (1-{}) and training type (1-3): ".format(len(self.game.staff)), end="", flush=True)
    
    def render_staff_promotion_screen(self):
        """Render staff promotion selection screen"""
        clear_screen()
        
        print("=" * 80)
        print("🎖️ STAFF PROMOTION".center(80))
        print("=" * 80)
        
        promotable_staff = [staff for staff in self.game.staff if staff.can_be_promoted()]
        
        if not promotable_staff:
            print("No staff members are eligible for promotion.")
            print("Requirements: Level 5+ and 70%+ satisfaction")
            print("\nPress Enter to continue...")
            return
        
        print("Staff eligible for promotion:")
        print()
        
        for i, staff in enumerate(promotable_staff, 1):
            cost = staff.get_promotion_cost()
            print(f"{i}. {staff.name} ({staff.role}) - Level {staff.skill_level}")
            print(f"   Satisfaction: {staff.satisfaction}% | Cost: ${cost}")
            print()
        
        print("Enter staff number to promote: ", end="", flush=True)
    
    def render_recipes_screen(self):
        """Render the recipes screen"""
        clear_screen()
        
        print("=" * 80)
        print("📚 RECIPES".center(80))
        print("=" * 80)
        
        recipes_content = []
        
        for i, recipe_id in enumerate(self.game.unlocked_recipes[:10], 1):
            recipe = self.game.recipes[recipe_id]
            recipes_content.append(f"{i}. {recipe.name} - ${recipe.price}")
            recipes_content.append(f"   Difficulty: {recipe.difficulty}/10 | Category: {recipe.category}")
            recipes_content.append("")
        
        if len(self.game.unlocked_recipes) > 10:
            recipes_content.append(f"... and {len(self.game.unlocked_recipes) - 10} more")
        
        recipes_content.extend([
            "",
            "1. View Recipe Details",
            "2. Back to Main Menu"
        ])
        
        self.draw_panel("RECIPES", recipes_content)
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_inventory_screen(self):
        """Render the inventory screen"""
        clear_screen()
        
        print("=" * 80)
        print("📦 INVENTORY".center(80))
        print("=" * 80)
        
        inventory_value = self.game.get_inventory_value()
        print(f"Total Inventory Value: ${inventory_value:.0f}")
        print()
        
        inventory_content = []
        
        for ingredient_id, amount in list(self.game.inventory.items())[:10]:
            ingredient = self.game.ingredients[ingredient_id]
            value = ingredient.base_cost * amount
            inventory_content.append(f"{ingredient.name}: {amount} units (${value:.0f})")
        
        if len(self.game.inventory) > 10:
            inventory_content.append(f"... and {len(self.game.inventory) - 10} more items")
        
        inventory_content.extend([
            "",
            "1. Buy Ingredients",
            "2. Restock All",
            "3. View All Items",
            "4. Back to Kitchen"
        ])
        
        self.draw_panel("INVENTORY", inventory_content)
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_venues_screen(self):
        """Render the venues screen"""
        clear_screen()
        
        print("=" * 80)
        print("🏢 VENUES".center(80))
        print("=" * 80)
        
        venues_content = []
        
        for venue_id, venue in self.game.venues.items():
            owned = "✅" if venue_id in self.game.venues_owned else "❌"
            venues_content.append(f"{owned} {venue.name}")
            venues_content.append(f"   Cost: ${venue.purchase_cost:,} | Rent: ${venue.rent_cost}/month")
            venues_content.append(f"   Staff: {venue.staff_capacity} | Customers: {venue.customer_capacity}")
            venues_content.append("")
        
        venues_content.extend([
            "1. Purchase Venue",
            "2. Switch Venue",
            "3. Back to Main Menu"
        ])
        
        self.draw_panel("VENUES", venues_content)
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_loans_screen(self):
        """Render the loans screen"""
        clear_screen()
        
        print("=" * 80)
        print("🏦 LOANS".center(80))
        print("=" * 80)
        
        loans_content = []
        
        for loan_id, loan in self.game.loans_available.items():
            loans_content.append(f"{loan.name}")
            loans_content.append(f"   Amount: ${loan.amount:,} | Rate: {loan.interest_rate*100}%")
            loans_content.append(f"   Term: {loan.term_months} months")
            loans_content.append("")
        
        loans_content.extend([
            "1. Apply for Loan",
            "2. View Current Loans",
            "3. Back to Main Menu"
        ])
        
        self.draw_panel("LOANS", loans_content)
        print("\nEnter your choice: ", end="", flush=True)
    
    def render_activities_screen(self):
        """Render the activities screen"""
        clear_screen()
        
        print("=" * 80)
        print("🎯 AFTER-HOURS ACTIVITIES".center(80))
        print("=" * 80)
        
        activities_content = []
        
        for activity_id, activity in list(self.game.activities.items())[:8]:
            activities_content.append(f"{activity.name} - ${activity.cost}")
            activities_content.append(f"   {activity.description}")
            activities_content.append("")
        
        activities_content.extend([
            "1. Choose Activity",
            "2. Trigger Night Events",
            "3. View All Activities",
            "4. Show Habit Progress",
            "5. Back to Main Menu"
        ])
        
        self.draw_panel("ACTIVITIES", activities_content)
        print("\nEnter your choice: ", end="", flush=True)

class RestaurantGame:
    def __init__(self):
        self.game = GameState()
        self.ui = GameUI(self.game)
    
    def start_service_hours(self):
        """Start the restaurant service hours"""
        self.game.log_event("🚪 Opening restaurant for service hours")
        
        # Pay daily expenses first
        self.game.pay_daily_expenses()
        
        # Calculate restaurant standing factors
        venue = self.game.get_venue()
        total_staff_skill = sum(staff.skill_level for staff in self.game.staff)
        avg_staff_skill = total_staff_skill / max(1, len(self.game.staff))
        
        # Base customer count based on restaurant standing
        base_customers = max(1, min(16, int(self.game.rating / 100) + 2))
        
        # Determine if we should show detailed events or summary
        show_detailed_events = True  # Can be made configurable later
        
        # Simulate service hours
        customers_served = 0
        revenue = 0
        events_this_service = 0
        max_events = 16
        
        for hour in range(8):  # 8 hours of service
            # Calculate customers for this hour based on restaurant standing
            hour_multiplier = 1.0
            if hour in [5, 6, 7]:  # Peak dinner hours
                hour_multiplier = 1.5
            
            # Customer count influenced by rating, venue, and staff
            customer_attraction = (self.game.rating / 1000) + (avg_staff_skill / 10) + (venue.customer_capacity / 50)
            num_customers = max(1, min(5, int(base_customers * hour_multiplier * customer_attraction / 8)))
            
            for customer in range(num_customers):
                if events_this_service >= max_events:
                    break
                
                # Determine customer order based on restaurant quality
                order = self.generate_customer_order()
                
                if order:
                    # Process the order
                    order_result = self.process_customer_order(order)
                    if order_result['success']:
                        customers_served += 1
                        revenue += order_result['revenue']
                        self.game.rating += order_result['rating_gain']
                        events_this_service += 1
                        
                        if show_detailed_events:
                            self.game.log_event(order_result['message'])
                    else:
                        self.game.rating -= 1
                        events_this_service += 1
                        if show_detailed_events:
                            self.game.log_event(order_result['message'])
            
            # Random events (kitchen incidents, staff issues, etc.)
            if random.random() < 0.15 and events_this_service < max_events:  # 15% chance per hour
                # Filter events by service hours categories
                service_categories = ["customer", "kitchen", "staff", "business", "special"]
                self.trigger_random_event(random.choice(service_categories))
                events_this_service += 1
            
            if events_this_service >= max_events:
                break
            
            time.sleep(0.1)  # Small delay for visual effect
        
        # End of service
        self.game.earn_money(revenue)
        self.game.log_event(f"🏁 Service hours ended - Served {customers_served} customers, Revenue: ${revenue}")
        
        # Pay staff daily salaries
        total_salaries = sum(staff.salary for staff in self.game.staff)
        self.game.spend_money(total_salaries)
        self.game.log_event(f"💰 Paid staff salaries: ${total_salaries}")
        
        # Update staff burnout and check for quits
        if self.game.update_staff_burnout():
            self.game.log_event("⚠️ Staff member quit due to poor conditions")
        
        # Increase stress for staff
        for staff in self.game.staff:
            staff.stress += random.randint(5, 15)
            staff.satisfaction -= random.randint(1, 5)
        
        self.game.stress += random.randint(10, 20)
        self.game.day += 1
        
        # Check for recipe unlocks
        self.game.check_recipe_unlocks()
        
        # Check for game over
        if self.game.check_game_over():
            print(f"\n💀 GAME OVER: {self.game.game_over_reason}")
            input("Press Enter to continue...")
            return
        
        input("\nPress Enter to continue...")
    
    def generate_customer_order(self):
        """Generate a customer order based on restaurant quality"""
        venue = self.game.get_venue()
        total_staff_skill = sum(staff.skill_level for staff in self.game.staff)
        avg_staff_skill = total_staff_skill / max(1, len(self.game.staff))
        
        # Calculate restaurant quality score (0-100)
        quality_score = min(100, (
            (self.game.rating / 10) +  # Rating contribution
            (avg_staff_skill * 2) +    # Staff skill contribution
            (len(self.game.staff) * 5) +  # Staff count contribution
            (venue.customer_capacity / 10)  # Venue quality contribution
        ))
        
        # Determine order complexity based on quality
        order = {
            'dishes': [],
            'drinks': [],
            'desserts': [],
            'total_value': 0
        }
        
        # Always order a main dish
        main_dish = self.select_dish_by_quality(quality_score, "main")
        if main_dish:
            order['dishes'].append(main_dish)
            order['total_value'] += main_dish.price
        
        # Chance for starter (30-70% based on quality)
        starter_chance = 0.3 + (quality_score / 100) * 0.4
        if random.random() < starter_chance:
            starter = self.select_dish_by_quality(quality_score, "starter")
            if starter:
                order['dishes'].append(starter)
                order['total_value'] += starter.price
        
        # Chance for dessert (20-60% based on quality)
        dessert_chance = 0.2 + (quality_score / 100) * 0.4
        if random.random() < dessert_chance:
            dessert = self.select_dish_by_quality(quality_score, "dessert")
            if dessert:
                order['desserts'].append(dessert)
                order['total_value'] += dessert.price
        
        # Chance for drinks (40-90% based on quality)
        drink_chance = 0.4 + (quality_score / 100) * 0.5
        if random.random() < drink_chance:
            drink = self.select_dish_by_quality(quality_score, "drink")
            if drink:
                order['drinks'].append(drink)
                order['total_value'] += drink.price
        
        return order if order['dishes'] else None
    
    def select_dish_by_quality(self, quality_score, dish_type):
        """Select a dish based on restaurant quality and dish type"""
        available_recipes = []
        
        for recipe_id in self.game.unlocked_recipes:
            recipe = self.game.recipes[recipe_id]
            
            # Filter by dish type
            if dish_type == "main":
                if recipe.category in ["italian", "grilling", "sushi", "asian"]:
                    available_recipes.append(recipe)
            elif dish_type == "starter":
                if recipe.category in ["basic"]:
                    available_recipes.append(recipe)
            elif dish_type == "dessert":
                if recipe.category in ["dessert"]:
                    available_recipes.append(recipe)
            elif dish_type == "drink":
                if recipe.category in ["cafe"]:
                    available_recipes.append(recipe)
        
        if not available_recipes:
            return None
        
        # Weight selection by quality - higher quality restaurants get better dishes
        weighted_recipes = []
        for recipe in available_recipes:
            # Higher quality restaurants prefer higher difficulty/price dishes
            quality_preference = (recipe.difficulty + recipe.price / 10) / 20
            weight = max(0.1, quality_preference * (quality_score / 100))
            weighted_recipes.append((recipe, weight))
        
        # Select based on weights
        total_weight = sum(weight for _, weight in weighted_recipes)
        if total_weight == 0:
            return random.choice(available_recipes)
        
        rand = random.uniform(0, total_weight)
        current_weight = 0
        
        for recipe, weight in weighted_recipes:
            current_weight += weight
            if rand <= current_weight:
                return recipe
        
        return random.choice(available_recipes)
    
    def process_customer_order(self, order):
        """Process a customer order and return results"""
        venue = self.game.get_venue()
        total_staff_skill = sum(staff.skill_level for staff in self.game.staff)
        avg_staff_skill = total_staff_skill / max(1, len(self.game.staff))
        
        # Check if we have ingredients for all dishes
        all_dishes = order['dishes'] + order['drinks'] + order['desserts']
        missing_ingredients = []
        
        for dish in all_dishes:
            for ingredient_id in dish.ingredients:
                if self.game.inventory.get(ingredient_id, 0) < 1:
                    missing_ingredients.append(ingredient_id)
        
        if missing_ingredients:
            missing_names = []
            for ing_id in missing_ingredients:
                ingredient = self.game.ingredients.get(ing_id)
                if ingredient:
                    missing_names.append(ingredient.name)
                else:
                    missing_names.append("Unknown")
            return {
                'success': False,
                'revenue': 0,
                'rating_gain': -1,
                'message': f"❌ Cannot fulfill order - missing ingredients: {', '.join(missing_names)}"
            }
        
        # Calculate success chance based on staff skill vs dish difficulty
        total_difficulty = sum(dish.difficulty for dish in all_dishes)
        base_success_chance = min(0.95, 0.5 + (avg_staff_skill * 0.1) - (total_difficulty * 0.05))
        
        # Apply role bonuses to success chance
        role_success_bonus = 0
        for staff in self.game.staff:
            role_bonus = staff.get_role_bonus()
            if "cooking_success" in role_bonus:
                role_success_bonus += role_bonus["cooking_success"]
        
        success_chance = min(0.95, base_success_chance + role_success_bonus)
        
        if random.random() < success_chance:
            # Calculate ingredient costs
            total_ingredient_cost = 0
            for dish in all_dishes:
                for ingredient_id in dish.ingredients:
                    if ingredient_id in self.game.ingredients:
                        ingredient = self.game.ingredients[ingredient_id]
                        total_ingredient_cost += ingredient.base_cost
            
            # Calculate profit (revenue - ingredient costs)
            revenue = order['total_value']
            profit = revenue - total_ingredient_cost
            rating_gain = 1
            
            # Consume ingredients
            for dish in all_dishes:
                for ingredient_id in dish.ingredients:
                    self.game.inventory[ingredient_id] -= 1
            
            # Staff gain XP
            for staff in self.game.staff:
                total_xp = 0
                for dish in all_dishes:
                    xp_gain = dish.get_xp_reward(staff.skill_level)
                    total_xp += xp_gain
                
                leveled_up = staff.gain_xp(total_xp, "cooking")
                if leveled_up:
                    self.game.log_event(f"🎉 {staff.name} leveled up to {staff.skill_level}!")
            
            # Apply role bonuses
            for staff in self.game.staff:
                role_bonus = staff.get_role_bonus()
                if "recipe_quality" in role_bonus:
                    profit += int(order['total_value'] * role_bonus["recipe_quality"])
                if "customer_satisfaction" in role_bonus:
                    rating_gain += int(role_bonus["customer_satisfaction"] * 10)
            
            # Generate customer review
            service_quality = min(5, max(1, int(avg_staff_skill / 2) + random.randint(-1, 1)))
            food_quality = min(5, max(1, int(avg_staff_skill / 2) + random.randint(-1, 1)))
            review = self.game.generate_customer_review(True, food_quality, service_quality)
            self.game.customer_reviews.append(review)
            
            # Add tip to profit
            profit += review.tip_amount
            
            # Generate order description
            dish_names = [dish.name for dish in order['dishes']]
            drink_names = [drink.name for drink in order['drinks']]
            dessert_names = [dessert.name for dessert in order['desserts']]
            
            order_desc = []
            if dish_names:
                order_desc.append(f"🍽️ {', '.join(dish_names)}")
            if drink_names:
                order_desc.append(f"🥤 {', '.join(drink_names)}")
            if dessert_names:
                order_desc.append(f"🍰 {', '.join(dessert_names)}")
            
            message = f"✅ Customer ordered: {' | '.join(order_desc)} - Revenue: ${revenue}, Profit: ${profit} (Tip: ${review.tip_amount})"
            
            return {
                'success': True,
                'revenue': profit,  # Return profit instead of revenue
                'rating_gain': rating_gain,
                'message': message
            }
        else:
            # Failed order
            return {
                'success': False,
                'revenue': 0,
                'rating_gain': -2,
                'message': f"❌ Failed to prepare order - customer left disappointed"
            }
    
    def trigger_random_event(self, event_category=None):
        """Trigger a random event, optionally filtered by category"""
        available_events = []
        
        for event_id, event in self.game.events.items():
            # Filter by category if specified
            if event_category is None or event.category == event_category:
                available_events.append((event_id, event))
        
        if not available_events:
            return
        
        # Trigger events based on probability
        for event_id, event in available_events:
            if random.random() < event.probability:
                self.game.log_event(f"🎭 {event.name}: {event.description}")
                
                # Show event choices to player
                if event.choices:
                    print(f"\n🎭 EVENT: {event.name}")
                    print(f"   {event.description}")
                    print("\nChoose your response:")
                    
                    for i, choice in enumerate(event.choices, 1):
                        print(f"   {i}. {choice['text']}")
                    
                    try:
                        choice_num = int(input("\nEnter your choice (1-{}): ".format(len(event.choices))))
                        if 1 <= choice_num <= len(event.choices):
                            choice = event.choices[choice_num - 1]
                            effects = choice.get('effects', {})
                            
                            # Apply effects
                            for effect, value in effects.items():
                                if effect == 'money':
                                    if value > 0:
                                        self.game.earn_money(value)
                                    else:
                                        self.game.spend_money(abs(value))
                                elif effect == 'rating':
                                    self.game.rating += value
                                elif effect == 'satisfaction':
                                    for staff in self.game.staff:
                                        staff.satisfaction += value
                                elif effect == 'staff_stress':
                                    for staff in self.game.staff:
                                        staff.stress += value
                                elif effect == 'stress':
                                    self.game.stress += value
                            
                            self.game.log_event(f"   → Chose: {choice['text']}")
                        else:
                            self.game.log_event("   → No choice made - random outcome")
                    except ValueError:
                        self.game.log_event("   → Invalid choice - random outcome")
                
                break
    
    def view_kitchen(self):
        """View kitchen management"""
        while True:
            self.ui.render_kitchen_screen()
            choice = input().strip()
            
            if choice == '1':
                self.view_staff()
            elif choice == '2':
                self.view_inventory()
            elif choice == '3':
                self.game.log_event("🔧 Equipment maintenance completed")
                self.game.spend_money(50)
            elif choice == '4':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def view_staff(self):
        """View staff management"""
        while True:
            self.ui.render_staff_screen()
            choice = input().strip()
            
            if choice == '1':
                self.train_staff_menu()
            elif choice == '2':
                self.promote_staff()
            elif choice == '3':
                self.give_pay_raise()
            elif choice == '4':
                self.hire_new_staff()
            elif choice == '5':
                self.fire_staff()
            elif choice == '6':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def train_staff_menu(self):
        """Show training menu"""
        self.ui.render_staff_training_screen()
        try:
            user_input = input().strip()
            if not user_input:
                print("No input provided!")
                time.sleep(1)
                return
            
            parts = user_input.split()
            if len(parts) != 2:
                print("Invalid input format! Use: staff_number training_type")
                time.sleep(1)
                return
            
            staff_num, training_type = map(int, parts)
            if 1 <= staff_num <= len(self.game.staff) and 1 <= training_type <= 3:
                training_types = {1: "basic", 2: "advanced", 3: "expert"}
                if self.game.train_staff(staff_num - 1, training_types[training_type]):
                    print("Training completed successfully!")
                else:
                    print("Cannot afford training!")
            else:
                print("Invalid staff number or training type!")
        except ValueError:
            print("Invalid input format! Use: staff_number training_type")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)
    
    def hire_new_staff(self):
        """Hire new staff member"""
        if not self.game.can_hire_staff():
            print("Cannot hire more staff - venue at capacity!")
            time.sleep(2)
            return
        
        cost = self.game.get_staff_hire_cost()
        if not self.game.can_afford(cost):
            print(f"Cannot afford to hire staff (${cost})!")
            time.sleep(2)
            return
        
        # Generate random staff name and role
        names = ["Alex", "Sam", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Quinn"]
        roles = ["chef", "server", "prep_cook", "dishwasher"]
        
        name = random.choice(names)
        role = random.choice(roles)
        
        if self.game.hire_staff(name, role):
            self.game.spend_money(cost)
            print(f"Hired {name} as {role} for ${cost}")
        else:
            print("Failed to hire staff!")
        
        time.sleep(2)
    
    def promote_staff(self):
        """Promote staff"""
        self.ui.render_staff_promotion_screen()
        try:
            staff_num = int(input())
            promotable_staff = [staff for staff in self.game.staff if staff.can_be_promoted()]
            if 1 <= staff_num <= len(promotable_staff):
                if self.game.promote_staff(self.game.staff.index(promotable_staff[staff_num - 1])):
                    print("Promotion successful!")
                else:
                    print("Cannot afford promotion!")
            else:
                print("Invalid staff number!")
        except ValueError:
            print("Invalid input!")
        time.sleep(2)
    
    def give_pay_raise(self):
        """Give staff member a pay raise"""
        if not self.game.staff:
            print("No staff to give pay raise to!")
            time.sleep(2)
            return
        
        print("Select staff to give pay raise:")
        for i, staff in enumerate(self.game.staff, 1):
            raise_cost = staff.get_pay_raise_cost()
            print(f"{i}. {staff.name} ({staff.role}) - Current: ${staff.salary}, Raise: ${raise_cost}")
        
        try:
            staff_num = int(input("Enter staff number: "))
            if 1 <= staff_num <= len(self.game.staff):
                if self.game.give_staff_pay_raise(staff_num - 1):
                    print("Pay raise successful!")
                else:
                    print("Cannot afford pay raise!")
            else:
                print("Invalid staff number!")
        except ValueError:
            print("Invalid input!")
        time.sleep(2)
    
    def fire_staff(self):
        """Fire staff"""
        if len(self.game.staff) <= 1:
            print("Cannot fire last staff member!")
            time.sleep(2)
            return
        
        print("Select staff to fire:")
        for i, staff in enumerate(self.game.staff, 1):
            print(f"{i}. {staff.name} ({staff.role})")
        
        try:
            staff_num = int(input("Enter staff number: "))
            if 1 <= staff_num <= len(self.game.staff):
                fired_staff = self.game.staff.pop(staff_num - 1)
                self.game.log_event(f"👋 Fired {fired_staff.name}")
                print(f"Fired {fired_staff.name}")
            else:
                print("Invalid staff number!")
        except ValueError:
            print("Invalid input!")
        time.sleep(2)
    
    def view_recipes(self):
        """View recipes"""
        while True:
            self.ui.render_recipes_screen()
            choice = input().strip()
            
            if choice == '1':
                # Show recipe details
                if self.game.unlocked_recipes:
                    recipe_id = self.game.unlocked_recipes[0]
                    recipe = self.game.recipes[recipe_id]
                    self.game.log_event(f"📖 {recipe.name}: {recipe.description}")
            elif choice == '2':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def view_inventory(self):
        """View inventory"""
        while True:
            self.ui.render_inventory_screen()
            choice = input().strip()
            
            if choice == '1':
                # Buy ingredients
                if self.game.ingredients:
                    ingredient_id = random.choice(list(self.game.ingredients.keys()))
                    ingredient = self.game.ingredients[ingredient_id]
                    cost = int(ingredient.base_cost * 5) # Buy 5 units
                    if self.game.can_afford(cost):
                        if self.game.buy_ingredients(ingredient_id, 5):
                            pass  # Success message already logged
                        else:
                            self.game.log_event("❌ Failed to buy ingredients")
                    else:
                        self.game.log_event("❌ Cannot afford to buy ingredients")
                else:
                    self.game.log_event("❌ No ingredients available")
            elif choice == '2':
                # Restock all
                cost = len(self.game.ingredients) * 5
                if self.game.can_afford(cost):
                    self.game.restock_inventory()
                    self.game.spend_money(cost)
                    self.game.log_event("📦 Inventory restocked")
                else:
                    self.game.log_event("❌ Cannot afford restocking")
            elif choice == '3':
                # Show all items
                for ingredient_id, amount in self.game.inventory.items():
                    ingredient = self.game.ingredients[ingredient_id]
                    self.game.log_event(f"📦 {ingredient.name}: {amount}")
            elif choice == '4':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def view_venues(self):
        """View venues"""
        while True:
            self.ui.render_venues_screen()
            choice = input().strip()
            
            if choice == '1':
                # Purchase venue
                available_venues = [v for v in self.game.venues.values() if v.id not in self.game.venues_owned]
                if available_venues:
                    venue = available_venues[0]
                    if self.game.can_afford(venue.purchase_cost):
                        self.game.spend_money(venue.purchase_cost)
                        self.game.venues_owned.append(venue.id)
                        self.game.log_event(f"🏢 Purchased {venue.name}")
                    else:
                        self.game.log_event("❌ Cannot afford venue")
            elif choice == '2':
                # Switch venue
                if len(self.game.venues_owned) > 1:
                    self.game.current_venue = self.game.venues_owned[1]
                    venue = self.game.get_venue()
                    self.game.log_event(f"🏢 Switched to {venue.name}")
                    
                    # Enforce staff capacity for new venue
                    if self.game.enforce_staff_capacity():
                        self.game.log_event(f"⚠️ Staff capacity adjusted for {venue.name}")
            elif choice == '3':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def view_loans(self):
        """View loans"""
        while True:
            self.ui.render_loans_screen()
            choice = input().strip()
            
            if choice == '1':
                # Apply for loan
                available_loans = list(self.game.loans_available.values())
                if available_loans:
                    loan = available_loans[0]
                    self.game.money += loan.amount
                    self.game.loans.append({
                        'id': loan.id,
                        'amount': loan.amount,
                        'interest_rate': loan.interest_rate,
                        'term_months': loan.term_months,
                        'monthly_payment': loan.amount * loan.interest_rate / 12
                    })
                    self.game.log_event(f"🏦 Approved loan: {loan.name}")
            elif choice == '2':
                # Show current loans
                for loan in self.game.loans:
                    self.game.log_event(f"🏦 Loan: ${loan['amount']:,} - ${loan['monthly_payment']:.0f}/month")
            elif choice == '3':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def view_activities(self):
        """View after-hours activities"""
        while True:
            self.ui.render_activities_screen()
            choice = input().strip()
            
            if choice == '1':
                # Choose activity
                available_activities = list(self.game.activities.values())
                if available_activities:
                    activity = available_activities[0]
                    if self.game.can_afford(activity.cost):
                        self.game.spend_money(activity.cost)
                        self.game.log_event(f"🎯 Completed: {activity.name}")
                        
                        # Apply effects
                        for effect, value in activity.effects.items():
                            if effect == 'stress_reduction':
                                self.game.stress = max(0, self.game.stress - value)
                            elif effect == 'reputation':
                                self.game.rating += value
                        
                        # Track habit progress
                        habit_name = activity.habit_bonus.get('name', '')
                        if habit_name:
                            current_count = self.game.habits.get(habit_name, 0) + 1
                            self.game.habits[habit_name] = current_count
                            requirement = activity.habit_bonus.get('requirement', 10)
                            
                            if current_count >= requirement:
                                self.game.log_event(f"🏆 Habit unlocked: {habit_name}!")
                            else:
                                self.game.log_event(f"📈 Habit progress: {habit_name} ({current_count}/{requirement})")
                    else:
                        self.game.log_event("❌ Cannot afford activity")
            elif choice == '2':
                # Trigger night events
                self.game.log_event("🌙 Night events check...")
                night_events_triggered = 0
                max_night_events = 3
                
                for event_id, event in self.game.events.items():
                    if event.category == "night" and random.random() < event.probability:
                        if night_events_triggered < max_night_events:
                            self.trigger_random_event("night")
                            night_events_triggered += 1
                        else:
                            break
                
                if night_events_triggered == 0:
                    self.game.log_event("🌙 Quiet night - no events occurred")
            elif choice == '3':
                # Show all activities
                for activity in self.game.activities.values():
                    self.game.log_event(f"🎯 {activity.name}: ${activity.cost}")
            elif choice == '4':
                # Show habit progress
                if self.game.habits:
                    self.game.log_event("🏆 Current Habits:")
                    for habit_name, count in self.game.habits.items():
                        self.game.log_event(f"   {habit_name}: {count} times")
                else:
                    self.game.log_event("🏆 No habits formed yet")
            elif choice == '5':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def save_game(self):
        """Save the game"""
        if self.game.save_game():
            print("Game saved successfully!")
        else:
            print("Failed to save game!")
        time.sleep(2)
    
    def load_game(self):
        """Load the game"""
        if self.game.has_save_file():
            if self.game.load_game():
                print("Game loaded successfully!")
            else:
                print("Failed to load game!")
        else:
            print("No save file found!")
        time.sleep(2)
    
    def view_reviews(self):
        """View customer reviews"""
        while True:
            clear_screen()
            print("=" * 80)
            print("📝 CUSTOMER REVIEWS".center(80))
            print("=" * 80)
            
            if not self.game.customer_reviews:
                print("No customer reviews yet!")
                print("\nPress Enter to continue...")
                input()
                break
            
            # Show recent reviews
            recent_reviews = self.game.customer_reviews[-10:]  # Last 10 reviews
            for i, review in enumerate(recent_reviews, 1):
                stars = "⭐" * review.rating
                print(f"\n{i}. {stars} ({review.rating}/5)")
                print(f"   Food: {'🍽️' * review.food_quality} Service: {'👨‍💼' * review.service_quality}")
                print(f"   Atmosphere: {'🏠' * review.atmosphere} Value: {'💰' * review.value_for_money}")
                print(f"   Tip: ${review.tip_amount}")
                print(f"   \"{review.comment}\"")
            
            # Calculate average ratings
            if self.game.customer_reviews:
                avg_rating = sum(r.rating for r in self.game.customer_reviews) / len(self.game.customer_reviews)
                avg_food = sum(r.food_quality for r in self.game.customer_reviews) / len(self.game.customer_reviews)
                avg_service = sum(r.service_quality for r in self.game.customer_reviews) / len(self.game.customer_reviews)
                total_tips = sum(r.tip_amount for r in self.game.customer_reviews)
                
                print(f"\n📊 AVERAGE RATINGS:")
                print(f"   Overall: {avg_rating:.1f}/5")
                print(f"   Food: {avg_food:.1f}/5")
                print(f"   Service: {avg_service:.1f}/5")
                print(f"   Total Tips: ${total_tips}")
            
            print("\n1. Back to Main Menu")
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
    
    def run(self):
        """Main game loop"""
        print("Welcome to Restaurant Roguelike!")
        print("Loading game...")
        time.sleep(1)
        
        # Check for existing save file
        if self.game.has_save_file():
            print("Save file found! Would you like to load it? (y/n): ", end="")
            choice = input().strip().lower()
            if choice == 'y':
                self.game.load_game()
        
        while not self.game.game_over:
            self.ui.render_main_screen()
            choice = input().strip()
            
            if choice == '1':
                self.start_service_hours()
            elif choice == '2':
                self.view_kitchen()
            elif choice == '3':
                self.view_staff()
            elif choice == '4':
                self.view_recipes()
            elif choice == '5':
                self.view_inventory()
            elif choice == '6':
                self.view_venues()
            elif choice == '7':
                self.view_loans()
            elif choice == '8':
                self.view_activities()
            elif choice == '9':
                self.view_reviews()
            elif choice == '0':
                self.save_game()
            elif choice.lower() == 'q':
                print("Thanks for playing!")
                break
            else:
                print("Invalid choice!")
                time.sleep(1)
        
        if self.game.game_over:
            print(f"\n💀 GAME OVER: {self.game.game_over_reason}")
            print("Thanks for playing!")

if __name__ == "__main__":
    game = RestaurantGame()
    game.run() 