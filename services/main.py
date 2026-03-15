print("🔥 Script started")

import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt

print("✅ Imports successful")

# ✅ Dataset paths
BASE_DIR = r"C:\Users\Navya\Desktop\sparsha\dataset"
DERMNET_TRAIN = os.path.join(BASE_DIR, "Dermnet", "train")
DERMNET_TEST  = os.path.join(BASE_DIR, "Dermnet", "test")
print(f"✅ Paths set:\nTrain: {DERMNET_TRAIN}\nTest: {DERMNET_TEST}")

# ✅ Parameters
IMG_SIZE = (128, 128)
BATCH_SIZE = 8
EPOCHS = 10
print("✅ Parameters defined")

# ✅ Data generators
try:
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        validation_split=0.2
    )
    print("✅ ImageDataGenerator created")
except Exception as e:
    print("❌ Error creating ImageDataGenerator:", e)

try:
    train_gen = train_datagen.flow_from_directory(
        DERMNET_TRAIN,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        subset='training'
    )
    print("✅ Training generator ready")
except Exception as e:
    print("❌ Error creating training generator:", e)

try:
    val_gen = train_datagen.flow_from_directory(
        DERMNET_TRAIN,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        subset='validation'
    )
    print("✅ Validation generator ready")
except Exception as e:
    print("❌ Error creating validation generator:", e)

# ✅ Model (MobileNetV2)
try:
    base_model = MobileNetV2(include_top=False, input_shape=IMG_SIZE + (3,), weights='imagenet')
    base_model.trainable = False
    print("✅ MobileNetV2 base model loaded")

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(train_gen.num_classes, activation='softmax')
    ])
    print("✅ Model built successfully")

    model.compile(
        optimizer=Adam(1e-4),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print("✅ Model compiled")
except Exception as e:
    print("❌ Error building model:", e)

# ✅ Callbacks
try:
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
        ModelCheckpoint('mobilenet_dermnet_model.keras', save_best_only=True)
    ]
    print("✅ Callbacks defined")
except Exception as e:
    print("❌ Error creating callbacks:", e)

# ✅ Training section
if __name__ == "__main__":
    print("🚀 Starting training...")
    try:
        history = model.fit(
            train_gen,
            epochs=EPOCHS,
            validation_data=val_gen,
            callbacks=callbacks
        )
        print("✅ Training complete")

        # ✅ Plot accuracy & loss
        plt.figure(figsize=(12,5))
        plt.subplot(1,2,1)
        plt.plot(history.history['accuracy'], label='Train')
        plt.plot(history.history['val_accuracy'], label='Val')
        plt.title('Accuracy')
        plt.legend()

        plt.subplot(1,2,2)
        plt.plot(history.history['loss'], label='Train')
        plt.plot(history.history['val_loss'], label='Val')
        plt.title('Loss')
        plt.legend()
        plt.show()

        # ✅ Save model
        model.save("mobilenet_dermnet_model_final.keras")
        print("💾 Model saved successfully at mobilenet_dermnet_model_final.keras")
    except Exception as e:
        print("❌ Error during training:", e)

print("✅ End of script reached")
