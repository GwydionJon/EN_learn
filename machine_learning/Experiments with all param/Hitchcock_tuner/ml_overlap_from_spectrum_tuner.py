import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import kerastuner as kt
from sklearn.model_selection import train_test_split
import seaborn as sns
import os 
import glob

def plot_curve(epochs, hist, list_of_metrics,name):
    """Plot a curve of one or more classification metrics vs. epoch."""  
    plt.figure()
    plt.xlabel("Epoch "+name)
    plt.ylabel("Value")

    for m in list_of_metrics:
        x = hist[m]
        plt.plot(epochs[1:], x[1:], label=m)
    plt.legend()
    
    
def create_model_optimizer(hp):
    model = tf.keras.models.Sequential()
    
   
    
    

    first_layer=hp.Int(str('1_units'), min_value = 32, max_value = 64, step = 8)
    model.add(tf.keras.layers.Dense(units = first_layer, activation = 'relu'))
    
    second_layer=hp.Int(str('2_units'), min_value = 64, max_value = 256, step = 16)
    model.add(tf.keras.layers.Dense(units = second_layer, activation = 'relu'))

    third_layer=hp.Int(str('3_units'), min_value = 128, max_value = 2048, step = 128)
    model.add(tf.keras.layers.Dense(units = third_layer, activation = 'relu'))

    fourth_layer=hp.Int(str('4_units'), min_value = 512, max_value = 4096, step = 256)
    model.add(tf.keras.layers.Dense(units = fourth_layer, activation = 'relu'))

    fith_layer=hp.Int(str('5_units'), min_value = 128, max_value = 512, step = 32)
    model.add(tf.keras.layers.Dense(units = fith_layer, activation = 'relu'))


    six_layer=hp.Int(str('6_units'), min_value = 32, max_value = 128, step = 16)
    model.add(tf.keras.layers.Dense(units = six_layer, activation = 'relu'))



        
    hp_lr=hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
    hp_momentum=hp.Choice('momentum', values=[1e-2, 1e-1, 2e-1,5e-1,7e-1,8e-1])

    model.add(tf.keras.layers.Dense(units=15,name='Output', activation = 'relu'))                             
    model.compile(optimizer=tf.keras.optimizers.SGD(lr=hp_lr,momentum=hp_momentum),                                       
                loss=tf.keras.losses.MeanAbsoluteError(),
                metrics=[tf.keras.metrics.MeanAbsoluteError()])
    return model


def train_model(model,x_data, y_data, epochs, label_name,
                batch_size=None,shuffle=True):
    #features = {name:np.array(value) for name, value in dataset.items()}
    history = model.fit(x=x_data, y=y_data, batch_size=batch_size,
                      epochs=epochs, shuffle=shuffle,validation_split=0.2,
                       callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)])
  
    epochs = history.epoch
    hist = pd.DataFrame(history.history)
    return epochs, hist
    
    
#returns dataframe
def test_model(model,x_data, y_data ,label_name):
    evaluation=model.evaluate(x = x_data, y = y_data, batch_size=100)
    predicted = model.predict(x_data)
    df_test=pd.DataFrame(y_data,columns=[label_name])
   # print(predicted)
    df_predict=pd.DataFrame(predicted,columns=[label+"_pred" for label in label_name])
    return pd.concat([df_test,df_predict], axis=1)


dir_path = os.path.dirname(os.path.realpath(__file__))
all_labels_features=["delta","lambda","all_maxima","Intensity","overlap_s0_s2_k6a","overlap_s0_s2_k1","overlap_s0_s2_k9a"]

csv_filename=glob.glob(dir_path+"\*.csv")[0]



all_data=pd.read_csv(csv_filename)

df_feature_labels=all_data[all_labels_features]

max_no_of_peak_list=max(all_data["no_of_max"])

#convert string lists into numpy arrays in dict

all_maxima_array=np.asarray([  np.asarray([x for x in row.replace("[","").replace("]","").replace("  "," ",5).replace(" ",";").split(";") if x!=""],dtype=np.float64)     for row in df_feature_labels["all_maxima"] ])

intensity_array=np.asarray([  np.asarray([x for x in row.replace("[","").replace("]","").replace("  "," ",5).replace(" ",";").split(";") if x!=""],dtype=np.float64)     for row in df_feature_labels["Intensity"] ])

overlap_s0_s2_k6a_array=np.asarray([  np.asarray([x for x in row.replace(",","").replace("[","").replace("]","").replace("  "," ",5).replace(" ",";").split(";") if x!=""],dtype=np.float64)     for row in df_feature_labels["overlap_s0_s2_k6a"] ])

overlap_s0_s2_k1_array=np.asarray([  np.asarray([x for x in row.replace(",","").replace("[","").replace("]","").replace("  "," ",5).replace(" ",";").split(";") if x!=""],dtype=np.float64)     for row in df_feature_labels["overlap_s0_s2_k1"] ])

overlap_s0_s2_k9a_array=np.asarray([  np.asarray([x for x in row.replace(",","").replace("[","").replace("]","").replace("  "," ",5).replace(" ",";").split(";") if x!=""],dtype=np.float64)     for row in df_feature_labels["overlap_s0_s2_k9a"] ])

#pad all_maxima_array and intensity_array
all_maxima_array_padded=np.zeros((len(all_maxima_array),max_no_of_peak_list))
intensity_array_padded=np.zeros((len(intensity_array),max_no_of_peak_list))

for i in range(len(all_maxima_array)):
    for j in range(len(all_maxima_array[i])):
        all_maxima_array_padded[i][j]=all_maxima_array[i][j]
        intensity_array_padded[i][j]=intensity_array[i][j]



concat_label=np.concatenate((overlap_s0_s2_k6a_array,overlap_s0_s2_k1_array,overlap_s0_s2_k9a_array),axis=1)
concat_feature=np.concatenate((all_maxima_array_padded,intensity_array_padded),axis=1)

x_train, x_test,y_train,y_test = train_test_split( concat_feature, concat_label  ,test_size=0.20, random_state=42)

MAX_TRIALS = 2

EXECUTIONS_PER_TRIAL = 1

tuner = kt.RandomSearch(

    create_model_optimizer,

    objective='val_mean_absolute_error',

    max_trials=MAX_TRIALS,

    executions_per_trial=EXECUTIONS_PER_TRIAL,

    directory='overlap_from_spectrum_hitchcock',
    #overwrite = True,
    project_name='first Try',

    seed=12

)

tuner.search(x_train, y_train, epochs = 70, validation_data = (x_test, y_test))
best_model = tuner.get_best_models()[0]
best_model.save("saved_Models/first Try")