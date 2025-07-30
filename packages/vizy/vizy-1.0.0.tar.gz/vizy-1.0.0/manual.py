import vizy
import torch
import numpy as np

from PIL import Image

test_image = Image.open("tests/data/input/test_image.jpg")
img = np.array(test_image)[np.newaxis, :, :, :]  # Convert to (1, H, W, C)
img = img.transpose(3, 0, 1, 2)  # Convert to CBHW format
img = torch.from_numpy(img).float()  # Convert to torch tensor and cast to float

# Create a batch of 5 images by duplicating and adding some noise
img = torch.cat(
    [
        img,
        img + torch.randn_like(img) * 10,
        # img + torch.randn_like(img)*5,
        # img + torch.randn_like(img)*15,
        # img + torch.randn_like(img)*100,
    ],
    dim=1,
)
img = torch.clip(img, 0, 255)  # Ensure values stay in valid range

# img = img.permute(1, 0, 2, 3)  # channel confusion!

# vizy.summary(img)
vizy.plot(img)
