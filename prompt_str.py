from pydantic import BaseModel

class RecipeGeneration():
    @staticmethod
    def recipe_generation_prompt():
        return ("""I am sending you the products I have in my fridge. Please provide me with a recipe that I can cook 
            with these ingridients and the ones that you pick to fulfill the recipe. Describe the steps, having no more than 5.
            Also, provide me with the nutritional information of the dish per serving. 
        """)

class Ingredient(BaseModel):
    dish_name: str
    quantity: str
    mass: float

class Instruction(BaseModel):
    step: int
    step_title: str
    description: str

class Nutrients(BaseModel):
    calories: int
    proteins: float
    carbs: float
    sugars: float
    fats: float
    fiber: float

class Recipe(BaseModel):
    dish_title: str
    ingredients: list[Ingredient]
    instructions: list[Instruction]
    nutrients: Nutrients