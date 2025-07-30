
import random
import matplotlib.pyplot as plt
import networkx as nx
import math
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import plotly.io as pio
import math
from dataclasses import dataclass
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score
)

pio.renderers.default = 'vscode'  # Or 'notebook' or 'vscode'
random.seed(42)
np.random.seed(42)

@dataclass
class class_optimizer:
    name:str = 'null'
    mov_coff:int = 0.9
    decay_rate:int = 0.9
    

class net:
    def __init__(self, input, act:str="sigmoid",cost:str="binary",lr:int=0.05):
        self.optimizer = ''
        self.input = input  # Input is stored here
        self.velocity_weight = []
        self.velocity_bias = []
        self.network = [[0.0]*input] # Network pattern
        self.weight = [] 
        self.act_layer=[]
        self.losses = []
        self.timestep = 1 
        self.epoch_count = []
        self.bais = []
        self.activation_func = act
        self.temp_delta = 0
        self.learn_rate = lr
        self.cost_func = cost
        self.output_network = []
        self.fan_in = input
        self.temporary = []
        self.fan_out = 0
        self.batch_size = 1
        self.batch_size_count = 0
            

    
    
    def add_hidden(self, n, act: str):
        self.network.append([0.0] * n)
        self.bais.append([random.uniform(-0.5, 0.5)] * n)
        self.act_layer.append(act.lower())

        fan_in = len(self.network[-2])  # Number of neurons in previous layer
        fan_out = n  # Number of neurons in current layer
        if act.lower() in ['tanh', 'sigmoid', 'softmax']:
            limit = math.sqrt(6 / (fan_in + fan_out))
            self.weight.append([[random.uniform(-limit, limit) for _ in range(fan_in)] for _ in range(fan_out)])
        elif act.lower() == 'relu' or act.lower() == 'leaky relu':
            stddev = math.sqrt(2 / fan_in)
            self.weight.append([[random.uniform(-stddev, stddev) for _ in range(fan_in)] for _ in range(fan_out)])

    def add_output(self, n, act: str):
        self.network.append([0.0] * n)
        self.bais.append([random.uniform(-0.5, 0.5)] * n)
        self.act_layer.append(act.lower())
        self.fan_out = n
        fan_in = len(self.network[-2])
        if act.lower() in ['sigmoid', 'tanh', 'softmax']:
            limit = math.sqrt(6 / (fan_in + self.fan_out))
            self.weight.append([[random.uniform(-limit, limit) for _ in range(fan_in)] for _ in range(self.fan_out)])
        elif act.lower() == 'relu' or act.lower() == 'leaky relu':
            stddev = math.sqrt(2 / fan_in)
            self.weight.append([[random.uniform(-stddev, stddev) for _ in range(fan_in)] for _ in range(self.fan_out)])

    def weight_sum(self, weights, bias, act:str):
        total = sum(w * t for w, t in zip(weights, self.temporary)) + bias
        if act.lower() == "softmax":
            return total
        return self.activation(total, act)

    

        
    def backprob_cal(self, i, pr, tr, er, act: str):
        temp_weight = self.weight[i]
        temp_bais = self.bais[i]

        if act.lower() == 'sigmoid':

            delta = np.array(pr) - np.array(tr) # ensure 1D array
            self.temp_delta = delta
        
        elif i == len(self.weight) - 1 and act.lower() == 'softmax' and self.cost_func.lower() in ['mce', 'multiclass']:

            delta = np.array(pr) - np.array(tr)  # ensure 1D array

            self.temp_delta = delta
        elif act.lower() == 'relu':
            if i < len(self.weight) - 1:  # Hidden layer
                W_next_T = np.transpose(self.weight[i + 1])
                delta_raw = np.dot(W_next_T, self.temp_delta)
                relu_deriv = self.relu_derivative(self.output_network[i])
                delta = relu_deriv * delta_raw
                self.temp_delta = delta
            else:
                raise ValueError("ReLU should not be used for the output layer with MCE loss.")
        else:
            raise ValueError(f"Unsupported activation: {act}")
        
        
        if i == 0:
            a_prev = np.array(self.network[0])
        else:
            a_prev = np.array(self.output_network[i - 1])
        
        if self.optimizer.name == 'momentum':
            for j in range(len(temp_weight)):
                for k in range(len(temp_weight[j])):
                    grad = delta[j] * a_prev[k]
                    new_velocity = self.optimizer.mov_coff * self.velocity_weight[i][j][k]-self.learn_rate*grad
                    temp_weight[j][k] += new_velocity
                    self.velocity_weight[i][j][k] = new_velocity
                    
    
            for j in range(len(temp_bais)):
                bias_grad = delta[j]
                new_velocity_b = self.optimizer.mov_coff * self.velocity_bias[i][j] - self.learn_rate * bias_grad
                temp_bais[j] += new_velocity_b
                self.velocity_bias[i][j] = new_velocity_b
        
        elif self.optimizer.name == 'adagrad':
            epsilon = 1e-8
            for j in range(len(temp_weight)):
                for k in range(len(temp_weight[j])):
                    grad = delta[j] * a_prev[k]
                    self.grad_square_weight[i][j][k] += grad ** 2
                    adjusted_lr = self.learn_rate / (self.grad_square_weight[i][j][k] ** 0.5 + epsilon)
                    temp_weight[j][k] -= adjusted_lr * grad

            for j in range(len(temp_bais)):
                bias_grad = delta[j]
                self.grad_square_bias[i][j] += bias_grad ** 2
                adjusted_lr = self.learn_rate / (self.grad_square_bias[i][j] ** 0.5 + epsilon)
                temp_bais[j] -= adjusted_lr * bias_grad 
                
        elif self.optimizer.name == 'rmsprop':
            epsilon = 1e-8
            beta = self.rms_decay = self.optimizer.decay_rate  # usually 0.9
            for j in range(len(temp_weight)):
                for k in range(len(temp_weight[j])):
                    grad = delta[j] * a_prev[k]
                    self.grad_square_weight[i][j][k] = (
                        beta * self.grad_square_weight[i][j][k] + (1 - beta) * grad ** 2
                    )
                    adjusted_lr = self.learn_rate / (self.grad_square_weight[i][j][k] ** 0.5 + epsilon)
                    temp_weight[j][k] -= adjusted_lr * grad

            for j in range(len(temp_bais)):
                bias_grad = delta[j]
                self.grad_square_bias[i][j] = (
                    beta * self.grad_square_bias[i][j] + (1 - beta) * bias_grad ** 2
                )
                adjusted_lr = self.learn_rate / (self.grad_square_bias[i][j] ** 0.5 + epsilon)
                temp_bais[j] -= adjusted_lr * bias_grad
        
        elif self.optimizer == 'adam':
            beta1 = self.optimizer.mov_coff
            beta2 = self.optimizer.decay_rate
            epsilon = 1e-8

            for j in range(len(temp_weight)):
                for k in range(len(temp_weight[j])):
                    grad = delta[j] * a_prev[k]

                    self.m_weight[i][j][k] = beta1 * self.m_weight[i][j][k] + (1 - beta1) * grad
                    self.v_weight[i][j][k] = beta2 * self.v_weight[i][j][k] + (1 - beta2) * (grad ** 2)

                    # Compute bias-corrected first moment estimate
                    m_hat = self.m_weight[i][j][k] / (1 - beta1 ** self.timestep)
                    # Compute bias-corrected second raw moment estimate
                    v_hat = self.v_weight[i][j][k] / (1 - beta2 ** self.timestep)

                    # Update parameter
                    temp_weight[j][k] -= self.learn_rate * m_hat / (math.sqrt(v_hat) + epsilon)

            for j in range(len(temp_bais)):
                bias_grad = delta[j]

                self.m_bias[i][j] = beta1 * self.m_bias[i][j] + (1 - beta1) * bias_grad
                self.v_bias[i][j] = beta2 * self.v_bias[i][j] + (1 - beta2) * (bias_grad ** 2)

                m_hat_b = self.m_bias[i][j] / (1 - beta1 ** self.timestep)
                v_hat_b = self.v_bias[i][j] / (1 - beta2 ** self.timestep)

                temp_bais[j] -= self.learn_rate * m_hat_b / (math.sqrt(v_hat_b) + epsilon)


        
        else:
            # print("null")
            for j in range(len(temp_weight)):
                for k in range(len(temp_weight[j])):
                    grad = delta[j] * a_prev[k]
                    temp_weight[j][k] -= self.learn_rate * grad

            for j in range(len(temp_bais)):
                temp_bais[j] -= self.learn_rate * delta[j]
    
        return temp_weight, temp_bais   
    
    

        
    def visualize_network(self, network, weights, biases):
        G = nx.DiGraph()
        pos = {}
        layer_sizes = [len(layer) for layer in network]
        max_neurons = max(layer_sizes)
        y_gap = 2
        x_gap = 4

        # Step 1: Add nodes with centered y-positions
        for layer_idx, layer_size in enumerate(layer_sizes):
            y_start = (max_neurons - layer_size) * y_gap / 2
            for neuron_idx in range(layer_size):
                node_name = f"L{layer_idx}_N{neuron_idx}"
                G.add_node(node_name)
                x = layer_idx * x_gap
                y = y_start + neuron_idx * y_gap
                pos[node_name] = (x, y)

                # Label includes bias if not input layer
                if layer_idx > 0:
                    bias_val = biases[layer_idx - 1][neuron_idx]
                    G.nodes[node_name]['label'] = f"{node_name}\nb={bias_val:.2f}"
                else:
                    G.nodes[node_name]['label'] = node_name

        # Step 2: Add edges with weight labels
        for layer_idx in range(1, len(network)):
            prev_layer_size = layer_sizes[layer_idx - 1]
            curr_layer_size = layer_sizes[layer_idx]
            for curr_neuron in range(curr_layer_size):
                for prev_neuron in range(prev_layer_size):
                    from_node = f"L{layer_idx-1}_N{prev_neuron}"
                    to_node = f"L{layer_idx}_N{curr_neuron}"
                    weight_val = weights[layer_idx - 1][curr_neuron][prev_neuron]
                    G.add_edge(from_node, to_node, weight=weight_val)

        # Step 3: Draw everything
        node_labels = nx.get_node_attributes(G, 'label')
        edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}

        plt.figure(figsize=(14, 8))
        nx.draw(G, pos, with_labels=False, node_size=2000, node_color='skyblue', edge_color='gray', arrows=True)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        plt.title("Neural Network Architecture")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        


    def setup_live_plot(self):
        plt.ion()  # Turn on interactive mode
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')
        self.ax.set_xlabel("Epoch")
        self.ax.set_ylabel("Loss")
        self.ax.set_title("Live Training Loss")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_live_plot(self, epoch, loss):
        self.losses.append(loss)
        self.epoch_count.append(epoch)
        self.line.set_xdata(self.epoch_count)
        self.line.set_ydata(self.losses)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        



    
    def visualize_3d_network(self, network, weights, biases):
        layer_sizes = [len(layer) for layer in network]
        max_neurons = max(layer_sizes)
        neuron_radius = 0.2
        x_gap, y_gap, z_gap = 4, 2, 0  # Flat layers in X and Y
    
        positions = {}
        edges = []
    
        for l_idx, layer_size in enumerate(layer_sizes):
            y_start = (max_neurons - layer_size) * y_gap / 2
            for n_idx in range(layer_size):
                x = l_idx * x_gap
                y = y_start + n_idx * y_gap
                z = 0
                node = f"L{l_idx}_N{n_idx}"
                positions[node] = (x, y, z)
    
        for l in range(1, len(layer_sizes)):
            for j in range(layer_sizes[l]):
                for i in range(layer_sizes[l - 1]):
                    from_node = f"L{l - 1}_N{i}"
                    to_node = f"L{l}_N{j}"
                    edges.append((positions[from_node], positions[to_node]))
    
        xs, ys, zs, labels = [], [], [], []
        for node, (x, y, z) in positions.items():
            xs.append(x)
            ys.append(y)
            zs.append(z)
            labels.append(node)
    
        scatter = go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode='markers+text',
            text=labels,
            marker=dict(size=8, color='skyblue'),
            textposition='top center'
        )
    
        edge_x, edge_y, edge_z = [], [], []
        for (x1, y1, z1), (x2, y2, z2) in edges:
            edge_x += [x1, x2, None]
            edge_y += [y1, y2, None]
            edge_z += [z1, z2, None]
    
        lines = go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            mode='lines',
            line=dict(color='gray', width=2),
            hoverinfo='none'
        )
    
        layout = go.Layout(
            title='3D Neural Network Visualization',
            showlegend=False,
            scene=dict(
                xaxis=dict(title='Layer'),
                yaxis=dict(title='Neuron'),
                zaxis=dict(title='Depth'),
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
    
        fig = go.Figure(data=[scatter, lines], layout=layout)
        fig.show()
    
    
    def __clean__(self):
        self.output_network = []
        
    
    def __def_predict__(self, data: list):
        """
        Perform a forward pass to get the prediction for a given input.

        Args:
            data (list): Input data vector

        Returns:
            list: Final output (prediction)
        """
        if len(data) != len(self.network[0]):
            print("Input shape does not match the network input layer.")
            return None

        activations = data[:]  # Use local copy
        # print(activations,"ssss")
        for i in range(1, len(self.network)):
            layer_output = []
            for j in range(len(self.network[i])):
                z = sum(w * a for w, a in zip(self.weight[i - 1][j], activations)) + self.bais[i - 1][j]
                if i == len(self.network) - 1 and self.act_layer[i - 1] == "softmax":
                    layer_output.append(z)  # Collect pre-softmax outputs
                else:
                    layer_output.append(self.activation(z, self.act_layer[i - 1]))

            if i == len(self.network) - 1 and self.act_layer[i - 1] == "softmax":
                layer_output = self.activation(layer_output, 'softmax')

            activations = layer_output

        return activations

    
    
    def print_net(self):
        print("network = ",self.network)
        for i in range(len(self.network)):
            print(f"layer {i+1}= ",self.network[i])
        print('')
        for i in range(len(self.bais)):
            print(f"bais for layer {i+2}= ",self.bais[i])
        
        print("weights = ",self.weight)
        print('')
        for i,n in zip(self.weight,range(len(self.weight))):
            print(f"weight before layer {n+2}")
            for j in i:
                print(j)
                
    


    
    def activation(self, x, act_type):
        if act_type == 'relu':
            return max(0, x)
        elif act_type == 'sigmoid':
            x = max(min(x, 100), -100)
            return 1 / (1 + math.exp(-x))
        elif act_type == 'softmax':
            x = np.array(x)
            max_x = np.max(x)  # For stability
            exps = np.exp(x - max_x)
            sum_exps = np.sum(exps)
            return list(exps / sum_exps)

           

                
    
    
    def matrix_cal(self,weight,delta):
        return np.dot(weight,delta)
    
    def relu_cal(self,weight):
        temp = [None]*len(weight)
        for i in range(0,len(weight)):
            temp[i]= 1 if weight[i]>0 else 0
        
        return temp
            

        
    def relu_derivative(self, output):
        return np.array([1 if val > 0 else 0 for val in output])

     
    



    def backprob(self,pr,tr,er):
        '''
        pr : predicted output
        tr : true output
        '''
        delta = pr[0]-tr[0]

        
        for i in range(len(self.weight) - 1, -1, -1):
            self.weight[i], self.bais[i] = self.backprob_cal(i, pr, tr, er, self.act_layer[i])
        

        
        
    def cost_Cal(self, predicted, truth):
        """
        Calculate binary cross-entropy loss and trigger backpropagation.
    
        Args:
            predicted (list): Predicted values from the network.
            truth (list): Ground truth labels.
    
        Returns:
            float: Average loss over the batch.
        """
        epsilon = 1e-15  # To avoid log(0)
        
        if str.lower(self.cost_func) in ["binary","bce"]:
            total_loss = 0
            for i, j in zip(predicted, truth):

                # Clamp predicted value between epsilon and 1 - epsilon
                i = max(min(i, 1 - epsilon), epsilon)
                total_loss += -(j * math.log(i) + (1 - j) * math.log(1 - i))
    
            avg_loss = total_loss / len(truth)
            
            # Start backpropagation with calculated loss
            self.backprob(predicted, truth, avg_loss)
            return avg_loss
        
        elif str.lower(self.cost_func) in ["mce","multiclass"]:
            predicted = [max(min(p, 1 - epsilon), epsilon) for p in predicted]
            loss = -sum(t * math.log(p) for t, p in zip(truth, predicted))
            self.backprob(predicted, truth, loss)
            return loss


    
            

            
            
    def check_forward_P(self,val,data:list=[]):

        '''
        So the process is this:
        
        1. The input `data` is stored in a temporary variable for processing.
        2. It checks if the input size matches the input layer of the network.
           If not, it prints an error and returns.
        3. The input is set as the activation of the first layer (input layer).
        4. For each following layer (hidden + output layers):
            a. It creates an empty list `temp1` to hold the output of that layer.
            b. For each neuron in the current layer:
                - It calculates the weighted sum of inputs and adds bias.
                - It applies the activation function (via `weight_sum` method).
                - The result is stored in `temp1`.
            c. `temp1` now becomes the input (activation) for the next layer.
        5. After going through all layers, the final output is in `self.temporary`.
        6. It calculates the error between predicted and true values using the chosen cost function.
        7. Finally, it prints the input, predicted output, and the calculated error.
        '''
        
        self.temporary = data
        self.__clean__()
        if len(data) != len(self.network[0]):
            print("input shape of data does not matches !")
            return
        else:
            self.network[0] = data
        for i in range(1, len(self.network)):
            temp1 = [0] * len(self.network[i])
            for j in range(len(self.network[i])):
                temp1[j] = self.weight_sum(self.weight[i - 1][j], self.bais[i - 1][j], self.act_layer[i - 1])
            
            if self.act_layer[i - 1] == "softmax" and i == len(self.network) - 1:
                temp1 = self.activation(temp1, 'softmax')
            self.temporary = temp1
            self.output_network.append(temp1)
        

    def predict(self, test: list, label: list):

        """
        Perform a forward pass to get the prediction for a given input.

        Args:
            data (list): Input data vector
            labels (list): Input labels

        Returns:
            list: Final output (prediction)
        """
        if len(test) != len(label):
            raise "Predict error : Label and data size are not same 😑😒"
        
        
        outputs = []
        ni = []
        for data,y in zip(test,label):
            if len(data) != len(self.network[0]):
                raise f"Input shape does not match the network input layer, data {data}"

            activations =  data[:]
 
            for i in range(1, len(self.network)):
                layer_output = []
                for j in range(len(self.network[i])):
                    z = sum(w * a for w, a in zip(self.weight[i - 1][j], activations)) + self.bais[i - 1][j]
                    if i == len(self.network) - 1 and self.act_layer[i - 1] == "softmax":
                        layer_output.append(z)  # Collect pre-softmax outputs
                    else:
                        layer_output.append(self.activation(z, self.act_layer[i - 1]))

                if i == len(self.network) - 1 and self.act_layer[i - 1] == "softmax":
                    layer_output = self.activation(layer_output, 'softmax')
                
                activations =  data[:]
                    
            ni.append(activations)
            activations = layer_output.index(max(activations))
            true_class = list(y).index(1)
            outputs.append(true_class)
        print(outputs,label,"\nsss",ni)
        print("Accuracy :", accuracy_score(np.argmax(label,axis=1), outputs))
        print("Precision:", precision_score(np.argmax(label,axis=1), outputs, average='macro'))  # 'macro' for multi
        print("Recall   :", recall_score(np.argmax(label,axis=1), outputs, average='macro'))
        print("F1 Score :", f1_score(np.argmax(label,axis=1), outputs, average='macro'))
        print("Confusion Matrix:")
        print(confusion_matrix(np.argmax(label,axis=1), outputs))
        
    
    def predict(self, test: list, label: list):
        """
        Perform a forward pass to get the prediction for a given input.

        Args:
            data (list): Input data vector

        Returns:
            list: Final output (prediction)
        """
        if len(test) != len(label):
            raise "Predict error : Label and data size are not same 😑😒"
        
        arr = []
        for data,y in zip(test,label):
            activations = data[:]  # Use local copy

            for i in range(1, len(self.network)):
                layer_output = []
                for j in range(len(self.network[i])):
                    z = sum(w * a for w, a in zip(self.weight[i - 1][j], activations)) + self.bais[i - 1][j]
                    if i == len(self.network) - 1 and self.act_layer[i - 1] == "softmax":
                        layer_output.append(z)  # Collect pre-softmax outputs
                    else:
                        layer_output.append(self.activation(z, self.act_layer[i - 1]))

                if i == len(self.network) - 1 and self.act_layer[i - 1] == "softmax":
                    layer_output = self.activation(layer_output, 'softmax')

                activations = layer_output

            pred_class = activations.index(max(activations))
            y = list(y).index(1)
            arr.append(pred_class)
        print("Accuracy :", accuracy_score(np.argmax(label,axis=1), arr))
        print("Precision:", precision_score(np.argmax(label,axis=1), arr, average='macro'))  # 'macro' for multi
        print("Recall   :", recall_score(np.argmax(label,axis=1), arr, average='macro'))
        print("F1 Score :", f1_score(np.argmax(label,axis=1), arr, average='macro'))

        print("Confusion Matrix:")
        print(confusion_matrix(np.argmax(label,axis=1), arr))
        
        
        
        

    
    
    def train(self,data,labels,epochs,live_plot,optimizer:class_optimizer=class_optimizer(),batch:int=1,verbose:int=0):
        if verbose == 1:
            print("pass optimizer = ",optimizer)
        if not isinstance(optimizer,class_optimizer):
            raise 'optimizer must be a instance of class_optimizer'
            
        if optimizer.name.lower() not in ['null','momentum','adagrad','rmsprop','adam']:
            raise 'optimizer is not available, try giving momentum, adagrad, rmsprop or leave it blank'
        if optimizer.name == 'null':
            self.optimizer=optimizer
        elif optimizer.name == 'momentum':
            self.velocity_weight = [np.zeros_like(w) for w in self.weight]
            self.velocity_bias = [np.zeros_like(b) for b in self.bais]
            self.optimizer = optimizer
            print("dummy array made")
        elif optimizer.name.lower() in ['adagrad','rmsprop']:
            self.optimizer = optimizer
            self.grad_square_weight = [[[0.0 for _ in range(len(wi))] for wi in w_layer]for w_layer in self.weight]
            self.grad_square_bias = [[0.0 for _ in range(len(b_layer))]for b_layer in self.bais]
        
        elif optimizer.name.lower() == 'adam':
            self.optimizer = optimizer
            self.m_weight = [[[0.0]*len(self.network[0]) for _ in range(len(self.network[::-1][0]))] for _ in range(len(self.network))]
            self.v_weight = [[[0.0]*len(self.network[0]) for _ in range(len(self.network[::-1][0]))] for _ in range(len(self.network))]

            self.m_bias = [[0.0]*len(self.network[::-1][0]) for _ in range(len(self.network))]
            self.v_bias = [[0.0]*len(self.network[::-1][0]) for _ in range(len(self.network))]


        self.batch_size = batch
        if live_plot == 'true':
            self.setup_live_plot()
            if verbose == 1:
                print("live plot started 📈")
   
        min_loss = float("inf")
        
        if self.batch_size == 1:

            for epoch in range(epochs):
                total_loss = 0

                combined = list(zip(data, labels))     # Combine inputs and labels
                random.shuffle(combined)       # Shuffle the combined pairs
                for x, y in combined:
                    self.check_forward_P(y, x)
                    loss = self.cost_Cal(self.output_network[::-1][0], y)
                    total_loss += loss


                avg_loss = total_loss / len(data)


                if live_plot == 'true':
                    self.update_live_plot(epoch, avg_loss)

                if avg_loss < min_loss:
                    min_loss = avg_loss
                    best_epoch = epoch

                if epoch % 50 == 0:
                    preds = [np.argmax(self.predict(x)) for x in data]
                    truths = [np.argmax(y_i) for y_i in labels]
                    acc = sum(p == t for p, t in zip(preds, truths)) / len(data)
                    if verbose == 1:
                        print(f"Epoch {epoch}, Loss: {avg_loss:.4f}, Accuracy: {acc:.2%}")
            
            print(f"\n✅ Training done. Best loss = {min_loss:.4f} at epoch {best_epoch}")
            
        elif self.batch_size > 1:
            if len(data)%self.batch_size != 0:
                raise "!!! the batch size is incompatible with training set shape 😑😑😑!!!"
                return
            
            for epoch in range(epochs):
                total_loss = 0
                combined = list(zip(data, labels))     # Combine inputs and labels
                random.shuffle(combined)       # Shuffle the combined pairs
                for x, y in combined:
                    # print("x,y = ",x,y)
                    self.batch_size_count+=1
                    self.check_forward_P(y, x)
                    if self.batch_size_count%self.batch_size == 0:
                        self.batch_size_count = 0
                        # print("last = " ,self.output_network[::-1][0])we
                        loss = self.cost_Cal(self.output_network[::-1][0], y)
                        total_loss += loss
                

                avg_loss = total_loss / len(data)


                if live_plot == 'true':
                    self.update_live_plot(epoch, avg_loss)

                if avg_loss < min_loss:
                    min_loss = avg_loss
                    best_epoch = epoch

                if epoch % 50 == 0:
                    preds = [np.argmax(self.__def_predict__(x)) for x in data]
                    truths = [np.argmax(y_i) for y_i in labels]
                    acc = sum(p == t for p, t in zip(preds, truths)) / len(data)
                    if verbose == 1:
                        print(f"Epoch {epoch}, Loss: {avg_loss:.4f}, Accuracy: {acc:.2%}")

            print(f"\n✅ Training done. Best loss = {min_loss:.4f} at epoch {best_epoch}")
            
            
            
            



                
    