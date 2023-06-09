import random
import time
import numpy as np
import torch
from ML_NPI import ML_NPI
from DataHelper import DataHelper

np.random.seed(2021)
torch.manual_seed(2021)


def training(model, model_save=True, model_file=None):
    print('training model...')
    if config['use_cuda']:
        model.cuda()
    model.train()

    batch_size = config['batch_size']
    num_epoch = config['num_epoch']
    print('num_batch: ', int(len(train_data) / batch_size))

    for _ in range(num_epoch):  # 100
        loss, acc, ap, f1, auc = [], [], [], [], []
        aupr, precision, recall, specificity = [], [], [], []

        start = time.time()

        random.shuffle(train_data)
        num_batch = int(len(train_data) / batch_size)  # ~80
        support_x, support_y, query_x, query_y = zip(*train_data)  # supp_um_s:(list,list,...,2553)
        for i in range(num_batch):  # each batch contains some tasks (each task contains a support set and a query set)
            support_xs = list(support_x[batch_size * i:batch_size * (i + 1)])
            support_ys = list(support_y[batch_size * i:batch_size * (i + 1)])
            query_xs = list(query_x[batch_size * i:batch_size * (i + 1)])
            query_ys = list(query_y[batch_size * i:batch_size * (i + 1)])

            _loss, _acc, _ap, _f1, _auc,_aupr,_precision,_recall,_specificity = model.global_update(support_xs, support_ys, query_xs, query_ys)

            loss.append(_loss)
            acc.append(_acc)
            ap.append(_ap)
            f1.append(_f1)
            auc.append(_auc)
            aupr.append(_aupr)
            precision.append(_precision)
            recall.append(_recall)
            specificity.append(_specificity)

            if i % 20 == 0 and i != 0:
                print('batch: {}, loss: {:.6f}, cost time: {:.1f}s, acc: {:.5f}, ap: {:.5f}, f1: {:.5f}, auc: {:.5f}'.
                      format(i, np.mean(loss), time.time() - start, np.mean(acc), np.mean(ap), np.mean(f1), np.mean(auc)))

        print('epoch: {}, loss: {:.6f}, cost time: {:.1f}s, acc: {:.5f}, ap: {:.5f}, f1: {:.5f}, auc: {:.5f}'.
              format(_, np.mean(loss), time.time() - start, np.mean(acc), np.mean(ap), np.mean(f1), np.mean(auc)))
        if _ % 1 == 0:
            validation(model)
            testing(model)

            model.train()

    if model_save:
        print('saving model...')
        torch.save(model.state_dict(), model_file)


def validation(model):
    # testing
    print('evaluating model...')
    if config['use_cuda']:
        model.cuda()
    model.eval()

    support_x, support_y, query_x, query_y = zip(*valid_data)

    acc, ap, f1, auc,aupr,precision,recall,specificity = model.evaluate(support_x, support_y, query_x, query_y)

    print('val acc: {:.5f}, val ap: {:.5f}, val f1: {:.5f}, val auc: {:.5f},aupr: {:.5f},precision: {:.5f},recal: {:.5f},specificity: {:.5f}'.
          format(np.mean(acc), np.mean(ap), np.mean(f1), np.mean(auc),np.mean(aupr),np.mean(precision),np.mean(recall),np.mean(specificity)))


def testing(model):
    # testing
    print('evaluating model...')
    if config['use_cuda']:
        model.cuda()
    model.eval()

    support_x, support_y, query_x, query_y = zip(*test_data)


    acc, ap, f1, auc,aupr,precision,recall,specificity = model.evaluate(support_x, support_y, query_x, query_y)

    print(
        ' acc: {:.5f},  ap: {:.5f},  f1: {:.5f},  auc: {:.5f},aupr: {:.5f},precision: {:.5f},recal: {:.5f},specificity: {:.5f}'.
        format(np.mean(acc), np.mean(ap), np.mean(f1), np.mean(auc), np.mean(aupr), np.mean(precision), np.mean(recall),
               np.mean(specificity)))



if __name__ == "__main__":

    data_set = 'npi'


    res_dir = '../res/'+data_set
    load_model = False



    model_name = 'time_interval_sp'



    from Config import config_npi as config
    e_feat = np.load('../data/{0}/ml_{0}.npy'.format(data_set))
    n_feat = np.load('../data/{0}/ml_{0}_node.npy'.format(data_set))


    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(config)

    model_filename = "{}/mdgnn.pkl".format(res_dir)
    datahelper = DataHelper(data_set, k_shots=config['k_shots'], full_node=True)

    if 'time_interval' in model_name:
        train_data, valid_data, test_data, full_ngh_finder, train_ngh_finder \
            = datahelper.load_data_in_time_sp(interval=config['interval'])
    else:
        train_data, valid_data, test_data, full_ngh_finder, train_ngh_finder = datahelper.load_data()

    our_model = ML_NPI(config, train_ngh_finder, n_feat, e_feat, model_name)

    print('--------------- {} ---------------'.format(model_name))

    if not load_model:
        # Load training dataset
        print('loading train data...')
        training(our_model, model_save=True, model_file=model_filename)
        # testing(our_model)
    else:
        trained_state_dict = torch.load(model_filename)
        our_model.load_state_dict(trained_state_dict)

    # testing
    testing(our_model)
    print('--------------- {} ---------------'.format(model_name))

