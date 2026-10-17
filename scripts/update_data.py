import os
import json
import shutil
from datetime import datetime

LOG_DIR = "logs"
LATEST_LOG = os.path.join(LOG_DIR, "latest_rules.json")
PREVIOUS_LOG = os.path.join(LOG_DIR, "previous_rules.json")
OUTPUT_RULES = "marketplace_rules.json"

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def build_marketplace_metrics():
    """
    平台全指标基准库（涵盖 Amazon FBA 与 TikTok Shop 在美区、欧区、英区的全量类目与费率参数）
    未来接入各大平台爬虫或官方公告数据源时，在此函数内解析并更新即可
    """
    return {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "active",
        "platforms": {
            "TTS": {
                "name": "TikTok Shop",
                "regions": {
                    "US": {
                        "currency": "USD",
                        "symbol": "$",
                        "vat_rate": 0.0,
                        "tariff_rate": 7.5,
                        "inbound_placement": 0.0,
                        "storage_fee": 0.25,
                        "return_rate": 5.0,
                        "default_fulfillment": 4.50,
                        "categories": {
                            "Standard / General (常规通用类目)": 6.0,
                            "New Seller Promo (新店特惠/优惠期)": 3.0,
                            "Consumer Electronics (3C数码)": 5.0,
                            "Fashion & Apparel (服饰箱包)": 6.0,
                            "Beauty & Personal Care (美妆个护)": 6.0
                        }
                    },
                    "EU": {
                        "currency": "EUR",
                        "symbol": "€",
                        "vat_rate": 19.0,
                        "tariff_rate": 4.5,
                        "inbound_placement": 0.0,
                        "storage_fee": 0.30,
                        "return_rate": 4.0,
                        "default_fulfillment": 4.80,
                        "categories": {
                            "Standard / General (常规通用类目)": 6.0,
                            "New Seller Promo (新店特惠期)": 3.0,
                            "Consumer Electronics (3C数码)": 5.0,
                            "Fashion & Apparel (服饰箱包)": 6.0
                        }
                    },
                    "UK": {
                        "currency": "GBP",
                        "symbol": "£",
                        "vat_rate": 20.0,
                        "tariff_rate": 4.0,
                        "inbound_placement": 0.0,
                        "storage_fee": 0.25,
                        "return_rate": 4.0,
                        "default_fulfillment": 3.60,
                        "categories": {
                            "Standard / General (英区常规通用)": 5.0,
                            "New Seller Promo (新手扶持期)": 2.5,
                            "Consumer Electronics (3C数码)": 5.0,
                            "Fashion & Apparel (服饰箱包)": 5.0
                        }
                    }
                }
            },
            "AMZ": {
                "name": "Amazon FBA",
                "regions": {
                    "US": {
                        "currency": "USD",
                        "symbol": "$",
                        "vat_rate": 0.0,
                        "tariff_rate": 7.5,
                        "inbound_placement": 0.34,  # 2024起美区亚马逊分仓配置费
                        "storage_fee": 0.35,
                        "return_rate": 4.0,
                        "default_fulfillment": 5.80,
                        "categories": {
                            "Home & Kitchen (家居厨具)": 15.0,
                            "Consumer Electronics (消费数码)": 8.0,
                            "Automotive & Tools (汽配与工具)": 12.0,
                            "Clothing & Apparel (服饰大类 >$20)": 17.0,
                            "Clothing & Apparel (低客单服饰 <=$15)": 5.0,
                            "Sports & Outdoors (户外运动)": 15.0,
                            "Beauty & Personal Care (美妆个护)": 15.0,
                            "General / Other (其它常规类目)": 15.0
                        }
                    },
                    "EU": {
                        "currency": "EUR",
                        "symbol": "€",
                        "vat_rate": 19.0,
                        "tariff_rate": 4.5,
                        "inbound_placement": 0.0,
                        "storage_fee": 0.40,
                        "return_rate": 4.0,
                        "default_fulfillment": 5.20,
                        "categories": {
                            "Home & Kitchen (家居厨具)": 15.0,
                            "Consumer Electronics (消费电子)": 7.0,
                            "Automotive (汽车用品)": 15.0,
                            "Clothing & Accessories (服装配件)": 15.0,
                            "General / Other (常规通用类目)": 15.0
                        }
                    },
                    "UK": {
                        "currency": "GBP",
                        "symbol": "£",
                        "vat_rate": 20.0,
                        "tariff_rate": 4.0,
                        "inbound_placement": 0.0,
                        "storage_fee": 0.35,
                        "return_rate": 4.0,
                        "default_fulfillment": 3.80,
                        "categories": {
                            "Home & Kitchen (家居厨具)": 15.3,
                            "Consumer Electronics (消费电子)": 7.14,
                            "Automotive (汽车用品)": 15.3,
                            "Clothing & Accessories (服装服饰)": 15.3,
                            "General / Other (常规通用类目)": 15.3
                        }
                    }
                }
            }
        }
    }

def rotate_and_save_logs(new_data):
    ensure_log_dir()
    if os.path.exists(LATEST_LOG):
        shutil.copyfile(LATEST_LOG, PREVIOUS_LOG)
        print(f"[Backup] Archived previous rules to {PREVIOUS_LOG}")
    
    with open(LATEST_LOG, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print(f"[Success] Written latest rules snapshot to {LATEST_LOG}")

    # 同时写出供前端 index.html 实时请求使用的全局规则配置
    with open(OUTPUT_RULES, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print(f"[Success] Published {OUTPUT_RULES} for frontend access.")

def main():
    metrics = build_marketplace_metrics()
    rotate_and_save_logs(metrics)

if __name__ == "__main__":
    main()
