import os
import re
import urllib.request
import json
import shutil
from datetime import datetime

LOG_DIR = "logs"
LATEST_LOG = os.path.join(LOG_DIR, "latest_fx.json")
PREVIOUS_LOG = os.path.join(LOG_DIR, "previous_fx.json")
INDEX_PATH = "index.html"

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def fetch_live_rates():
    """从公共接口抓取最新实时汇率"""
    url = "https://open.er-api.com/v6/latest/CNY"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            rates = data.get("rates", {})
            usd = rates.get("USD")
            eur = rates.get("EUR")
            gbp = rates.get("GBP")

            # 严格有效性校验：防止空值或 0
            if not (usd and eur and gbp and usd > 0 and eur > 0 and gbp > 0):
                raise ValueError("Incomplete or zero currency rates received.")

            return {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "status": "success",
                "rates": {
                    "USD": round(1 / usd, 2),
                    "EUR": round(1 / eur, 2),
                    "GBP": round(1 / gbp, 2)
                }
            }
    except Exception as e:
        print(f"[Warning] Live fetch failed: {e}")
        return None

def rotate_and_save_logs(new_data):
    """滚动备份：若存在 latest，则将其归档为 previous，然后写入新 latest"""
    ensure_log_dir()
    if os.path.exists(LATEST_LOG):
        shutil.copyfile(LATEST_LOG, PREVIOUS_LOG)
        print(f"[Backup] Archived current latest to {PREVIOUS_LOG}")
    
    with open(LATEST_LOG, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print(f"[Success] Written latest snapshot to {LATEST_LOG}")

def get_fallback_rates():
    """容错回滚方案：优先读取 previous_fx.json，最后使用保底常量"""
    if os.path.exists(PREVIOUS_LOG):
        try:
            with open(PREVIOUS_LOG, "r", encoding="utf-8") as f:
                prev_data = json.load(f)
                print(f"[Rollback] Restoring rates from previous snapshot ({prev_data.get('timestamp')})")
                return prev_data.get("rates")
        except Exception as e:
            print(f"[Error] Failed to read previous log: {e}")
    
    print("[Fallback] Utilizing hardcoded base rates.")
    return {"USD": 7.25, "EUR": 7.82, "GBP": 9.15}

def apply_rates_to_html(rates):
    if not os.path.exists(INDEX_PATH):
        print(f"[Error] {INDEX_PATH} not found.")
        return False

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配并替换 JavaScript 中的默认保底汇率对象
    pattern = r"const\s+fxState\s*=\s*\{\s*rates:\s*\{[^}]*\}\s*\};"
    replacement = f"const fxState = {{ rates: {{ USD: {rates['USD']}, EUR: {rates['EUR']}, GBP: {rates['GBP']} }} }};"

    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[Updated] index.html synced with rates: {rates}")
        return True
    else:
        print("[No-op] index.html already matches target rates.")
        return False

def main():
    ensure_log_dir()
    fetched = fetch_live_rates()

    if fetched:
        target_rates = fetched["rates"]
        rotate_and_save_logs(fetched)
    else:
        # 抓取失败触发自动回滚
        target_rates = get_fallback_rates()

    apply_rates_to_html(target_rates)

if __name__ == "__main__":
    main()
