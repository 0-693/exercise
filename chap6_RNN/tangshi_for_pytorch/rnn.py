import torch.nn as nn
import torch
from torch.autograd import Variable
import torch.nn.functional as F

import numpy as np
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#对全连接层fc的权重等参数进行初始化【个人理解】，这里没有特别认真看。。。
def weights_init(m):
    classname = m.__class__.__name__  #   obtain the class name
    if classname.find('Linear') != -1:
        weight_shape = list(m.weight.data.size())
        fan_in = weight_shape[1]
        fan_out = weight_shape[0]
        w_bound = np.sqrt(6. / (fan_in + fan_out))
        m.weight.data.uniform_(-w_bound, w_bound)
        m.bias.data.fill_(0)
        print("inital  linear weight ")

class word_embedding(nn.Module):
    def __init__(self,vocab_length , embedding_dim):
        super(word_embedding, self).__init__()
        w_embeding_random_intial = np.random.uniform(-1,1,size=(vocab_length ,embedding_dim))#均匀分布embedding随机初始化
        self.word_embedding = nn.Embedding(vocab_length,embedding_dim)
        self.word_embedding.weight.data.copy_(torch.from_numpy(w_embeding_random_intial))#好像是加载已经训练好的词向量
    def forward(self,input_sentence):
        """
        :param input_sentence:  a tensor ,contain several word index.
        :return: a tensor ,contain word embedding tensor
        """
        sen_embed = self.word_embedding(input_sentence)#把input_sentence变成embedding吧
        return sen_embed


class RNN_model(nn.Module):
    def __init__(self, batch_sz ,vocab_len ,word_embedding,embedding_dim, lstm_hidden_dim):
        super(RNN_model,self).__init__()

        self.word_embedding_lookup = word_embedding
        self.batch_size = batch_sz
        self.vocab_length = vocab_len
        self.word_embedding_dim = embedding_dim
        self.lstm_dim = lstm_hidden_dim
        
        #########################################
        # here you need to define the "self.rnn_lstm"  the input size is "embedding_dim" and the output size is "lstm_hidden_dim"
        # the lstm should have two layers, and the  input and output tensors are provided as (batch, seq, feature)
        # ???
        # for name, param in self.rnn.named_parameters():
        #     nn.init.uniform_(param,-0.1,0.1)

        #这里就是定义lstm模型了，两层lstm，input_size、hidden_size都规定了
        self.rnn_lstm = nn.LSTM(input_size=self.word_embedding_dim,hidden_size=self.lstm_dim,num_layers=2,batch_first=True)
        ##########################################
        #这里是一个全连接层，输入大小是上面lstm出来的output=hidden_dim,输出大小是vocab_len，【self.word_embedding_dim】这个不确定，根据函数定义的话他是bias，是布尔类型的，但是感觉好像不对
        self.fc = nn.Linear(lstm_hidden_dim, vocab_len,self.word_embedding_dim)
        self.apply(weights_init) # call the weights initial function.#全连接层参数初始化去啦

        self.softmax = nn.LogSoftmax() # the activation function.
        self.tanh = nn.Tanh()
    def forward(self,sentence,is_test = False):
        batch_input = self.word_embedding_lookup(sentence).view(1,-1,self.word_embedding_dim)#加载的词向量
        # print(batch_input.size()) # print the size of the input
        ################################################
        # here you need to put the "batch_input"  input the self.lstm which is defined before.
        # the hidden output should be named as output, .
        # ???
        #将h、c都初始化为零，进入模型得到输出
        output, _ = self.rnn_lstm(batch_input, (torch.zeros(2, 1, self.lstm_dim).to(device), torch.zeros(2, 1, self.lstm_dim).to(device)))
        ################################################
        out = output.contiguous().view(-1,self.lstm_dim)#使用contiguous()针对x进行变化，感觉上就是深拷贝。当调用contiguous()时，会强制拷贝一份tensor，让它的布局和从头创建的一模一样，但是两个tensor完全没有联系。改变x之后，对y没有影响
        out =  F.relu(self.fc(out))
        # out =  self.tanh(self.fc(out))
        out = self.softmax(out)
        # out = self.softmax(out,dim=1)
        # out = nn.softmax(dim=1)

        if is_test:
            prediction = out[ -1, : ].view(1,-1)    #测试需要看看汉字。
            output = prediction
        else:
           output = out #训练的话，就直接输出数字id形式
        return output