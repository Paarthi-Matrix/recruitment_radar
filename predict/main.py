from scripts.train import train_model
from scripts.predict import predict_joining_score
import numpy as np

if __name__ == "__main__":
    action = input("Enter 'train' to train the model or 'predict' for inference: ").strip().lower()

    if action == "train":
        train_model(data_path="data/train.csv")
    elif action == "predict":
        numerical_data = np.expand_dims(np.arange(0, 23), axis=0) 
        categorical_data = np.expand_dims(np.array(['Category1'] * 46), axis=0)
        
        predicted_score = predict_joining_score(numerical_data, categorical_data)
        print(f"Predicted Joining Score: {predicted_score:.2f}")
    else:
        print("Invalid action. Please choose 'train' or 'predict'.")
