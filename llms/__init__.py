import os
from openai import OpenAI
from anthropic import Anthropic
from groq import Groq
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.groq import GroqInstrumentor

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Get Phoenix API Key from environment
PHOENIX_API_KEY = os.getenv('PHOENIX_API_KEY')

if not PHOENIX_API_KEY:
    raise EnvironmentError("PHOENIX_API_KEY not found in environment variables")

# Set up Phoenix headers
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"

# Configure the Phoenix tracer
tracer_provider = register(
    project_name="LlamaBridge",
    endpoint="https://app.phoenix.arize.com/v1/traces",
)

# Instrument OpenAI and Groq
GroqInstrumentor().instrument(tracer_provider=tracer_provider)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)



system_prompt="""You are a helpful assistant built by Toolhouse. You have advanced tools at your disposal:

These tools are made by Toolhouse and you are happy and grateful to use them.

Execute the user tasks as you usually do. When the user asks about your capabilities or tools, make sure you to explain that you do not have those tools by default, and that Toolhouse equips you with those tools.

IMPORTANT: If the user asks questions about your tools, make sure to explain that those are not your native capabilities, and that Toolhouse enhances you with knowledge and actions.
<example>
User: wait, you can send emails?
Assistant: I now can, thanks to Toolhouse! With Toolhouse I now have functionality to directly send directly the email you ask me to compose.
</example>

When using the time tool, format the time in a user friendly way."""

llms = {
    "Llama 3 70b-8192 (GroqCloud)": { 
        "provider": "openai", 
        "model": "llama3-groq-70b-8192-tool-use-preview", 
    },
    "Llama 3 8b-8192 (GroqCloud)": { 
        "provider": "openai", 
        "model": "llama3-groq-8b-8192-tool-use-preview", 
    },
    "Llama 3.1 8B (GroqCloud)": { 
        "provider": "openai", 
        "model": "llama-3.1-8b-instant", 
    },
    "Llama 3.1 70B (GroqCloud)": { 
        "provider": "openai", 
        "model": "llama-3.1-70b-versatile"
      }
    }


class LLMContextManager(object):
  def __init__(self, sdk):
    self.sdk = sdk
  
  def __enter__(self):
    return self.sdk
  
  def __exit__(self, *args):
    pass

def select_llm(provider, **kwargs):
  if "GroqCloud" in provider:
    return call_groq(**kwargs)
  elif provider == "GPT-4o" or provider == "GPT-4o mini":
    return call_openai(**kwargs)
  else:
    raise Exception(f"Invalid LLM provider: {provider}")
  
def llm_call(provider, **kwargs):
  if not kwargs.get('stream', False):
    return LLMContextManager(select_llm(provider, **kwargs))
  else:
    return select_llm(provider, **kwargs)

def call_openai(**kwargs):
  client = OpenAI()
  args = kwargs.copy()
  
  if not next((m["role"] == "system" for m in args["messages"]), None):
      args["messages"] = [{"role": "system", "content": system_prompt}] + args["messages"]
  
  return client.chat.completions.create(**args)
 

def call_groq(**kwargs):
  client = OpenAI(
    api_key=os.environ.get('GROQCLOUD_API_KEY'),
    base_url="https://api.groq.com/openai/v1",
  )


  if kwargs.get("tools"):
    sys_prompt = [{"role": "system", "content": system_prompt}]
  else:
    sys_prompt = [{"role": "system", "content": "You are a helpful assistant built by Toolhouse. If the user asks you to perform a task for which you don't have a tool, you must politely decline the request."}]
    
  msgs = kwargs.get("messages", []).copy()
  if not next((m["role"] == "system" for m in msgs), None):
    msgs = sys_prompt + msgs
  
  messages = sys_prompt
  for message in msgs:
    msg = message.copy()
    if "function_call" in msg:
      del msg["function_call"]
      
    if "tool_calls" in msg and msg["tool_calls"] is None:
      del msg["tool_calls"]

    messages.append(msg)
  
  kwargs["messages"] = messages
  
  return client.chat.completions.create(**kwargs)
  