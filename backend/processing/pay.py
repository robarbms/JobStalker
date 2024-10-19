import re

# Gets a pay range from a job description
def get_pay(text):
    pattern = r"(\$(\d{1,3},?)*)"
    try:
        matches = re.findall(pattern, text)
        if len(matches) > 0:
            prices = [match[0] for match in matches]

            prices = [re.sub(r'[$,]', '', price) for price in prices]
            prices = [int(price) for price in prices]
            prices.sort()
            salary_min = prices[0]
            salary_max = prices[0] if len(prices) < 2 else prices[-1]
            return salary_min, salary_max

    except Exception as e:
        print("Error: Could not find a pay range.", e)

    return None, None