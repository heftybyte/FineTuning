import numpy as np
import json
import os
from IPython.display import display
import pandas as pd
from openai import OpenAI
import itertools
import time
import base64
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import Any, Dict, List, Generator
import ast
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_SECRET_KEY'))

# messages = [
#     {
#         'role': "system",
#         'content': "You are a chatbot that only speaks pidgin English, no matter what language is spoken to you or what you are asked." },
#     {
#         'role': "user",
#         'content': "Why is the world unfair?",
#     },
# ]
pd.options.display.max_columns = 5
def get_chat_completion(messages:list[dict[str, str]], model = "gpt-4o-mini" ) -> str:
    params = {
        "model": model,
        "messages": messages,
        "max_tokens": 500, #The maximum number of tokens that can be generated in the chat completion.

    }
    completion = client.chat.completions.create(**params)
    return completion.choices[0].message, completion.usage


def eval(model:str, system_prompt:str, prompts_to_expected_language):
    """
    Evaluate the performance of a model in selecting the correct language based on given prompts.
    Args:
        model(str): The name of the model to be evaluated
        system_prompt: The system prompt to be used in the chat completion
        prompts_to_expected_language: A dictionary mapping prompts to expected language
    Returns:
        None
    """

    prompts_to_actual = []
    latencies = []
    tokens_used = []

    for prompt, expected_language in prompts_to_expected_language.items():
        messages = [
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": prompt }
        ]
        start_time = time.time()
        completion, usage = get_chat_completion(
            messages = messages,
            model = model,
        )
        end_time = time.time()

        #Calculate Latency
        latency = (end_time - start_time) * 1000 #Convert To Miliseconds

        latencies.append(latency)
        tokens_used.append(usage.total_tokens)
        prompts_to_actual.append({
            prompt: completion.content
        })
    total_prompts = len(prompts_to_expected_language)

    # Calculate average latency
    avg_latency = sum(latencies) / total_prompts

    # Calculate average tokens used
    avg_tokens_used = sum(tokens_used) / total_prompts

    results_df = pd.DataFrame(columns=["Prompt", "Expected", "Match"])

    # Calculate the number of matches
    matches = 0
    results_list = []
    for result in prompts_to_actual:
        prompt = list(result.keys())[0]
        actual_language = list(result.values())[0]
        expected_language = prompts_to_expected_language[prompt]
        match = actual_language == expected_language
        results_list.append(
            {
                "Prompt": prompt,
                "Actual": actual_language,
                "Expected": expected_language,
                "Match": "Yes" if match else "No",
            }
        )
        if actual_language == expected_language:
            matches += 1

    # Get percentage of matches
    match_percentage = (matches / total_prompts) * 100

    results_df = pd.DataFrame(results_list)

    results_df.to_json('non-finetuned-model-4omini.json')

    print(results_df)
    print(
        f"Number of matches: {matches} out of {total_prompts} ({match_percentage:.2f}%)"
    )
    print(f"Average latency per request: {avg_latency:.2f} ms")
    print(f"Average tokens used per request: {avg_tokens_used:.2f}")

SYSTEM_PROMPT = """You are an intelligent detector that can detect any language. Your job as a translator
is to make sense of any phrase given to you and return the correct language. For example if you are provided
with the phrase 'Estoy muy ocupado', you respond with the word 'Spanish', if the detected language is Nigerian Pidgin,
you are to return only one word 'Pidgin'. Your response must be one word except the language in question is in 
multiple words.In situations where the phrase you are given does not make sense, you are to return the word 'Gibberish'."""

languages = {
    "Yo quiero dinero": "Spanish",
    "Adannaya, kedu ka i mere": "Igbo",
    "aap kaise hain": "Hindi",
    "Quiero hshiuyu yuwb": "Gibberish",
    "भवान्‌ कथमसि": "Sanskrit",
    "Wetin dey happen, I wan comot": "Pidgin",
    "eu estou saindo": "Portuguese",
    "los estados unidos kedu?": "Gibberish",
    "Dɔ le wuyem, taflatse ɖa nu": "Ewe",
    "Market thlengin min zui rawh": "Mizo",
}

difficult_languages = {
    "Yo quiero where you dey go?": "Gibberish",
    "estados unidos ka i mere": "Gibberish",
    "aap ighotago": "Gibberish",
    "Quiero hshiuyu yuwb": "Gibberish",
    "भवान्‌ le wuyem, taflatse": "Gibberish",
    "Bia Adannaya, Kedu": "Igbo",
    "eu min zui rawh saindo": "Gibberish",
    "los estados unidos kedu?": "Gibberish",
    "Dɔ koshi danu ɖa nu": "Gibberish",
    "Market thlengin estou": "Gibberish",
}

eval(
    model="ft:gpt-4o-mini-2024-07-18:heftybyte:mini-language-detector:A0ZweJEi",
    system_prompt=SYSTEM_PROMPT,
    prompts_to_expected_language=difficult_languages
)

