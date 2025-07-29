import torch

def extract_hidden_states(model, input_ids):
    with torch.no_grad():
        outputs = model(input_ids, output_hidden_states=True)
        hidden_states = outputs.hidden_states
        last_layer = hidden_states[-1][:, -1, :]
        second_last_layer = hidden_states[-2][:, -1, :]
        concatenated = torch.cat((last_layer, second_last_layer), dim=1)
    return concatenated
