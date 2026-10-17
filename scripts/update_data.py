import os
import re
import urllib.request
import json

def fetch_exchange_rates():
    url = "https://open.er-api.com/v6/latest/CNY"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            rates = data.get("rates", {})
            # 汇率换算：1 USD/EUR/GBP = X CNY
            usd_rate = round(1 / rates.get("USD", 0.138), 2) if rates.get("USD") else 7.25
            eur_rate = round(1 / rates.get("EUR", 0.128), 2) if rates.get("EUR") else 7.82
            gbp_rate = round(1 / rates.get("GBP", 0.109), 2) if rates.get("GBP") else 9.15
            return {"USD": usd_rate, "EUR": eur_rate, "GBP": gbp_rate}
    except Exception as e:
        print(f"Fetch failed: {e}")
        return None

def update_index_html():
    file_path = "index.html"
    if not os.path.exists(file_path):
        print("index.html not found!")
        return

    rates = fetch_exchange_rates()
    if not rates:
        print("Using fallback rates; skipping file update.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配并替换 JavaScript 中的默认硬编码保底汇率对象
    pattern = r"const\s+fxState\s*=\s*\{\s*rates:\s*\{[^}]*\}\s*,\s*base:\s*'CNY'\s*\};"
    replacement = f"const fxState = {{ rates: {{ USD: {rates['USD']}, EUR: {rates['EUR']}, GBP: {rates['GBP']} }}, base: 'CNY' }};"

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully updated fxState to: {rates}")
    else:
        print("Rates already up-to-date or pattern matched without change.")

if __name__ == "__main__":
    update_index_html()
