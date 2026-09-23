from openai import OpenAI

client = OpenAI(
    base_url='https://integrate.api.nvidia.com/v1',
    api_key='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'
)

candidates = [
    'meta/llama-3.2-11b-vision-instruct',
    'meta/llama-3.2-90b-vision-instruct',
    'mistralai/mistral-large-2-instruct',
    'mistralai/mistral-7b-instruct-v0.3',
    'deepseek-ai/deepseek-v4.1-flash',
    'nvidia/nemotron-4-340b-instruct',
    'mistralai/mixtral-8x22b-v0.1',
]

for model in candidates:
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'hi'}],
            max_tokens=10
        )
        print(f"SUCCESS: {model} -> {res.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"FAILED: {model} -> {e}")
