import os 
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# if __name__=='__main__':
#   app.debug=True
#   app.run()

from keras.models import load_model 
from keras.backend import set_session
from keras.layers import LayerNormalization
from skimage.transform import resize 
import matplotlib.pyplot as plt 
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()  
import numpy as np 

print("Loading model") 
global sess
global model 
model = load_model('my_cifar10_model.h5') 
global graph
graph = tf.get_default_graph()

@app.route('/', methods=['GET', 'POST']) 
def main_page():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('prediction', filename=filename))
    return render_template('index.html')

@app.route('/prediction/<filename>') 
def prediction(filename):
    #Step 1
    my_image = plt.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #Step 2
    my_image_re = resize(my_image, (32,32,3))
    
    #Step 3
    with graph.as_default():
      sess = tf.Session() 
      set_session(sess)
      model = load_model('my_cifar10_model.h5')
      probabilities = model.predict(np.array( [my_image_re,] ))[0,:]
      print(probabilities)
      #Step 4
      number_to_class = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
      index = np.argsort(probabilities)
      predictions = {
        "class1":number_to_class[index[9]],
        "class2":number_to_class[index[8]],
        "class3":number_to_class[index[7]],
        "prob1":probabilities[index[9]],
        "prob2":probabilities[index[8]],
        "prob3":probabilities[index[7]],
      }
    #Step 5
    return render_template('predict.html', predictions=predictions, filename=filename)
    
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
app.run(host='0.0.0.0', port=80)
