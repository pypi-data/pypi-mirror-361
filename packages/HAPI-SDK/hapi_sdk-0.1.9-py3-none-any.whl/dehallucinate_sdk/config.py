import os

# Get the absolute path of the current package directory.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Update the classifier mapping to point to the models folder inside the package.
CLASSIFIER_MAPPING = {
    "meta-llama/Llama-2-7b-chat-hf": os.path.join(CURRENT_DIR, "models", "best_acc_model.pt"),
}
