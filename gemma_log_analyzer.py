from transformers import pipeline
from huggingface_hub import InferenceClient
import re

class LogAnalyzer:
    def __init__(self, model_name="google/gemma-2b-it", token=None, local_mode=False):
        self.local_mode = local_mode
        if self.local_mode:
            # Downloads the 6GB model to your computer
            self.pipe = pipeline(
                "text-generation",
                model=model_name,
                token=token
            )
        else:
            # Uses the free Hugging Face API
            self.client = InferenceClient(model=model_name, token=token)

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
        try:
            if self.local_mode:
                result = self.pipe(prompt, max_new_tokens=200, max_length=None)
                generated_text = result[0]["generated_text"]
            else:
                generated_text = self.client.text_generation(
                    prompt, 
                    max_new_tokens=200,
                    temperature=0.1
                )
            
            # Clean up the output
            output = generated_text.strip()
            if "Log:" in output:
                output = output.split("Log:")[1].split("\"", 1)[-1].strip()
                if log in output:
                    output = output.replace(log, "").strip()
            return output
            
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"

if __name__ == "__main__":
    pass