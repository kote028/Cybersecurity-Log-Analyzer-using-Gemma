from transformers import pipeline
import re

class LogAnalyzer:
    def __init__(self, model_name="google/gemma-2b-it", token=None):
        self.pipe = pipeline(
            "text-generation",
            model=model_name,
            token=token
        )

    def analyze_log(self, log):
        prompt = f"""
You are a cybersecurity expert.

Analyze the log below and provide:
1. Summary
2. Risk Level (Low/Medium/High)
3. Attack Type
4. Recommended Actions

Do NOT show reasoning. Format your response cleanly.

Log:
{log}
"""
        result = self.pipe(prompt, max_new_tokens=200)
        generated_text = result[0]["generated_text"]
        
        # Clean up the output to only return the model's response part
        if "Log:" in generated_text:
            output = generated_text.split("Log:")[1].split("\"", 1)[-1].strip()
            # It might include the original log in the prompt, let's remove the prompt from the result
            if log in output:
                output = output.replace(log, "").strip()
            return output
        return generated_text

if __name__ == "__main__":
    analyzer = LogAnalyzer()
    test_log = "Failed login 5 times from 192.168.1.10"
    print(analyzer.analyze_log(test_log))