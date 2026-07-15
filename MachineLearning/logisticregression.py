# from sklearn import datasets
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# # 1. Generate the data (your starter code)
# x, y = datasets.make_blobs(n_samples=1000, centers=2, n_features=2, center_box=(0, 10))

# # 2. Split into training and test sets
# x_train, x_test, y_train, y_test = train_test_split(
#     x, y, test_size=0.2, random_state=42
# )

# # 3. Create and train the logistic regression model
# model = LogisticRegression()
# model.fit(x_train, y_train)

# # 4. Make predictions on the test set
# y_pred = model.predict(x_test)

# # 5. Evaluate the model
# acc = accuracy_score(y_test, y_pred)
# print(f"Accuracy: {acc:.3f}")
# print(confusion_matrix(y_test, y_pred))
# print(classification_report(y_test, y_pred))

import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from array import array
 
def h(x,theta):
    """
    logistic regression hypothesis function
    """
    e=2.71828
    return e**(np.dot(x,theta))/(1.+e**(np.dot(x,theta)))
 
def lr_gd(a, x, y, ep=0.001, max_iter=1000, debug=True):
    #if we are debugging, we'll collect the error at each iteration
    if debug: err = array('f',[])
   
    ### Initialize the algorithm state ###
    cvg = False
    m = 0
    m,n = x.shape
    z = np.arange(m)
    #intialize the parameter/weight vector
    theta = np.random.random(n)
   
    #for each training example, compute the gradient
    z = [(y[i]-h(x[i],theta))*x[i] for i in range(n)]
 
    #update the parameters
    theta = theta + a * sum(z)
   
    #compute the total error
    pe = sum([(y[i]-h(x[i],theta))**2 for i in range(n)])
   
    ### Iterate until convergence or max iterations ###
    for t in range(max_iter):
        z = [(y[i]-h(x[i],theta))*x[i] for i in range(n)]
        theta = theta + a*sum(z)
        e = sum([(y[i]-h(x[i],theta))**2 for i in range(n)])
        if debug: err.append(e)
        if abs(pe-e) <= ep:
            print ('*** Converged, iterations: ', m, ' ***')
            cvg = True
        pe = e
        m+=1
        if m == max_iter:
            print ('*** Max interactions exceeded ***')
            break
    if debug:
        return (t,err)
    else:
        return (t)
 
if __name__ == '__main__':
    #learning rate
    a = 0.0001
    #generate linear seperate data
    X, y = datasets.make_blobs(n_samples=1000, centers=2, n_features=2, center_box=(0, 10))
    #seperate training set and test set
    xtrain = X[0:799]
    ytrain = y[0:799]
    xtest = X[800:999]
    ytest = y[800:999]
    #learning the model
    theta,err = lr_gd(a,xtrain,ytrain)
    print('GD:',theta)
    #measure the total error, print and plot results
    results = sum([(ytest[i]-np.dot(theta,xtest[i]))**2 for i in range(xtest.shape[0])])
    print ('Total BGD error: ', results)
   
    #plot the error
    plt.plot(err, linewidth=2)
    plt.xlabel('Iteration, i', fontsize=24)
    plt.ylabel(r'J($\theta$)', fontsize=24)
    plt.figure()
    #plot predictions
    plt.plot(xtest, [np.dot(theta,i) for i in xtest], 'b-', linewidth=2, label='Model')
    #plot data
    plt.figure()
    plt.plot(X[:, 0][y == 0], X[:, 1][y == 0], 'g^')
    plt.plot(X[:, 0][y == 1], X[:, 1][y == 1], 'bs')
    plt.show()

