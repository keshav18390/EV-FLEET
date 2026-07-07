import json
import sys
from app.core.config import settings
from app.core.llm import call_llm

print("Settings LLM_PROVIDER:", settings.LLM_PROVIDER)
key = settings.active_api_key
if not key:
    print(json.dumps({"has_key": False, "masked_key": None}))
    sys.exit(0)
masked = key[:6] + "..." + key[-4:] if len(key) > 12 else "***"
print(json.dumps({"has_key": True, "masked_key": masked}))

print("Calling LLM with a short test prompt...")
res = call_llm("Say hello in one word.")
print(json.dumps({"success": res.success, "text": res.text, "error_code": res.error_code}))
