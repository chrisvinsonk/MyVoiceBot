import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Dictionary of models with their URLs and parameters
MODELS = {
    "google/flan-t5-small": {
        "url": "https://api-inference.huggingface.co/models/google/flan-t5-small",
        "max_length": 150,
        "temperature": 0.7
    },
    "google/flan-t5-xl": {
        "url": "https://api-inference.huggingface.co/models/google/flan-t5-xl",
        "max_length": 200,
        "temperature": 0.8
    },
    "google/mt5-large": {
        "url": "https://api-inference.huggingface.co/models/google/mt5-large",
        "max_length": 180,
        "temperature": 0.75
    }
}

def get_bot_response(user_input, model="google/flan-t5-small"):
    """
    Get response from Hugging Face API based on user input.
    
    Args:
        user_input (str): The user's input/query
        model (str): The model to use for generating a response
        
    Returns:
        str: The bot's response
    """
    try:
        # Get model configuration
        model_config = MODELS.get(model, MODELS["google/flan-t5-small"])
        chat_url = model_config["url"]
        max_length = model_config["max_length"]
        temperature = model_config["temperature"]
        
        # Prepare a more conversational prompt for better responses
        # The improved prompt engineering is key to getting better responses
        prompt = f"""
        You are a helpful, friendly, and knowledgeable assistant.
        
        User: {user_input}
        
        Assistant:
        """
        
        # Call the Hugging Face API with improved parameters
        response = requests.post(
            chat_url, 
            headers=HEADERS, 
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 50,
                    "repetition_penalty": 1.2,
                    "do_sample": True
                }
            }
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            # Extract the generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0]['generated_text'].strip()
                
                # Clean up the response
                if generated_text.startswith("Assistant:"):
                    generated_text = generated_text[len("Assistant:"):].strip()
                
                # If the response is too short, try to improve it
                if len(generated_text) < 20:
                    return enhance_short_response(user_input, generated_text)
                    
                return generated_text
            else:
                generated_text = result.get('generated_text', "I'm not sure how to respond to that.").strip()
                if generated_text.startswith("Assistant:"):
                    generated_text = generated_text[len("Assistant:"):].strip()
                return generated_text
        else:
            print(f"API Error: {response.status_code} - {response.text}")  # Debugging
            return "I'm having trouble thinking right now. Let's talk about something else."
    
    except Exception as e:
        print(f"Error in get_bot_response: {str(e)}")  # Debugging
        return f"I'm having trouble connecting right now. Please try again in a moment."

def enhance_short_response(user_input, original_response):
    """
    Try to enhance responses that are too short or low quality.
    
    Args:
        user_input (str): The original user input
        original_response (str): The short response to enhance
        
    Returns:
        str: An enhanced response
    """
    # If the original response is decent, return it
    if len(original_response) > 10 and not original_response.lower() in ["i don't know", "i'm not sure"]:
        return original_response
        
    # Otherwise, try a different approach with a more detailed prompt
    try:
        # Get model configuration for a larger model
        model_config = MODELS.get("google/flan-t5-xl", MODELS["google/flan-t5-small"])
        chat_url = model_config["url"]
        
        # More detailed prompt
        detailed_prompt = f"""
        You are a helpful assistant providing detailed, informative answers.
        Answer the following question thoroughly:
        
        Question: {user_input}
        
        Your detailed answer:
        """
        
        # Call the API with the enhanced prompt
        response = requests.post(
            chat_url, 
            headers=HEADERS, 
            json={
                "inputs": detailed_prompt,
                "parameters": {
                    "max_length": 250,
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "top_k": 50,
                    "repetition_penalty": 1.2,
                    "do_sample": True
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                enhanced_text = result[0]['generated_text'].strip()
                
                # Clean up the response
                for prefix in ["Your detailed answer:", "Answer:"]:
                    if enhanced_text.startswith(prefix):
                        enhanced_text = enhanced_text[len(prefix):].strip()
                
                return enhanced_text if len(enhanced_text) > len(original_response) else original_response
            else:
                return original_response
        else:
            return original_response
            
    except Exception:
        # If enhancement fails, return the original
        return original_response