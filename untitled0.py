# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IIHh57rQbI8yfHFfTqpFAF3LYFjIiE1A
"""

import json
import openai
import joblib  # To load a pre-trained machine learning model

# Set your OpenAI API key
client = openai.OpenAI(api_key="sk-your-api-key-here")

# Load a pre-trained air quality prediction model (you can replace this with your actual model)
# For this example, let's assume we're loading a RandomForest model
air_quality_model = joblib.load("path_to_air_quality_model.pkl")

# Function to predict air quality based on environmental data (e.g., temperature, humidity, pollutant levels)
def predict_air_quality(temperature, humidity, pm25, pm10):
    # Create a feature array from the inputs
    features = [[temperature, humidity, pm25, pm10]]  # Example features: temperature, humidity, PM2.5, PM10

    # Use the loaded model to predict air quality
    prediction = air_quality_model.predict(features)

    # Assuming prediction is in numerical form (e.g., 1 = good, 2 = moderate, 3 = unhealthy)
    air_quality = {1: "Good", 2: "Moderate", 3: "Unhealthy"}.get(prediction[0], "Unknown")

    return air_quality

# Chat function with GPT and function calling
def chat_with_gpt(message, history):
    messages = [{"role": "system", "content": "You are a helpful assistant providing air quality predictions."}]

    # Include conversation history
    for user_msg, bot_reply in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_reply})

    # Add the new user message
    messages.append({"role": "user", "content": message})

    # Chat completion request to GPT model
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        functions=[{
            "name": "predict_air_quality",
            "description": "Predict air quality based on environmental data",
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number", "description": "Temperature in Celsius"},
                    "humidity": {"type": "number", "description": "Humidity percentage"},
                    "pm25": {"type": "number", "description": "PM2.5 concentration"},
                    "pm10": {"type": "number", "description": "PM10 concentration"}
                },
                "required": ["temperature", "humidity", "pm25", "pm10"]
            }
        }],
        function_call="auto"
    )

    msg = response.choices[0].message

    # If the model wants to call the function
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        temperature = args.get("temperature", 0)
        humidity = args.get("humidity", 0)
        pm25 = args.get("pm25", 0)
        pm10 = args.get("pm10", 0)

        # Call the air quality prediction function
        result = predict_air_quality(temperature, humidity, pm25, pm10)
        history.append((message, f"The predicted air quality is: {result}"))
        return "", history
    else:
        bot_reply = msg.content
        history.append((message, bot_reply))
        return "", history

# Launch Gradio app
with gr.Blocks() as demo:
    gr.Markdown("## Air Quality Prediction Chatbot")

    # Create a chatbot interface
    chatbot = gr.Chatbot()

    # Input fields for temperature, humidity, PM2.5, and PM10
    msg = gr.Textbox(label="Ask about air quality (e.g., 'What is the air quality today?')")
    state = gr.State([])

    # Trigger the chatbot function
    msg.submit(chat_with_gpt, [msg, state], [msg, chatbot, state])

# Launch the app
demo.launch()