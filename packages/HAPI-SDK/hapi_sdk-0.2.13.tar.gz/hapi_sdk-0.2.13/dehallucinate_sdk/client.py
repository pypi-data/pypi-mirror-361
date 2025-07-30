import os
import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
# from dehallucinate_sdk.config import CLASSIFIER_MAPPING
from dehallucinate_sdk.telemetry import init_telemetry_log, report_usage
from dehallucinate_sdk.utils import extract_hidden_states
# from dehallucinate_sdk.classifier import HAPIClassifier  # Assumes classifier.py is available
from dehallucinate_sdk.SE.SemanticEntropy.modules.utils.SE_config import SEConfig
from dehallucinate_sdk.SE.SemanticEntropy.compute_entropy import compute_entropy, init_entailment_model
from dehallucinate_sdk.SE.utils.init_model import init_model
from dehallucinate_sdk.SE.utils.inference_config import InferenceConfig
from dehallucinate_sdk.SE.ConfidenceFilter.process_tokens import process_tokens, filter_hypotheses
from dehallucinate_sdk.SE.ConfidenceFilter.create_validation import get_topic, generate_validation_prompt,  generate_validation_prompt_v2
from dehallucinate_sdk.SE.ConfidenceFilter.extract_keywords import extract_keywords
from dehallucinate_sdk.SE.ConfidenceFilter.self_contradiction import check_contradiction
from dehallucinate_sdk.SE.CoNLI.modules.data.response_preprocess import hypothesis_preprocess_into_sentences
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import login
import nltk
import re

# Optionally, you can remove this login call if clients set their tokens via parameters.
# login(token="") 

inference_config = InferenceConfig()
nltk.download('punkt_tab')

