import openai
import requests
import logging
import time
from constants import OPENAI_API_KEY, SYSTEM_PROMPT, USER_PROMPT, JSON_TEMPLATE

class OpenAIClient:
    def __init__(self, api_key):
        start_time = time.time()
        if not api_key:
            raise ValueError("OpenAI API key is not set.")
        self.api_key = api_key
        self.client = openai.Client(api_key=self.api_key)
        
        logging.info(f"Initialized OpenAIClient in {time.time() - start_time:.2f} seconds.")


    def extract_resume_info(self, resume_text):
        start_time = time.time()
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{USER_PROMPT}\n{JSON_TEMPLATE}\n{resume_text}\nPlease respond in valid JSON format."}
            ]
        }

        response = requests.post(url, headers=headers, json=data, verify=False)
        logging.info(f"Extracted resume info in {time.time() - start_time:.2f} seconds.")
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else None

    # def extract_resume_info(self, system_prompt, user_prompt, json_template, resume_text):
    #     start_time = time.time()
    #     url = "https://api.openai.com/v1/chat/completions"
    #     headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
    #     data = {
    #         "model": "gpt-3.5-turbo",
    #         "messages": [
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": f"{user_prompt}\n{json_template}\n{resume_text}\nPlease respond in valid JSON format."}
    #         ]
    #     }

    #     response = requests.post(url, headers=headers, json=data, verify=False)
    #     logging.info(f"Extracted resume info in {time.time() - start_time:.2f} seconds.")
    #     return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else None

    def call_gpt4o(self, base64_image):
        start_time = time.time()
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": f"{USER_PROMPT}\n{JSON_TEMPLATE}\nPlease respond in valid JSON format."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=4096
        )
        logging.info(f"Called GPT-4o in {time.time() - start_time:.2f} seconds.")
        return response.choices[0].message.content
