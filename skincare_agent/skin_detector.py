import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import os


class SkinTypeDetector:
    """
    Skin type detector using your own fine-tuned Hugging Face ViT model.
    Supports: oily, dry, normal skin types
    """

    def __init__(self, model_path: str = "models/advanced_skin_model_complete.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = None
        self.classes = ["dry", "normal", "oily"]

        # Image preprocessing — same normalization used in ViT training
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

        self._load_model()

    # ---------------------------------------------------------------------
    def _load_model(self):
        """
        Load fine-tuned ViT model checkpoint and rebuild the architecture.
        """
        from transformers import ViTForImageClassification

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

        try:
            # Load checkpoint dictionary (you saved it using torch.save({...}))
            checkpoint = torch.load(self.model_path, map_location=self.device)
            state_dict = checkpoint.get('model_state_dict', checkpoint)
            print(f"[Debug] Loaded model from: {self.model_path}")
            print(f"[Debug] Checkpoint keys: {checkpoint.keys()}")

            # Recreate the same model architecture you fine-tuned
            self.model = ViTForImageClassification.from_pretrained(
                "dima806/skin_types_image_detection",
                num_labels=3,  # dry, normal, oily
                ignore_mismatched_sizes=True
            )

            # Load your fine-tuned weights
            self.model.load_state_dict(state_dict, strict=False)
            self.model.to(self.device)
            self.model.eval()

            print(f"[SkinDetector] ✅ Successfully loaded fine-tuned ViT model from {self.model_path}")

        except Exception as e:
            print(f"[SkinDetector] ❌ Failed to load model: {e}")
            raise RuntimeError("Could not load fine-tuned ViT model — check checkpoint file or weights.")

    # ---------------------------------------------------------------------
    def detect_skin_type(self, image_path: str) -> str:
        """
        Detect skin type from an image.

        Args:
            image_path: Path to the image file

        Returns:
            Predicted class: 'dry', 'normal', or 'oily'
        """
        try:
            print(f"[Debug] Using device: {self.device}")
            print(f"[Debug] Loading image: {image_path}")

            image = Image.open(image_path).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            print(f"[Debug] Image tensor shape: {image_tensor.shape}")

            if self.model is None:
                raise RuntimeError("Model not loaded.")

            with torch.no_grad():
                outputs = self.model(image_tensor)
                logits = outputs.logits if hasattr(outputs, "logits") else outputs
                probabilities = torch.nn.functional.softmax(logits, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()

                print(f"[SkinDetector] 🎯 Prediction: {self.classes[predicted_class]} ({confidence:.2f})")
                return self.classes[predicted_class]

        except Exception as e:
            print(f"Error in skin detection: {e}")
            raise 