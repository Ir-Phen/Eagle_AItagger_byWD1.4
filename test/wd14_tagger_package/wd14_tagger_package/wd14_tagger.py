from wd14_tagger_api.tagger.interrogator import Interrogator
from PIL import Image
from pathlib import Path

from wd14_tagger_api.tagger.interrogators import interrogators

class ImageTagger:
    def __init__(self, model_name='wd14-convnextv2.v1', threshold=0.35,device="cpu"):
        self.threshold = threshold
        self.device = device
        self.load_model(model_name)

    def load_model(self, model_name):
        """
        Loads the selected model.
        """
        if model_name in interrogators.keys():
            self.model_name = model_name
            self.interrogator = interrogators[model_name]
            self.interrogator.use_cpu = self.device == "cpu"
        else:
            raise ValueError(f"Model {model_name} not available.")

    def change_model(self, new_model_name):
        """
        Changes the current model to the new model.
        """
        print(f"Changing model from {self.model_name} to {new_model_name}")
        self.load_model(new_model_name)

    def image_interrogate(self, image_path: Path):
        """
        Performs prediction on an image path.
        """
        im = Image.open(image_path)
        result = self.interrogator.interrogate(im)
        return self.interrogator.postprocess_tags(result[1], threshold=self.threshold)


# TEST
# tags = Interrogator.postprocess_tags(result[1], threshold=self.threshold)
# return tags

# def process_file(self, file_path):
# tags = self.image_interrogate(Path(file_path))
# print("\nDetected Tags:", ", ".join(tags.keys()))

# # Example usage:
# if __name__ == "__main__":
# tagger = ImageTagger(model_name='wd14-convnextv2.v1', threshold=0.35) 
# file_path = "/path/to/your/image.jpg" 
# tagger.process_file(file_path)  

# tagger.change_model('new-model-name') 
