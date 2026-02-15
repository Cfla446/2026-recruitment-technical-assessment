from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = recipeName.replace("_", " ").replace("-", " ")
	recipeName = "".join(char for char in recipeName if char.isalpha() or char.isspace())
	words = recipeName.strip().split()

	if not words:
		return None
	
	return " ".join(word.capitalize() for word in words)

# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	# Create and add more entries to cookbook
	# Implement endpoint and store the cookbook entries. if successful, return HTTP 200 and empty response body

	data = request.get_json()

	type = data.get('type')
	name = data.get('name')

	if name in cookbook:
		return 'Error: entry already exists! (entry names must be unique)', 400
	
	if type == 'recipe':
		visited_items = set() # set as by storing strings instead of obj, that way can check for duplicate strings
		approved_items = [] # list as final required_items is type List

		items = data.get('requiredItems', [])

		for item in items:
			item_name = item.get('name')
			item_quantity = item.get('quantity')

			if item_name in visited_items:
				return 'Error: duplicated required item in recipe!', 400
			
			visited_items.add(item_name)
			approved_items.append(RequiredItem(name = item_name, quantity = item_quantity))
		
		new_entry = Recipe(name = name, required_items = approved_items)
	elif type == 'ingredient':
		cook_time = data.get('cookTime')
		
		if cook_time < 0:
			return 'Error: invalid cook time! (cook time >= 0)', 400
		
		new_entry = Ingredient(name = name, cook_time = cook_time)
	else:
		return 'Error: invalid type! (not recipe or ingredient)', 400
	
	cookbook[name] = new_entry
	
	return jsonify({}), 200

# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	name = request.args.get('name')
	if name not in cookbook or not isinstance(cookbook[name], Recipe):
		return 'Error: name not found or is not a recipe!', 400
	
	# Recursion outer variables
	total_cook_time = 0
	final_ingredients_list = {}

	def resolve_item(name, frequency):
		nonlocal total_cook_time
		if name not in cookbook:
			raise ValueError("Missing item in cookbook") # stops recursion
		
		entry = cookbook[name]

		if isinstance(entry, Ingredient):
			total_cook_time += entry.cook_time * frequency
			final_ingredients_list[name] = final_ingredients_list.get(name, 0) + frequency

		elif isinstance(entry, Recipe):
			for item in entry.required_items:
				resolve_item(item.name, frequency * item.quantity)

	try: # for ValueError case
		recipe = cookbook[name]
		for fin_item in recipe.required_items:
			resolve_item(fin_item.name, fin_item.quantity)
	except ValueError:
		return 'Recipe contains unknown items', 400
	
	ingredients_list = [
		{"name": item_name, "quantity": item_quantity}
		for item_name, item_quantity in final_ingredients_list.items()
	]

	return jsonify({
		"name": name,
		"cookTime": total_cook_time,
		"ingredients": ingredients_list
	}), 200

# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