class DeHallucinationClient:
    def __init__(self, model_id, license_key, openai_api_key=None, hf_api_key=None, device="cuda:0", 
                 telemetry_log_path="telemetry.log", entropy_threshold=0.63, contradiction_threshold=0.25, 
                 contradiction_num_samples=1, num_generations=3):
        """
        Initializes the dehallucination client.
        :param model_id: Hugging Face model identifier (e.g., "meta-llama/Llama-2-7b-chat-hf")
        :param license_key: Client's license key.
        :param openai_api_key: The OpenAI API key; if not provided, falls back to the OPENAI_API_KEY environment variable.
        :param hf_api_key: The Hugging Face API token; if not provided, falls back to the HUGGINGFACE_API_KEY environment variable.
        :param device: Device to use ("cuda:0" if GPU available, otherwise "cpu").
        :param telemetry_log_path: Path for logging telemetry data.
        :param entropy_threshold: Threshold for semantic entropy detection (default: 0.63).
        :param contradiction_threshold: Threshold for contradiction detection (default: 0.25).
        :param contradiction_num_samples: Number of samples for contradiction checking (default: 1).
        :param num_generations: Number of generations for semantic entropy analysis (default: 3).
        """
        if not license_key or license_key.strip() == "":
            raise ValueError("A valid license key is required.")
        self.license_key = license_key
        self.model_id = model_id
        self.device = device if torch.cuda.is_available() else "cpu"

        # Initialize semantic entropy configuration with custom parameters
        self.se_config = SEConfig()
        self.se_config.entropy_threshold = entropy_threshold
        self.se_config.contradiction_threshold = contradiction_threshold
        self.se_config.contradiction_num_samples = contradiction_num_samples
        self.se_config.num_generations = num_generations

        # Set OpenAI API key
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("An OpenAI API key is required either as a parameter or via the OPENAI_API_KEY environment variable.")
        self.openai_api_key = openai_api_key
        
        # Set Hugging Face API token
        if hf_api_key is None:
            hf_api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if not hf_api_key:
            raise ValueError("A Hugging Face API token is required either as a parameter or via the HUGGINGFACE_API_KEY environment variable.")
        self.hf_api_key = hf_api_key

        # Load LLM from Hugging Face using the provided HF token.
        print(f"Loading LLM ({model_id}) on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=self.hf_api_key)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16,  # enforce half precision
            device_map="auto",
            offload_folder="./offload",
            use_auth_token=self.hf_api_key
        ).to(self.device)

        # # Load classifier based on the model ID.
        # if model_id not in CLASSIFIER_MAPPING:
        #     raise ValueError(f"No classifier configured for model_id '{model_id}'")
        # classifier_path = CLASSIFIER_MAPPING[model_id]
        # print("Loading Hallucination Classifier from", classifier_path)
        # self.classifier = HAPIClassifier(classifier_path, device=self.device)

        # # Initialize telemetry logging.
        # self.telemetry_log_path = init_telemetry_log(telemetry_log_path)
        # print("DeHallucinationClient initialized")

    def generate_sentence(self, context: str, sentence_max_length=60, temperature=0.8, top_k=50, semantic_entropy=False):
        print("Generating sentence...")
        raw_input = self.tokenizer(context, return_tensors="pt").to(self.device)
        
        return_dict_in_generate = semantic_entropy  # bool
        output_scores = semantic_entropy
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": context}
        ]

        # Apply chat template and get input tensors
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            return_tensors="pt"
        )
        
        inputs = inputs.to(self.device)

        # Prepare arguments for generate
        generate_kwargs = {
            "input_ids": inputs,
            "max_new_tokens": sentence_max_length,
            "do_sample": True,
            "temperature": temperature,
            "top_k": top_k,
            "return_dict_in_generate": return_dict_in_generate,
            "output_scores": output_scores,
        }
        # if "attention_mask" in inputs:
        #     generate_kwargs["attention_mask"] = inputs["attention_mask"]

        output = self.model.generate(**generate_kwargs)

        if return_dict_in_generate:
            sequences = output.sequences
            scores = output.scores
        else:
            sequences = output
            scores = None

        input_length = inputs.shape[-1]
        generated_tokens = sequences[0, input_length:]
        sentence = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        if sentence.startswith(context):
            sentence = sentence[len(context):].strip()
        if ". " in sentence:
            sentence = sentence.split(". ")[0] + "."
        else:
            if sentence and sentence[-1] not in ".!?":
                sentence += "."
                
        # print(sentence)

        if semantic_entropy and scores is not None:
            generated_tokens = sequences[0, inputs.shape[-1]:]
            probs = [torch.softmax(score, dim=-1) for score in scores]
            token_probs = []
            token_texts = []
            
            # Get the full decoded text first
            full_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            running_text = ""
            
            for i, token_id in enumerate(generated_tokens):
                token_probs.append(probs[i][0, token_id].item())
                
                # Decode individual token with its proper context
                prev_text = running_text
                running_text = self.tokenizer.decode(generated_tokens[:i+1], skip_special_tokens=True)
                
                # Extract just this token's contribution (with whitespace preserved)
                token_text = running_text[len(prev_text):]
                if not token_text and i > 0:  # Handle empty token case
                    token_text = ""  # Placeholder for empty tokens
                    
                token_texts.append(token_text)
                # print(f"Token {i}: '{token_text}' ({token_probs[-1]:.3f})")
                
            return sentence.strip(), token_probs, token_texts
        
        return sentence.strip(), None, None


    def generate(self, context: str, max_new_tokens=200, temperature=0.8, top_k=50, semantic_entropy=False):
        """
        Generate a full response (not limited to one sentence) with optional token probabilities.
        
        :param context: Input prompt/context for generation
        :param max_new_tokens: Maximum number of new tokens to generate (default: 200)
        :param temperature: Sampling temperature for generation (default: 0.8)
        :param top_k: Top-k sampling parameter (default: 50)
        :param semantic_entropy: Whether to return token probabilities and texts (default: False)
        :return: If semantic_entropy=True: (response, token_probs, token_texts)
                 If semantic_entropy=False: (response, None, None)
        """
        print("Generating full response...")
        raw_input = self.tokenizer(context, return_tensors="pt").to(self.device)
        return_dict_in_generate = semantic_entropy
        output_scores = semantic_entropy
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": context}
        ]

        # Apply chat template and get input tensors
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            return_tensors="pt"
        )
        
        inputs = inputs.to(self.device)
        attention_mask = torch.ones_like(inputs).to(self.device)

        # Prepare arguments for generate
        generate_kwargs = {
            "input_ids": inputs,
            "attention_mask": attention_mask,
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": temperature,
            "top_k": top_k,
            "return_dict_in_generate": return_dict_in_generate,
            "output_scores": output_scores,
        }
        # if "attention_mask" in inputs:
        #     generate_kwargs["attention_mask"] = inputs["attention_mask"]

        output = self.model.generate(**generate_kwargs)

        if return_dict_in_generate:
            sequences = output.sequences
            scores = output.scores
        else:
            sequences = output
            scores = None

        # Decode the full response
        full_response = self.tokenizer.decode(sequences[0], skip_special_tokens=True)
        
        # Remove the original context from the response
        if full_response.startswith(context):
            response = full_response[len(context):].strip()
        else:
            response = full_response.strip()
                
        # print(f"Generated response ({len(response)} characters)")

        if semantic_entropy and scores is not None:
            generated_tokens = sequences[0, inputs.shape[-1]:]
            probs = [torch.softmax(score, dim=-1) for score in scores]
            token_probs = []
            token_texts = []
            
            # Get the full decoded text first
            full_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            running_text = ""
            
            for i, token_id in enumerate(generated_tokens):
                token_probs.append(probs[i][0, token_id].item())
                
                # Decode individual token with its proper context
                prev_text = running_text
                running_text = self.tokenizer.decode(generated_tokens[:i+1], skip_special_tokens=True)
                
                # Extract just this token's contribution (with whitespace preserved)
                token_text = running_text[len(prev_text):]
                if not token_text and i > 0:  # Handle empty token case
                    token_text = ""  # Placeholder for empty tokens
                    
                token_texts.append(token_text)
                
            # print(f"Extracted {len(token_probs)} token probabilities")
            return response.strip(), token_probs, token_texts
        
        return response.strip(), None, None


    def sentence_contains_hallucination(self, sentence, original_prompt, threshold=0.9):
        print("Checking hallucination...")
        stripped_sentence = sentence.replace(original_prompt, "").replace("\n", " ").strip()
        tokens = stripped_sentence.split()
        for token in tokens:
            token_tensor = self.tokenizer(token, return_tensors="pt").input_ids.to(self.device)
            hidden_state = extract_hidden_states(self.model, token_tensor)
            score = self.classifier.get_hallucination_score(hidden_state)
            if score > threshold:
                return True
        return False

    def semantic_entropy_check(self, response, original_prompt, tokens_raw, probs_raw):
        print("Analyzing semantic entropy...")
        tokens, probs = process_tokens(probs_raw, tokens_raw)

        hypotheses = hypothesis_preprocess_into_sentences(response)
        num_hypotheses = len(hypotheses)
        keyword_list = extract_keywords(inference_config.keyword_model, response)
        # print(keyword_list)
        hypothesis_evaluations, hallucinated_keywords = filter_hypotheses(hypotheses, keyword_list, probs)
        # print(hallucinated_keywords)
        labeled_hypotheses = {i: {"hypothesis": hypotheses[i]['text'], "is_hallucinated": hypothesis_evaluations[i], "hallucinated_keywords": hallucinated_keywords[i]} for i in range(num_hypotheses)}
        is_hallucinated_se = [False for i in range(num_hypotheses)]
        hallucinated_keywords_se = {i: [] for i in range(num_hypotheses)}
        
        topic = get_topic(original_prompt)
        
        entailment_model = init_entailment_model(inference_config.entailment_model)
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            def process_hypothesis(i):
                local_labeled = labeled_hypotheses[i]
                local_hallucinated_se = is_hallucinated_se[i]
                local_hallucinated_keywords_se = hallucinated_keywords_se[i]
                if not hypothesis_evaluations[i]:
                    local_labeled["semantic_entropy"] = None
                    return (i, local_labeled, local_hallucinated_se, local_hallucinated_keywords_se)
                local_labeled["semantic_entropy"] = []
                local_labeled["validation_prompts"] = []
                hypothesis = hypotheses[i]["text"]
                
                if i == 0:
                    hypothesis_context = ""
                else:
                    hypothesis_context = " ".join([hypotheses[j]["text"] for j in range(i)])
                    
                for hallucination in hallucinated_keywords[i]:
                    validation_prompt = generate_validation_prompt(inference_config.validation_model, hypothesis, hypothesis_context, topic, hallucination[0])
                    # print(f"Validation Prompt: {validation_prompt}")
                    full_responses = []
                    sampled_responses = []
                    
                    for j in range(self.se_config.num_generations):
                        predicted_answer, sample_logits, sample_tokens = self.generate_sentence(
                            validation_prompt, 
                            sentence_max_length=60, 
                            temperature=0.4, 
                            semantic_entropy=True
                        )
                        full_responses.append((predicted_answer, sample_logits, sample_tokens))
                        sampled_responses.append(predicted_answer)
                        # print(predicted_answer)
                        
                    entropies, semantic_ids = compute_entropy(entailment_model, self.se_config, validation_prompt, full_responses)
                    entropy_data = {"all_responses": json.dumps(sampled_responses), "semantic_ids": json.dumps(semantic_ids), "entropies": json.dumps(entropies)}
                    full_responses.append((response, probs, tokens))
                    local_labeled["semantic_entropy"].append(entropies["semantic_entropy"][0])
                    local_labeled["validation_prompts"].append(validation_prompt)
                    # print(f"Entropy: {entropies['semantic_entropy'][0]}")
                    if (entropies["semantic_entropy"][0] > self.se_config.entropy_threshold) \
                            or (entropies["semantic_entropy"][0] < self.se_config.contradiction_threshold 
                            and check_contradiction(inference_config.contradiction_model, hypothesis, sampled_responses, self.se_config.contradiction_num_samples)):
                        local_hallucinated_se = True
                        local_hallucinated_keywords_se.append(hallucination)
                        
                return (i, local_labeled, local_hallucinated_se, local_hallucinated_keywords_se)
            
            futures = [executor.submit(process_hypothesis, i) for i in range(num_hypotheses)]
            
            for f in futures:
                i, updated_labeled, updated_hallucinated_se, updated_hallucinated_keywords_se = f.result()
                labeled_hypotheses[i] = updated_labeled
                is_hallucinated_se[i] = updated_hallucinated_se
                hallucinated_keywords_se[i] = updated_hallucinated_keywords_se
        
        return {"response": response, "hallucinations": hallucinated_keywords_se, "is_hallucinated_se": is_hallucinated_se, "hallucination_data": labeled_hypotheses}

    def dehallucinate1(self, prompt, desired_word_count=250, sentence_max_length=60, max_regen_attempts=5, threshold=0.9):
        """
        dehallucinate1: Generates a passage using only the classifier-based approach.
        """
        context = prompt
        generated_sentences = []
        flagged_sentences = []
        while len(" ".join(generated_sentences).split()) < desired_word_count:
            sentence = self.generate_sentence(context, sentence_max_length, semantic_entropy=False)[0]
            attempts = 0
            while self.sentence_contains_hallucination(sentence, prompt, threshold) and attempts < max_regen_attempts:
                print(f"[dehallucinate1] Hallucination detected in sentence: '{sentence}'. Regenerating (attempt {attempts+1})...")
                flagged_sentences.append(sentence)
                sentence = self.generate_sentence(context, sentence_max_length, semantic_entropy=False)[0]
                attempts += 1
            generated_sentences.append(sentence)
            context += " " + sentence
            if not sentence.strip():
                break
        output_text = " ".join(generated_sentences)
        report_usage(self.license_key, self.model_id, prompt, output_text, self.tokenizer, self.telemetry_log_path)
        return output_text, flagged_sentences

    def dehallucinate2(self, prompt, desired_word_count=250, sentence_max_length=60, max_regen_attempts=3, threshold=0.9):
        """
        dehallucinate2: Generates a passage using classifier plus semantic entropy filtering.
        """
        # Define a default inference temperature for semantic entropy regeneration.
        inference_temperature = 1.0
        
        context = prompt
        generated_sentences = []
        flagged_sentences = []
        se_flags = []
        while len(" ".join(generated_sentences).split()) < desired_word_count:
            sentence, token_probs, tokens_raw = self.generate_sentence(context, sentence_max_length, semantic_entropy=True)
            attempts = 0
            se_result = self.semantic_entropy_check(sentence, prompt, tokens_raw, token_probs)
            # print(f"Semantic Entropy Result: {se_result}")
            while se_result["is_hallucinated_se"] and self.sentence_contains_hallucination(sentence, prompt, threshold) and attempts < max_regen_attempts:
                if se_result["is_hallucinated_se"]:
                    print(f"[dehallucinate2] Semantic entropy flagged sentence.")
                print(f"[dehallucinate2] Classifier flagged sentence: '{sentence}'. Regenerating (attempt {attempts+1})...")
                flagged_sentences.append(sentence)
                sentence, token_probs, tokens_raw = self.generate_sentence(context, sentence_max_length, semantic_entropy=True)
                attempts += 1
                continue
            generated_sentences.append(sentence)
            context += " " + sentence
            if not sentence.strip():
                break
            se_flags.append(se_result)
        output_text = " ".join(generated_sentences)
        report_usage(self.license_key, self.model_id, prompt, output_text, self.tokenizer, self.telemetry_log_path)
        return output_text, flagged_sentences, se_flags
    
    def generate_output(self, prompt, max_new_tokens=200, temperature=0.8, top_k=10):
        """
        Generate a full response and run semantic entropy analysis on it.
        
        :param prompt: Input prompt for generation
        :param max_new_tokens: Maximum number of new tokens to generate (default: 200)
        :param temperature: Sampling temperature for generation (default: 0.8)
        :param top_k: Top-k sampling parameter (default: 50)
        :return: (response, semantic_entropy_result)
        """
        # Generate full response with token probabilities
        response, token_probs, token_texts = self.generate(
            prompt, 
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            semantic_entropy=True
        )
        
        # Run semantic entropy check on the full response
        se_result = self.semantic_entropy_check(response, prompt, token_texts, token_probs)
        
        return response, se_result

    def full_generation(self, prompt, max_length=400):
        print("Generating full output...")
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        output_ids = self.model.generate(**inputs, max_length=max_length)
        output_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        report_usage(self.license_key, self.model_id, prompt, output_text, self.tokenizer, self.telemetry_log_path)
        return output_text
    
    
    def _extract_answer_from_reasoning(self, text):
        answer_match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL | re.IGNORECASE)
        if answer_match:
            return answer_match.group(1).strip()
        
        return text


    def semantic_entropy_check_v2(self, sentence, original_prompt, tokens_raw, probs_raw):
        print("Analyzing semantic entropy...")
        tokens, probs = process_tokens(probs_raw, tokens_raw)
        
        local_hallucinated_se = False
        local_hallucinated_keywords_se = []
        
        validation_prompt = generate_validation_prompt_v2(inference_config.validation_model, sentence, original_prompt)
        full_responses = []
        sampled_responses = []
        
        entailment_model = init_entailment_model(inference_config.entailment_model)
        
        
        for j in range(self.se_config.num_generations):
            predicted_answer, sample_logits, sample_tokens = self.generate_sentence(
                validation_prompt, 
                sentence_max_length=200, 
                temperature=0.6, 
                semantic_entropy=True
            )
            
            # Extract answer from reasoning model output if it contains <answer> tags
            extracted_answer = self._extract_answer_from_reasoning(predicted_answer)
            
            full_responses.append((extracted_answer, sample_logits, sample_tokens))
            sampled_responses.append(extracted_answer)
        
        entropies, semantic_ids = compute_entropy(entailment_model, self.se_config, validation_prompt, full_responses)
        entropy_data = {"all_responses": json.dumps(sampled_responses), "semantic_ids": json.dumps(semantic_ids), "entropies": json.dumps(entropies), "validation_prompt": validation_prompt}
        print(f"Entropy: {entropies['semantic_entropy'][0]}")
        if (entropies["semantic_entropy"][0] > self.se_config.entropy_threshold) \
                or (entropies["semantic_entropy"][0] < self.se_config.contradiction_threshold 
                and check_contradiction(inference_config.contradiction_model, sentence, sampled_responses, self.se_config.contradiction_num_samples)):
            return True, entropy_data
        return False, entropy_data


# Example usage with custom semantic entropy parameters:
# client = DeHallucinationClient(
#     model_id="meta-llama/Llama-2-7b-chat-hf",
#     license_key="your_license_key",
#     entropy_threshold=0.7,        # Higher threshold = more conservative entropy detection
#     contradiction_threshold=0.3,  # Higher threshold = more conservative contradiction detection
#     contradiction_num_samples=2,  # More samples for contradiction checking
#     num_generations=5             # More generations for semantic entropy analysis
# )
#
# # Generate a single sentence with token probabilities:
# sentence, token_probs, token_texts = client.generate_sentence(
#     "What is quantum computing?", 
#     semantic_entropy=True
# )
#
# # Generate a full response with token probabilities:
# response, token_probs, token_texts = client.generate(
#     "Explain the history of artificial intelligence",
#     max_new_tokens=300,
#     semantic_entropy=True
# )
#
# # Generate and analyze with semantic entropy:
# response, se_analysis = client.generate_output(
#     "Tell me about climate change",
#     max_new_tokens=250
# )
    
    
