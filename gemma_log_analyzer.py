from huggingface_hub import InferenceClient
import re

class LogAnalyzer:
    def __init__(self, model_name="google/gemma-2b-it", token=None):
        # Using InferenceClient so we don't have to download 6GB of weights locally!
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
            # Call the free Hugging Face Inference API
            generated_text = self.client.text_generation(
                prompt, 
                max_new_tokens=200,
                temperature=0.1
            )
            
            # Clean up the output
            output = generated_text.strip()
            if "Log:" in output:
                output = output.split("Log:")[1].split("\"", 1)[-1].strip()
            return output
            
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"

if __name__ == "__main__":
    # Test block
    pass