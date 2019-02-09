import os
import tensorflow as tf


class Predictor():
    """ A session wrapper which predicts catness given an image.

    Argument:
        path: path to optimized frozen pb.
        node_name_path: path to input / output node names of the frozen pb.
    """

    def __init__(self, path, node_name_path="node_names.txt"):
        with open(node_name_path) as f:
            node_names = f.read().splitlines()
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)
        gd = tf.GraphDef()
        with tf.gfile.GFile(path, 'rb') as f:
            gd.ParseFromString(f.read())
        with self.graph.as_default():
            tf.import_graph_def(gd, name='')
        self.graph.finalize()
        self.input = self.graph.get_tensor_by_name("%s:0" % node_names[0])
        self.output = self.graph.get_tensor_by_name("%s:0" % node_names[1])

    def predict(self, file_path):
        """ Predict catness given an image.

        Argument:
            file_path: path to desired image file.

        Returns:
            prob: catness given the image.
                  >0: cat
                  <=0: dog
        """
        return self.sess.run(self.output, {self.input: file_path})


def gen_kaggle_sub(model_path):
    import numpy as np

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    fpaths = [os.path.join('datasets', 'test1', '%d.jpg' % i) for i in range(1, 12501)]
    number = [i for i in range(1, 12501)]
    out_f = ['id,label']
    p = Predictor(model_path)
    for idx, fpath in zip(number, fpaths):
        pred = 1 - sigmoid(p.predict(fpath))
        print(fpath, pred, end='\033[K\r')
        out_f.append("%d,%f" % (idx, pred))
    print(fpath, pred)
    with open('submission.csv', 'w') as f:
        f.write("\n".join(out_f))
    print('\nDone')


if __name__ == '__main__':
    import sys
    gen_kaggle_sub(sys.argv[1])
