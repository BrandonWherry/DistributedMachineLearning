#!/bin/bash

echo "Training Model"
python3 keypointDetection_training.py | tee Results/training_g3s.xlarge.log
echo "Done with training"
python3 keypointDetection_predictions.py
echo "Done with predictions"
