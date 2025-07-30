

# temporary storage of this function
def semantic_entropy(self, sentence, original_prompt, tokens, probs):
    tokens, probs = process_tokens(probs, tokens)

    hypotheses = hypothesis_preprocess_into_sentences(sentence)
    num_hypotheses = len(hypotheses)
    keyword_list = extract_keywords(inference_config.keyword_model, api_key, response)
    print(keyword_list)
    hypothesis_evaluations, hallucinated_keywords = filter_hypotheses(hypotheses, keyword_list, probs)
    print(hallucinated_keywords)
    labeled_hypotheses = {i: {"hypothesis": hypotheses[i]['text'], "is_hallucinated": hypothesis_evaluations[i], "hallucinated_keywords": hallucinated_keywords[i]} for i in range(num_hypotheses)}
    is_hallucinated_se = [False for i in range(num_hypotheses)]
    hallucinated_keywords_se = {i: [] for i in range(num_hypotheses)}
    
    topic = get_topic(original_prompt, api_key)
    
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
                hypothesis_context = hypotheses[i - 1]["text"]
            for hallucination in hallucinated_keywords[i]:
                validation_prompt = generate_validation_prompt(inference_config.validation_model, api_key, hypothesis, hypothesis_context, topic, hallucination[0])
                print(f"Validation Prompt: {validation_prompt}")
                full_responses = []
                sampled_responses = []
                for j in range(se_config.num_generations):
                    predicted_answer, sample_logits, sample_tokens = model_instance.predict(validation_prompt, inference_temperature, max_completion_tokens=se_config.max_completion_tokens)
                    full_responses.append((predicted_answer, sample_logits, sample_tokens))
                    sampled_responses.append(predicted_answer)
                    print(predicted_answer)
                entropies, semantic_ids = compute_entropy(se_config, api_key, validation_prompt, full_responses)
                entropy_data = {"all responses": json.dumps(sampled_responses), "semantic ids": json.dumps(semantic_ids), "entropies": json.dumps(entropies)}
                full_responses.append((response, token_log_likelihoods, tokens))
                local_labeled["semantic_entropy"].append(entropies["semantic_entropy"][0])
                local_labeled["validation_prompts"].append(validation_prompt)
                print(f"Entropy: {entropies['semantic_entropy'][0]}")
                if (entropies["semantic_entropy"][0] > se_config.entropy_threshold) or (entropies["semantic_entropy"][0] < se_config.contradiction_threshold and check_contradiction(inference_config.contradiction_model, api_key, hypothesis, sampled_responses, se_config.contradiction_num_samples)):
                    local_hallucinated_se = True
                    local_hallucinated_keywords_se.append(hallucination)
            return (i, local_labeled, local_hallucinated_se, local_hallucinated_keywords_se)
        futures = [executor.submit(process_hypothesis, i) for i in range(num_hypotheses)]
        for f in futures:
            i, updated_labeled, updated_hallucinated_se, updated_hallucinated_keywords_se = f.result()
            labeled_hypotheses[i] = updated_labeled
            is_hallucinated_se[i] = updated_hallucinated_se
            hallucinated_keywords_se[i] = updated_hallucinated_keywords_se
    return jsonify({"response": response, "hallucinations": hallucinated_keywords_se, "is_hallucinated_se": is_hallucinated_se, "hallucination_data": labeled_hypotheses})
