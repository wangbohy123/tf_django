import os
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# 绘制参数变化
def variable_summaries(var):
    with tf.name_scope('summaries'):
        # 计算参数的均值，并使用tf.summary.scaler记录
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean', mean)

        # 计算参数的标准差
        with tf.name_scope('stddev'):
            stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        # 使用tf.summary.scaler记录记录下标准差，最大值，最小值
        tf.summary.scalar('stddev', stddev)
        tf.summary.scalar('max', tf.reduce_max(var))
        tf.summary.scalar('min', tf.reduce_min(var))
        # 用直方图记录参数的分布
        tf.summary.histogram('histogram', var)

def convolutional(x, keep_prob):
    # 总共定义了四个隐层  一个输出层  每一层最终都进行dropout
    def conv2d(x, W):
        # 实现卷积
        # x代表输入图像矩阵 W代表卷积核
        # keep_prob 代表每个元素被保留的概率
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def max_pool_2x2(x):
        # stride [1, x_movement, y_movement, 1]
        # 接着定义池化pooling，为了得到更多的图片信息，padding时我们选的是一次一步，也就是strides[1]=strides[2]=1，这样得到的图片尺寸没有变化，
        # 而我们希望压缩一下图片也就是参数能少一些从而减小系统的复杂度，因此我们采用pooling来稀疏化参数，也就是卷积神经网络中所谓的下采样层。
        # pooling 有两种，一种是最大值池化，一种是平均值池化，本例采用的是最大值池化tf.max_pool()。池化的核函数大小为2x2，因此ksize=[1,2,2,1]，步长为2，因此strides=[1,2,2,1]:
        return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    def weight_variable(shape):
        # 权重的初始化
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def bias_variable(shape):
        # 偏置项的初始化
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)


    with tf.name_scope('first_layer'):
        # 隐层1
        # First Convolutional Layer
        # 我们需要处理我们的xs，把xs的形状变成[-1,28,28,1]，-1代表先不考虑输入的图片例子多少这个维度，
        # 后面的1是channel的数量，因为我们输入的图片是黑白的，因此channel是1，例如如果是RGB图像，那么channel就是3。
        x_image = tf.reshape(x, [-1, 28, 28, 1])
        # 卷积核patch的大小是3x3，因为黑白图片channel是1所以输入是1，输出是32个featuremap（经验值）
        W_conv1 = weight_variable([3, 3, 1, 32])  # 卷积核
        # variable_summaries(W_conv1)

        b_conv1 = bias_variable([32])
        # variable_summaries(b_conv1)

        # relu激励函数
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        # tf.summary.histogram('activations01', h_conv1)
        h_pool1 = max_pool_2x2(h_conv1)
        L1 = tf.nn.dropout(h_pool1, keep_prob=keep_prob)

    with tf.name_scope('second_layer'):
        # 隐层2
        # Second Convolutional Layer 加厚一层，图片大小14*14
        W_conv2 = weight_variable([3, 3, 32, 64])
        # variable_summaries(W_conv2)

        b_conv2 = bias_variable([64])
        # variable_summaries(b_conv2)

        h_conv2 = tf.nn.relu(conv2d(L1, W_conv2) + b_conv2)
        # tf.summary.histogram('activations02', h_conv2)
        # 池化层
        h_pool2 = max_pool_2x2(h_conv2)
        L2 = tf.nn.dropout(h_pool2, keep_prob=keep_prob)

    with tf.name_scope('third_layer'):
        # 隐层3
        # Third Convolutional Layer 加厚一层，图片大小14*14
        W_conv3 = weight_variable([3, 3, 64, 128])
        # variable_summaries(W_conv2)

        b_conv3 = bias_variable([128])
        # variable_summaries(b_conv2)

        h_conv3 = tf.nn.relu(conv2d(L2, W_conv3) + b_conv3)
        # tf.summary.histogram('activations02', h_conv2)
        # 池化层
        h_pool3 = max_pool_2x2(h_conv3)
        L3 = tf.nn.dropout(h_pool3, keep_prob=keep_prob)

    with tf.name_scope('densely_layer'):
        # 隐层4 全连接层
        # Densely Connected Layer 加厚一层，图片大小7*7
        W_fc1 = weight_variable([128 * 4 * 4, 625])
        # variable_summaries(W_fc1)

        # 特征经验 2的n次方，如32,64,1024
        b_fc1 = bias_variable([625])
        # variable_summaries(b_fc1)

        h_pool2_flat = tf.reshape(L3, [-1, 128 * 4 * 4])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
        # tf.summary.histogram('activations03', h_fc1)

        # Dropout 剪枝
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob=keep_prob)

    with tf.name_scope('output_layer'):
        # 输出层
        # Readout Layer
        W_fc2 = weight_variable([625, 10])
        # variable_summaries(W_fc2)
        b_fc2 = bias_variable([10])
        # variable_summaries(b_fc2)
        out = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
        # tf.summary.histogram('output', out)
        y = tf.nn.softmax(out)  # 最终返回是softmax分类器

    return y, [W_conv1, b_conv1, W_conv2, b_conv2, W_conv3, b_conv3, W_fc1, b_fc1, W_fc2, b_fc2]

