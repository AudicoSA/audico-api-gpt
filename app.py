
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import openai
from difflib import get_close_matches

app = Flask(__name__)
CORS(app)

with open("products.json") as f:
    PRODUCTS = json.load(f)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/search_gpt")
def search_gpt():
    query = request.args.get("query", "").lower()
    results = []

    for product in PRODUCTS:
        name = product.get("name", "").lower()
        sku = product.get("sku", "").lower()
        if query in name or query in sku:
            results.append(product)

    if not results:
        names = [p["name"] for p in PRODUCTS]
        close_matches = get_close_matches(query, names, n=5, cutoff=0.3)
        results = [p for p in PRODUCTS if p["name"] in close_matches]

    prompt = f"""You are a senior AV system designer at Audico Online (https://www.audicoonline.co.za).
A client has requested: "{query}"

Your role is to:
- Understand the space and use case
- Select suitable products from the list below
- Use intelligent design logic when recommending systems
- If products are missing (e.g. speaker cable, mounts, zone control), mention what else is needed
- If the request is vague or lacks important information such as room size, number of zones, or speaker preference, ask follow-up questions before quoting
- Speak in a confident, helpful, and friendly tone
- Think like a designer, not a catalogue

Design logic and best practices:
- If 3 or more zones are mentioned, recommend a multi-zone audio controller
- In large spaces, include a subwoofer if one isn't mentioned
- For restaurants, bars, or cafés, suggest wide-dispersion ceiling speakers and a streaming amp
- If Bluetooth is requested, recommend a Yamaha WXA-50 or Denon CEOL N11
- For boardrooms, suggest ceiling microphones or sound reinforcement
- For multi-room or office setups, recommend matrix amps or wall volume controls

Available products:
{chr(10).join([f"- {p['name']} (SKU: {p['sku']}) – R{p['price']}" for p in results])}

Now, recommend a system OR ask clarifying questions if needed.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "system", "content": "You are a product quoting assistant." },
                { "role": "user", "content": prompt }
            ]
        )
        gpt_reply = response.choices[0].message.content
        return jsonify({ "reply": gpt_reply })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
