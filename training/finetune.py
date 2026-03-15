import os
import tensorflow as tf
from tensorflow.keras import models, layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt

# ===============================
# ✅ Paths
# ===============================
BASE_DIR = r"C:\Users\Navya\Desktop\sparsha\dataset"
DERMNET_TRAIN = os.path.join(BASE_DIR, "Dermnet", "train")
DERMNET_TEST  = os.path.join(BASE_DIR, "Dermnet", "test")

IMG_SIZE = (128, 128)
BATCH_SIZE = 8
EPOCHS = 10  # You can increase later

# ===============================
# ✅ Data generators
# ===============================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    validation_split=0.2
)

train_gen = train_datagen.flow_from_directory(
    DERMNET_TRAIN,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    subset='training'
)

val_gen = train_datagen.flow_from_directory(
    DERMNET_TRAIN,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    subset='validation'
)

# ===============================
# ✅ Load and unfreeze layers
# ===============================
model = models.load_model("mobilenet_dermnet_model_final.keras")

base_model = model.layers[0]  # MobileNetV2 is first
fine_tune_at = len(base_model.layers) - 50  # unfreeze last 50 layers

for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False
for layer in base_model.layers[fine_tune_at:]:
    layer.trainable = True

# ===============================
# ✅ Compile (smaller LR)
# ===============================
model.compile(
    optimizer=Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ===============================
# ✅ Callbacks
# ===============================
callbacks = [
    EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
    ModelCheckpoint('mobilenet_dermnet_finetuned.keras', save_best_only=True)
]

# ===============================
# ✅ Fine-tune training
# ===============================
print("🚀 Starting fine-tuning...")
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=callbacks
)

# ===============================
# ✅ Save final model
# ===============================
model.save("mobilenet_dermnet_finetuned_final.keras")
print("✅ Fine-tuning complete and model saved!")

# ===============================
# ✅ Plot accuracy/loss
# ===============================
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label='Train')
plt.plot(history.history['val_accuracy'], label='Val')
plt.title('Fine-tuning Accuracy')
plt.legend()

plt.subplot(1,2,2)
plt.plot(history.history['loss'], label='Train')
plt.plot(history.history['val_loss'], label='Val')
plt.title('Fine-tuning Loss')
plt.legend()

plt.show()