def main():
    log_dir = 'data/log02'    # 输出日志保存的路径
    # 超参数
    learning_rate = 1e-4
    dropout = 0.7
    max_step = 10000
    data = input_data.read_data_sets("MNIST_data/", one_hot=True)

    # model
    with tf.variable_scope("convolutional"):
        x = tf.placeholder(tf.float32, [None, 784])
        #解决过拟合问题
        keep_prob = tf.placeholder(tf.float32)
        # tf.summary.scalar('dropout_keep_probability', keep_prob)
        y, variables = convolutional(x, keep_prob)

    # train
    y_ = tf.placeholder(tf.float32, [None, 10])
    cross_entropy = -tf.reduce_sum(y_ * tf.log(y))
    # tf.summary.scalar('loss', cross_entropy)

    #AdamOptimizer 数据量大，比梯度下降算法要快些
    
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)

    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    acc = 0
    saver = tf.train.Saver(variables)

    # summaries合并
    # merged = tf.summary.merge_all()


    with tf.Session() as sess:
        # 写到指定的磁盘路径中
        # train_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
        # test_writer = tf.summary.FileWriter(log_dir + '/test')

        sess.run(tf.global_variables_initializer())
        for i in range(max_step):
            batch = data.train.next_batch(50)
            if i % 100 == 0:
                train_accuracy = accuracy.eval(feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
                print("step %d, training accuracy %g" % (i, train_accuracy))
            # summary, _ = sess.run([merged, train_step], feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.8})
            # train_writer.add_summary(summary, i)
            sess.run(train_step, feed_dict={x: batch[0], y_: batch[1], keep_prob: dropout})

        # print(sess.run(accuracy, feed_dict={x: data.test.images, y_: data.test.labels, keep_prob: 1.0}))
        for j in range(1000):
            # 测试集载入
            batch_test = data.test.next_batch(100)
            # summary, s = sess.run([merged, accuracy], feed_dict={x: batch_test[0], y_: batch_test[1], keep_prob: 1.0})
            s = sess.run(accuracy, feed_dict={x: batch_test[0], y_: batch_test[1], keep_prob: 1.0})
            if j % 100 == 0:
                print(s)
            acc += s
            # test_writer.add_summary(summary, j)
        # total:0.985900010467
        print('total:' + str(acc / 1000))
        path = saver.save(
            sess, os.path.join(os.path.dirname(__file__), 'data', 'convolutional.ckpt'),
            write_meta_graph=False, write_state=False)
        print("Saved:", path)

        # train_writer.close()
        # test_writer.close()

if __name__ == '__main__':
    main()
