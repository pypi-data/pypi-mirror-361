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
  prompt = (f"You are given a statement, along with context. Your task is to generate a very precise and simple question "
           f"that verifies whether the term <{concept}> is correctly used in the statement. "
           f"Don't reference the statement in your question.\n"
           f"Context: {context}\n"
           f"Statement: {sentence}")
  
  question, _, _ = model.predict(prompt=prompt, max_tokens=50)
  
  return context + "\n" + question + " Answer the question in one simple sentence, as briefly as possible: "



def generate_validation_prompt_v2(model_name, sentence, context):
  
  model = init_model(model_name)
  
  # if model_name == "gpt-4o":
  #   prompt = f"You are given a statement, along with context. Your task is to generate a very precise and simple question that verifies whether the term <{concept}> is correctly used in the statement. Do not attempt to verify anything else.\nContext: {context}\nStatement: {sentence}"
  # elif model_name == "DeepSeek-V3":
  #   prompt = f"You are given a statement, along with context. Your task is to generate a very precise and simple question that verifies whether the term <{concept}> is correctly used in the statement. Don't reference the statement in your question.\nContext: {context}\nStatement: {sentence}"
  prompt = (f"You are given a math problem, possibly with a partial solution. "
           f"You are also given the next step in the solution. "
           f"Your task is to generate a simple question that verifies whether the next step is true or false. "
           f"Do not output anything else. Your question should follow these constraints:\n"
           f"-It should be a simple question that can be answered in one sentence.\n"
           f"-Avoid leading questions that point to an answer. (e.g. Instead of asking \"are there two roots to the equation $x^2 - 1$?\", ask \"How many roots does the equation $x^2 - 1$ have?\")\n"
           f"-Do not begin your question with \"is it true that\" because it promotes a confirmation bias. (e.g. Instead of asking \"is it true that the square root of 4 is 2?\", ask \"what is the value of the square root of 4?\")\n\n"
           f"Problem: {context}\n"
           f"Next step: {sentence}")
  
  question, _, _ = model.predict(prompt=prompt, max_tokens=120)
  
  return ("You are given a math problem, possibly with a partial solution. "
          "You will also be given a question regarding the current logic. "
          "Your job is to answer the given question in ONE simple sentence, as briefly as possible. "
          "CONSTRAINTs: Do not use any <think></think> tags, and don't include reasoning steps. "
          "Do not attempt to solve the original problem:\n\n"
          f"Original Problem: {context}\n\n"
          f"Question: {question}")