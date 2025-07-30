import os
import json
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_cooking_instructions(recipe_name, user_ingredients, recipe_ingredients):
    """
    Get detailed AI-powered cooking instructions for a recipe
    """
    try:
        # Prepare the prompt for GPT-4o
        missing_ingredients = [ing for ing in recipe_ingredients if ing not in user_ingredients]
        
        prompt = f"""
        You are an experienced Indian mother who loves to cook and teach cooking. 
        A person wants to cook "{recipe_name}" and has these ingredients: {', '.join(user_ingredients)}.
        
        The complete recipe requires: {', '.join(recipe_ingredients)}.
        Missing ingredients: {', '.join(missing_ingredients) if missing_ingredients else 'None'}.
        
        Please provide:
        1. Step-by-step cooking instructions in a warm, motherly tone (like an Indian mom would explain)
        2. Practical substitution suggestions for missing ingredients
        3. Helpful cooking tips and tricks
        4. Cultural context or interesting facts about this dish
        5. Serving suggestions
        
        Keep the language natural and conversational, as if you're teaching your child to cook.
        Use Indian English style and include terms like "hing", "jeera", "haldi" naturally.
        
        Format your response as JSON with these keys:
        - "instructions": array of step-by-step cooking instructions
        - "substitutions": array of substitution suggestions for missing ingredients
        - "tips": array of helpful cooking tips
        - "cultural_context": string with interesting facts about the dish
        - "serving_suggestions": array of serving suggestions
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian cook and loving mother who explains recipes in a warm, conversational manner. Always respond with valid JSON in the specified format."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1500,
            temperature=0.7
        )
        
        # Parse the JSON response
        ai_response = json.loads(response.choices[0].message.content or "{}")
        
        return ai_response
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse AI response as JSON: {e}")
        return {
            "instructions": ["Sorry, I couldn't get proper cooking instructions right now. Please try again."],
            "substitutions": [],
            "tips": [],
            "cultural_context": "",
            "serving_suggestions": []
        }
    except Exception as e:
        logging.error(f"Error getting AI cooking instructions: {e}")
        return {
            "instructions": ["Sorry, I couldn't connect to get cooking instructions right now. Please try again later."],
            "substitutions": [],
            "tips": [],
            "cultural_context": "",
            "serving_suggestions": []
        }
