import tensorflow as tf
from tensorflow.keras import models, layers, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# -----------------------------
# PATHS & BASIC CONFIG
# -----------------------------
base_dir = r"C:\Users\Navya\Desktop\sparsha\dataset\Dermnet"  # change if needed
train_dir = os.path.join(base_dir, "train")
val_dir = os.path.join(base_dir, "test")

fine_tuned_model_path = "mobilenet_dermnet_finetuned_full_final.keras"

batch_size = 32
img_size = (128,128)
epochs = 15

# -----------------------------
# LOAD MODEL
# -----------------------------
print("🚀 Loading fine-tuned model from Stage 2...")
model = tf.keras.models.load_model(fine_tuned_model_path)
print("✅ Model loaded successfully!")

# -----------------------------
# UNFREEZE ALL LAYERS FOR FULL FINE-TUNING
# -----------------------------
for layer in model.layers:
    layer.trainable = True

print(f"Total layers in model: {len(model.layers)}")
print(f"Trainable layers: {sum(layer.trainable for layer in model.layers)}")

# -----------------------------
# DATA AUGMENTATION FOR STAGE 3
# -----------------------------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.25,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode="nearest"
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical"
)

val_gen = val_datagen.flow_from_directory(
    val_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical"
)

# -----------------------------
# COMPILE FOR LOW LR FINE-TUNING
# -----------------------------
optimizer = optimizers.Adam(learning_rate=5e-6)
model.compile(
    optimizer=optimizer,
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# -----------------------------
# CALLBACKS
# -----------------------------
callbacks = [
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.3, patience=3, verbose=1, min_lr=1e-4
    ),
    tf.keras.callbacks.ModelCheckpoint(
        "mobilenet_dermnet_finetuned_stage3.keras",
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1
    ),
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=5,
        restore_best_weights=True
    )
]

# -----------------------------
# TRAIN
# -----------------------------
print("🔥 Starting Stage 3 Full Fine-Tuning...")
history = model.fit(
    train_gen,
    epochs=epochs,
    validation_data=val_gen,
    callbacks=callbacks
)

# -----------------------------
# SAVE FINAL MODEL
# -----------------------------
model.save("mobilenet_dermnet_finetuned_stage3_final.keras")
print("✅ Stage 3 fine-tuning complete! Model saved as mobilenet_dermnet_finetuned_stage3_final.keras")
