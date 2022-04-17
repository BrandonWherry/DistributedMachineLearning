import json
import os

tf_config = {
    'cluster': {
        'worker': ['172.31.29.52:4000', '172.31.30.246:4001']
    },
    'task': {'type': 'worker', 'index': 0}
}

os.environ['TF_CONFIG'] = json.dumps(tf_config)

print(os.environ['TF_CONFIG'])

import time
import tensorflow as tf
import keypoint_setup
import matplotlib.pyplot as plt

now = time.time()

per_worker_batch_size = 128

num_workers = len(tf_config['cluster']['worker'])

print(os.environ['TF_CONFIG'])

strategy = tf.distribute.MultiWorkerMirroredStrategy()

print("Made it past strategy")

global_batch_size = per_worker_batch_size * num_workers

# The following line tells tf to partition the data based on global batch size
multi_worker_dataset = keypoint_setup.keypoint_dataset(global_batch_size)

print("Made it past data parallelization")

with strategy.scope():
    # Model building/compiling need to be within `strategy.scope()`
    # This enables the MultiWorker strategy
    multi_worker_model = keypoint_setup.build_and_compile_cnn_model()

later = time.time()
difference = later - now
print("\nInitialization time: {}\n".format(difference))
now = time.time()

multi_worker_model.fit(multi_worker_dataset, epochs=100, steps_per_epoch=25)

later = time.time()
difference = later - now
print("\nTraining time: {}\n".format(difference))

# No need to save model
# save_path = "SavedModel/keyPointModel"
# multi_worker_model.save(save_path)

results_dir = "Results/"

plt.plot(multi_worker_model.history.history['mae'])
plt.title('Mean Absolute Error')
plt.ylabel('mae')
plt.xlabel('# epochs')
plt.savefig(results_dir + 'mae.png', bbox_inches='tight')
plt.clf()
plt.plot(multi_worker_model.history.history['accuracy'])
plt.title('Training Accuracy')
plt.ylabel('acc')
plt.xlabel('# epochs')
plt.savefig(results_dir + 'acc.png', bbox_inches='tight')
