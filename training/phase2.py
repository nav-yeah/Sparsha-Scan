import os
import tensorflow as tf
from tensorflow.keras import models
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# ===============================
# ✅ Paths (same as before)
# ===============================
BASE_DIR = r"C:\Users\Navya\Desktop\sparsha\dataset"
DERMNET_TRAIN = os.path.join(BASE_DIR, "Dermnet", "train")
DERMNET_TEST  = os.path.join(BASE_DIR, "Dermnet", "test")

IMG_SIZE = (128, 128)
BATCH_SIZE = 8
EPOCHS = 15  # you can raise to 20 later if stable

# ===============================
# ✅ Data generators (same)
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
# ✅ Load previous fine-tuned model
# ===============================
model = models.load_model("mobilenet_dermnet_finetuned_final.keras")

# ===============================
# ✅ Full unfreeze (fine-tune all layers)
# ===============================
base_model = model.layers[0]  # MobileNetV2 base
for layer in base_model.layers:
    layer.trainable = True

# ===============================
# ✅ Recompile with smaller LR
# ===============================
model.compile(
    optimizer=Adam(learning_rate=5e-6),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ===============================
# ✅ Callbacks
# ===============================
callbacks = [
    EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True),
    ModelCheckpoint('mobilenet_dermnet_finetuned_full.keras', save_best_only=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-7)
]

# ===============================
# ✅ Continue Fine-tuning
# ===============================
print("🚀 Starting FULL fine-tuning (Stage 3)...")
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=callbacks
)

# ===============================
# ✅ Save Final Model
# ===============================
model.save("mobilenet_dermnet_finetuned_full_final.keras")
print("✅ Full fine-tuning complete and model saved!")

# ===============================
# ✅ Plot Updated Curves
# ===============================
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label='Train')
plt.plot(history.history['val_accuracy'], label='Val')
plt.title('Full Fine-tuning Accuracy')
plt.legend()

plt.subplot(1,2,2)
plt.plot(history.history['loss'], label='Train')
plt.plot(history.history['val_loss'], label='Val')
plt.title('Full Fine-tuning Loss')
plt.legend()

plt.show()
