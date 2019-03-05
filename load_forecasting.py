
# coding: utf-8

# In[1]:


from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential


# In[2]:


# define a function to convert a vector of time series into a 2D matrix
def convertSeriesToMatrix(vectorSeries, sequence_length):
    matrix=[]
    for i in range(len(vectorSeries)-sequence_length+1):
        matrix.append(vectorSeries[i:i+sequence_length])
    return matrix


# In[21]:


# random seed
np.random.seed(1234)

# load raw data
df_raw = pd.read_csv('hourly_load_2016.csv', header=None)
# numpy array
df_raw_array = df_raw.values
# plot original hourly load
plt.figure(1, figsize=(20, 5))
plt.plot(df_raw_array[:,1])
plt.xlabel('Hour')
plt.ylabel('Electricity load (*1e5)')
plt.show()

# daily load
list_daily_load = [df_raw_array[i,:] for i in range(0, len(df_raw)) if i % 24 == 0]
# plot original daily load
plt.figure(1, figsize=(20, 5))
plt.plot(np.array(list_daily_load)[:,1])
plt.xlabel('Day')
plt.ylabel('Electricity load (*1e5)')
plt.show()

# hourly load (23 loads for each day)
list_hourly_load = [df_raw_array[i,1]/100000 for i in range(0, len(df_raw)) if i % 24 != 0]

# the length of the sequnce for predicting the future value
sequence_length = 23


# In[22]:


# convert the vector to a 2D matrix
matrix_load = convertSeriesToMatrix(list_hourly_load, sequence_length)

# shift all data by mean
matrix_load = np.array(matrix_load)
shifted_value = matrix_load.mean()
matrix_load -= shifted_value
print ("Data  shape: ", matrix_load.shape)

# split dataset: 90% for training and 10% for testing
train_row = int(round(0.9 * matrix_load.shape[0]))
train_set = matrix_load[:train_row, :]

# shuffle the training set (but do not shuffle the test set)
np.random.shuffle(train_set)

# the training set: the last column is the true value to compute the mean-squared-error loss
X_train = train_set[:, :-1]
y_train = train_set[:, -1] 

# the test set
X_test = matrix_load[train_row:, :-1]
y_test = matrix_load[train_row:, -1]

# the input to LSTM layer needs to have the shape of (number of samples, the dimension of each element)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))


# In[27]:


# build the model
model = Sequential()
# layer 1: LSTM
model.add(LSTM( input_dim=1, output_dim=50, return_sequences=True))
model.add(Dropout(0.2))
# layer 2: LSTM
model.add(LSTM(output_dim=100, return_sequences=False))
model.add(Dropout(0.2))
# layer 3: dense
# linear activation: a(x) = x
model.add(Dense(output_dim=1, activation='linear'))
# compile the model
model.compile(loss="mse", optimizer="rmsprop")

# train the model
model.fit(X_train, y_train, batch_size=512, nb_epoch=50, validation_split=0.05, verbose=1)

# evaluate the result
test_mse = model.evaluate(X_test, y_test, verbose=1)
print ('\nThe mean squared error (MSE) on the test data set is %.3f over %d test samples.'%(test_mse,len(y_test)))


# In[28]:


# get the predicted values
predicted_values = model.predict(X_test)
num_test_samples = len(predicted_values)
predicted_values = np.reshape(predicted_values, (num_test_samples,1))


# In[29]:


# plot the results
fig = plt.figure(1, figsize=(20, 8))
plt.plot(y_test + shifted_value)
plt.plot(predicted_values + shifted_value)
plt.xlabel('Hour')
plt.ylabel('Electricity load (*1e5)')
plt.show()
fig.savefig('output_load_forecasting.jpg', bbox_inches='tight')

