import os
from dotenv import load_dotenv
import yaml
from groq import Groq

load_dotenv()

for key in ["GROQ_API_KEY", "NOTION_TOKEN", "NOTION_DATABASE_ID"]:
    print(key, "OK" if os.getenv(key) else "MANQUANTE")

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)
print("Config chargée :", config["llm"]["model"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model=config["llm"]["model"],
    messages=[{"role": "user", "content": "Say hello in one short sentence."}],
    max_tokens=500,
    reasoning_effort=config["llm"]["reasoning_effort"],
)
print("Réponse Groq :", response.choices[0].message.content)