import torch.nn as nn
import torch
from torch.autograd import Variable
import torch.nn.functional as F

import numpy as np
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#��ȫ���Ӳ�fc��Ȩ�صȲ������г�ʼ����������⡿������û���ر����濴������
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
        w_embeding_random_intial = np.random.uniform(-1,1,size=(vocab_length ,embedding_dim))#���ȷֲ�embedding�����ʼ��
        self.word_embedding = nn.Embedding(vocab_length,embedding_dim)
        self.word_embedding.weight.data.copy_(torch.from_numpy(w_embeding_random_intial))#�����Ǽ����Ѿ�ѵ���õĴ�����
    def forward(self,input_sentence):
        """
        :param input_sentence:  a tensor ,contain several word index.
        :return: a tensor ,contain word embedding tensor
        """
        sen_embed = self.word_embedding(input_sentence)#��input_sentence���embedding��
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

        #������Ƕ���lstmģ���ˣ�����lstm��input_size��hidden_size���涨��
        self.rnn_lstm = nn.LSTM(input_size=self.word_embedding_dim,hidden_size=self.lstm_dim,num_layers=2,batch_first=True)
        ##########################################
        #������һ��ȫ���Ӳ㣬�����С������lstm������output=hidden_dim,�����С��vocab_len����self.word_embedding_dim�������ȷ�������ݺ�������Ļ�����bias���ǲ������͵ģ����Ǹо����񲻶�
        self.fc = nn.Linear(lstm_hidden_dim, vocab_len,self.word_embedding_dim)
        self.apply(weights_init) # call the weights initial function.#ȫ���Ӳ������ʼ��ȥ��

        self.softmax = nn.LogSoftmax() # the activation function.
        self.tanh = nn.Tanh()
    def forward(self,sentence,is_test = False):
        batch_input = self.word_embedding_lookup(sentence).view(1,-1,self.word_embedding_dim)#���صĴ�����
        # print(batch_input.size()) # print the size of the input
        ################################################
        # here you need to put the "batch_input"  input the self.lstm which is defined before.
        # the hidden output should be named as output, .
        # ???
        #��h��c����ʼ��Ϊ�㣬����ģ�͵õ����
        output, _ = self.rnn_lstm(batch_input, (torch.zeros(2, 1, self.lstm_dim).to(device), torch.zeros(2, 1, self.lstm_dim).to(device)))
        ################################################
        out = output.contiguous().view(-1,self.lstm_dim)#ʹ��contiguous()���x���б仯���о��Ͼ��������������contiguous()ʱ����ǿ�ƿ���һ��tensor�������Ĳ��ֺʹ�ͷ������һģһ������������tensor��ȫû����ϵ���ı�x֮�󣬶�yû��Ӱ��
        out =  F.relu(self.fc(out))
        # out =  self.tanh(self.fc(out))
        out = self.softmax(out)
        # out = self.softmax(out,dim=1)
        # out = nn.softmax(dim=1)

        if is_test:
            prediction = out[ -1, : ].view(1,-1)    #������Ҫ�������֡�
            output = prediction
        else:
           output = out #ѵ���Ļ�����ֱ���������id��ʽ
        return output