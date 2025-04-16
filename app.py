
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

    prompt = f"""You are a helpful audio-visual sales assistant.
A customer said: "{query}"

Here are the matching products:
{chr(10).join([f"- {p['name']} (SKU: {p['sku']}) – R{p['price']}" for p in results])}

Generate a friendly, professional quote recommendation using the product options above.
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
