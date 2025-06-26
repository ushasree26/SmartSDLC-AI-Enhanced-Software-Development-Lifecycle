import os
from pathlib import Path
import shutil
import random
import matplotlib.pyplot as plt
import cv2
import yaml
from sklearn.model_selection import train_test_split
from ultralytics import YOLO

# Optional: Replace with proper logging
def log(message):
    print(f"[INFO] {message}")

# DATASET SETUP (run these in Colab separately, not in script)
# !kaggle datasets download mikhailma/railroad-worker-detection-dataset
# !unzip /content/railroad-worker-detection-dataset.zip

def create_folder(file_list, img_labels_root, imgs_source, mode):
    images_dir = Path(f"{img_labels_root}/images/{mode}")
    labels_dir = Path(f"{img_labels_root}/labels/{mode}")
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    for file_name in file_list:
        img_name = file_name.replace('.jpg', '')
        shutil.copyfile(f"{imgs_source}/{img_name}.jpg", f"{images_dir}/{img_name}.jpg")
        shutil.copyfile(f"{img_labels_root}/{img_name}.txt", f"{labels_dir}/{img_name}.txt")

def plot_bounding_boxes(image_files, dir_images, dir_labels, classes, rows=2, cols=2):
    fig, axs = plt.subplots(rows, cols, figsize=(16, 16))
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(dir_images, image_file)
        label_path = os.path.join(dir_labels, image_file.split(".")[0] + ".txt")

        image = cv2.imread(image_path)
        if image is None:
            continue

        try:
            with open(label_path, "r") as f:
                labels = f.read().strip().split("\n")
        except FileNotFoundError:
            continue

        for label in labels:
            parts = label.split()
            if len(parts) != 5:
                continue
            class_id, x_center, y_center, width, height = map(float, parts)
            x_min = int((x_center - width/2) * image.shape[1])
            y_min = int((y_center - height/2) * image.shape[0])
            x_max = int((x_center + width/2) * image.shape[1])
            y_max = int((y_center + height/2) * image.shape[0])

            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
            label_text = classes[int(class_id)]
            cv2.putText(image, label_text, (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        axs[i // cols, i % cols].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axs[i // cols, i % cols].axis('off')
    plt.show()

def main():
    dataset_dir = "/content/dataset"
    images_path = os.path.join(dataset_dir, "imgs")
    labels_path = os.path.join(dataset_dir, "txt")

    image_list = os.listdir(images_path)
    train_list, test_list = train_test_split(image_list, test_size=0.2, random_state=42)
    val_list, test_list = train_test_split(test_list, test_size=0.3, random_state=42)

    log(f"Total Images: {len(image_list)}, Train: {len(train_list)}, Val: {len(val_list)}, Test: {len(test_list)}")

    create_folder(train_list, labels_path, images_path, "train")
    create_folder(val_list, labels_path, images_path, "val")
    create_folder(test_list, labels_path, images_path, "test")

    # Preview random bounding boxes
    classes = {0: 'vest', 1: 'helmet', 2: 'worker'}
    random_images = random.sample(image_list, 4)
    plot_bounding_boxes(random_images, images_path, labels_path, classes)

    # Define YOLO data config
    data_config = {
        'train': f'{labels_path}/images/train',
        'val': f'{labels_path}/images/val',
        'nc': 3,
        'names': ['vest', 'helmet', 'worker']
    }

    yaml_path = '/content/railworkers.yaml'
    with open(yaml_path, 'w') as file:
        yaml.dump(data_config, file)

    # Load and train YOLO model
    model = YOLO("yolo11n.pt")
    model.train(data=yaml_path, epochs=6, imgsz=640, batch=16, lr0=0.001, dropout=0.15)

    # Save model
    model.save('/content/drive/MyDrive/model_checkpoint.pt')  # Ensure drive is mounted in Colab

    # Load model back (correct way)
    model = YOLO('/content/drive/MyDrive/model_checkpoint.pt')

    # Visualize predictions on random images
    plot_bounding_boxes(random_images, images_path, labels_path, classes)

if __name__ == "__main__":
    main()
