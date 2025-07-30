CLASSIFIER_JUDGE_PROMPT = """
    You will be provided with the following information:
    1. An arbitrary text sample. The sample is delimited with triple backticks.
    2. List of categories the text sample can be assigned to. The list is delimited with square brackets. The categories in the list are enclosed in the single quotes and comma separated. The text sample belongs to at least one category but cannot exceed {max_cats}.

    Perform the following tasks:
    1. Identify to which categories the provided text belongs to with the highest probability.
    2. Assign the text sample to at least 1 but up to {max_cats} categories based on the probabilities.
    3. Provide your response strictly in a JSON format containing a single key `label` and a value corresponding to the array of assigned categories. Do not provide any additional information except the JSON.

    List of categories: {labels}

    Text sample: ```{x}```

    Your JSON response:
"""

CLASSIFIER_JUDGE_PROMPT_WITH_CONTEXT = """
    You will be provided with the following information:
    1. An arbitrary text sample. The sample is delimited with triple backticks.
    2. Some context regarding the text sample.
    3. List of categories the text sample can be assigned to. The list is delimited with square brackets. The categories in the list are enclosed in the single quotes and comma separated. The text sample belongs to at least one category but cannot exceed {max_cats}.

    Perform the following tasks:
    1. Identify to which categories the provided text belongs to with the highest probability. Consider the context only if the query is not clear.
    2. Assign the text sample to at least 1 but up to {max_cats} categories based on the probabilities.
    3. Provide your response strictly in a JSON format containing a single key `label` and a value corresponding to the array of assigned categories. Do not provide any additional information except the JSON.

    List of categories: {labels}

    Text sample: ```{x}```

    Context: `{context}`

    Your JSON response:
"""
