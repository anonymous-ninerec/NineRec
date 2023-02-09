import torch
from torch import nn
from .encoders import Bert_Encoder, UserEncoder_sasrec, UserEncoder_nextitnet, UserEncoder_gru4rec
from torch.nn.init import xavier_normal_


class Model(torch.nn.Module):
    def __init__(self, args, item_num, use_modal, nlp_model):
        super(Model, self).__init__()
        self.args = args
        self.use_modal = use_modal
        self.max_seq_len = args.max_seq_len
        self.model_tower = args.model_tower

        if 'sasrec' in self.model_tower:
            self.user_encoder = UserEncoder_sasrec(
                item_num=item_num,
                max_seq_len=args.max_seq_len,
                item_dim=args.embedding_dim,
                num_attention_heads=args.num_attention_heads,
                dropout=args.drop_rate,
                n_layers=args.block_num)

        elif 'nextitnet' in self.model_tower:
            self.user_encoder = UserEncoder_nextitnet(
                args=args,
                item_num=item_num)

        elif 'gru4rec' in self.model_tower:
            self.user_encoder = UserEncoder_gru4rec(
                args=args)

        if self.use_modal:
            self.nlp_encoder = Bert_Encoder(args=args, nlp_model=nlp_model)
        else:
            self.id_embedding = nn.Embedding(item_num + 1, args.embedding_dim, padding_idx=0)
            xavier_normal_(self.id_embedding.weight.data)
        self.criterion = nn.BCEWithLogitsLoss()

    def forward(self, sample_items, log_mask, local_rank, batch_index):
        # if batch_index % 1000 == 0:
        #     print(f'======================================== batch {batch_index} ========================================')

        if self.use_modal:
            input_embs_all = self.nlp_encoder(sample_items)
        else:
            input_embs_all = self.id_embedding(sample_items)

        input_embs = input_embs_all.view(-1, self.max_seq_len + 1, 2, self.args.embedding_dim)
        pos_items_embs = input_embs[:, :, 0]
        neg_items_embs = input_embs[:, :, 1]

        input_logs_embs = pos_items_embs[:, :-1, :]
        target_pos_embs = pos_items_embs[:, 1:, :]
        target_neg_embs = neg_items_embs[:, :-1, :]

        # user encoder
        if 'sasrec' in self.model_tower:
            prec_vec = self.user_encoder(input_logs_embs, log_mask, local_rank)

        elif 'nextitnet' in self.model_tower:
            prec_vec = self.user_encoder(input_logs_embs)

        elif 'gru4rec' in self.model_tower:
            prec_vec = self.user_encoder(input_logs_embs)

        pos_score = (prec_vec * target_pos_embs).sum(-1)
        neg_score = (prec_vec * target_neg_embs).sum(-1)

        pos_labels, neg_labels = torch.ones(pos_score.shape).to(local_rank), torch.zeros(neg_score.shape).to(local_rank)
        indices = torch.where(log_mask != 0)
        loss = self.criterion(pos_score[indices], pos_labels[indices]) + \
            self.criterion(neg_score[indices], neg_labels[indices])
        return loss
