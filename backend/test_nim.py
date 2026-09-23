import time
from openai import OpenAI

client = OpenAI(
    base_url='https://integrate.api.nvidia.com/v1',
    api_key='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'
)

start = time.time()
completion = client.chat.completions.create(
    model='nvidia/llama-3.1-nemotron-70b-instruct',
    messages=[
        {'role': 'system', 'content': 'You extract structured JSON for pharma deviations.'},
        {'role': 'user', 'content': 'Extract JSON for: Metformin batch MFH260712A reported OOS temperature excursion at API Manufacturing Unit.'}
    ],
    temperature=0.1,
    max_tokens=250
)
duration = time.time() - start
print(f"Latency: {duration:.2f} seconds")
print("Response:\n", completion.choices[0].message.content)
