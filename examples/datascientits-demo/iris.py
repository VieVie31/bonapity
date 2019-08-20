import numpy as np

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

from bonapity import bonapity

class IrisDataset:
    iris_dataset = load_iris()

    x_data = iris_dataset['data']
    y_data = iris_dataset['target']

    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data)

    pca = PCA(2).fit(x_train)

class MyRFModel:
    clf = RandomForestClassifier().fit(
        IrisDataset.x_train, IrisDataset.y_train)

    @bonapity
    def retrain(nb_tree: int = 10) -> None:
        """
        Retrain the random forest classifier model.

        :param nb_tree: number of trees in the RF (default 10)
        """
        model = RandomForestClassifier(nb_tree).fit(
            IrisDataset.x_train, IrisDataset.y_train)
        bonapity.session["user_model"] = model

    @bonapity
    def model_acc() -> float:
        """
        Know the model accuracy on the test base.
        """
        model = bonapity.session["user_model"] if "user_model" in bonapity.session else MyRFModel.clf
        return (model.predict(IrisDataset.x_test) == IrisDataset.y_test).mean()

    @bonapity
    def predict_one_sample(
            sepal_length: float, sepal_width: float, 
            petal_length: float, petal_width: float) -> int:
        """
        Predict the class of a given class
        """
        model = model = bonapity.session["user_model"] if "user_model" in bonapity.session else MyRFModel.clf
        pred = model.predict([[
            sepal_length, sepal_width, petal_length, petal_width
        ]])[0]
        return pred

if __name__ == "__main__":
    bonapity.serve(index="iris.html")
