
import json
import os
from typing import Dict

def load_config() -> Dict:
    config_path = os.path.join('data', 'config.json')
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(config: Dict) -> None:
    os.makedirs('data', exist_ok=True)
    with open(os.path.join('data', 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
