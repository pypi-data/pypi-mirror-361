from ..utils.init_model import init_model

# try chain of thought or few shot
def get_topic(input):
  
  model = init_model("gpt-4o")
  
  prompt = "Extract the key topic of the following instruction. Answer only with the key topic. Do not output anything else: "
  full_prompt = prompt + input
  
  output_raw, _, _ = model.predict(prompt=full_prompt, max_tokens=10)
  
  return output_raw.rstrip('.,!?')
  

def generate_validation_prompt(model_name, sentence, context, topic, concept):
  
  model = init_model(model_name)
  
  # if model_name == "gpt-4o":
  #   prompt = f"You are given a statement, along with context. Your task is to generate a very precise and simple question that verifies whether the term <{concept}> is correctly used in the statement. Do not attempt to verify anything else.\nContext: {context}\nStatement: {sentence}"
  # elif model_name == "DeepSeek-V3":
  #   prompt = f"You are given a statement, along with context. Your task is to generate a very precise and simple question that verifies whether the term <{concept}> is correctly used in the statement. Don't reference the statement in your question.\nContext: {context}\nStatement: {sentence}"
  prompt = f"You are given a statement, along with context. Your task is to generate a very precise and simple question that verifies whether the term <{concept}> is correctly used in the statement. Don't reference the statement in your question.\nContext: {context}\nStatement: {sentence}"
  
  question, _, _ = model.predict(prompt=prompt, max_tokens=50)
  
  return question + " Answer the question in one simple sentence, as briefly as possible: "