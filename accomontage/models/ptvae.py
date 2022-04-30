import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence
from torch.distributions import Normal
import random
import pretty_midi
import numpy as np


class RnnEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, z_dim):
        super(RnnEncoder, self).__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, batch_first=True,
                          bidirectional=True)
        self.linear_mu = nn.Linear(hidden_dim * 2, z_dim)
        self.linear_var = nn.Linear(hidden_dim * 2, z_dim)
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.z_dim = z_dim

    def forward(self, x):
        x = self.gru(x)[-1]
        x = x.transpose_(0, 1).contiguous()
        x = x.view(x.size(0), -1)
        mu = self.linear_mu(x)
        var = self.linear_var(x).exp_()
        dist = Normal(mu, var)
        return dist


class RnnDecoder(nn.Module):

    def __init__(self, input_dim=36, z_input_dim=256,
                 hidden_dim=512, z_dim=256, num_step=32):
        super(RnnDecoder, self).__init__()
        self.z2dec_hid = nn.Linear(z_dim, hidden_dim)
        self.z2dec_in = nn.Linear(z_dim, z_input_dim)
        self.gru = nn.GRU(input_dim + z_input_dim, hidden_dim,
                          batch_first=True,
                          bidirectional=False)
        self.init_input = nn.Parameter(torch.rand(36))
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.z_dim = z_dim
        self.root_out = nn.Linear(hidden_dim, 12)
        self.chroma_out = nn.Linear(hidden_dim, 24)
        self.bass_out = nn.Linear(hidden_dim, 12)
        self.num_step = num_step

    def forward(self, z_chd, inference, tfr, c=None):
        # z_chd: (B, z_chd_size)
        bs = z_chd.size(0)
        z_chd_hid = self.z2dec_hid(z_chd).unsqueeze(0)
        z_chd_in = self.z2dec_in(z_chd).unsqueeze(1)
        if inference:
            tfr = 0.
        token = self.init_input.repeat(bs, 1).unsqueeze(1)
        recon_root = []
        recon_chroma = []
        recon_bass = []

        for t in range(int(self.num_step / 4)):
            chd, z_chd_hid = \
                self.gru(torch.cat([token, z_chd_in], dim=-1), z_chd_hid)
            r_root = self.root_out(chd)  # (bs, 1, 12)
            r_chroma = self.chroma_out(chd).view(bs, 1, 12, 2).contiguous()
            r_bass = self.bass_out(chd)  # (bs, 1, 12)
            recon_root.append(r_root)
            recon_chroma.append(r_chroma)
            recon_bass.append(r_bass)

            t_root = torch.zeros(bs, 1, 12).to(z_chd.device).float()
            t_root[torch.arange(0, bs), 0, r_root.max(-1)[-1]] = 1.
            t_chroma = r_chroma.max(-1)[-1].float()
            t_bass = torch.zeros(bs, 1, 12).to(z_chd.device).float()
            t_bass[torch.arange(0, bs), 0, r_bass.max(-1)[-1]] = 1.
            token = torch.cat([t_root, t_chroma, t_bass], dim=-1)
            if t == self.num_step - 1:
                break
            teacher_force = random.random() < tfr
            if teacher_force and not inference:
                token = c[:, t].unsqueeze(1)
        recon_root = torch.cat(recon_root, dim=1)
        recon_chroma = torch.cat(recon_chroma, dim=1)
        recon_bass = torch.cat(recon_bass, dim=1)
        return recon_root, recon_chroma, recon_bass


class TextureEncoder(nn.Module):

    def __init__(self, emb_size, hidden_dim, z_dim, num_channel=10, for_contrastive=False):
        '''input must be piano_mat: (B, 32, 128)'''
        super(TextureEncoder, self).__init__()
        self.cnn = nn.Sequential(nn.Conv2d(1, num_channel, kernel_size=(4, 12),
                                           stride=(4, 1), padding=0),
                                 nn.ReLU(),
                                 nn.MaxPool2d(kernel_size=(1, 4),
                                              stride=(1, 4)))
        self.fc1 = nn.Linear(num_channel * 29, 1000)
        self.fc2 = nn.Linear(1000, emb_size)
        self.gru = nn.GRU(emb_size, hidden_dim, batch_first=True,
                          bidirectional=True)
        self.linear_mu = nn.Linear(hidden_dim * 2, z_dim)
        self.linear_var = nn.Linear(hidden_dim * 2, z_dim)
        self.emb_size = emb_size
        self.hidden_dim = hidden_dim
        self.z_dim = z_dim
        self.for_contrastive = for_contrastive

    def forward(self, pr):
        # pr: (bs, 32, 128)
        bs = pr.size(0)
        pr = pr.unsqueeze(1)
        pr = self.cnn(pr).view(bs, 8, -1)
        pr = self.fc2(self.fc1(pr))  # (bs, 8, emb_size)
        pr = self.gru(pr)[-1]
        pr = pr.transpose_(0, 1).contiguous()
        pr = pr.view(pr.size(0), -1)
        mu = self.linear_mu(pr)
        var = self.linear_var(pr).exp_()
        dist = Normal(mu, var)
        if self.for_contrastive:
            return mu, pr
        else:
            return dist


class PtvaeEncoder(nn.Module):

    def __init__(self, device, max_simu_note=16, max_pitch=127, min_pitch=0,
                 pitch_sos=128, pitch_eos=129, pitch_pad=130,
                 dur_pad=2, dur_width=5, num_step=32,
                 note_emb_size=128,
                 enc_notes_hid_size=256,
                 enc_time_hid_size=512, z_size=512):
        super(PtvaeEncoder, self).__init__()

        # Parameters
        # note and time
        self.max_pitch = max_pitch  # the highest pitch in train/val set.
        self.min_pitch = min_pitch  # the lowest pitch in train/val set.
        self.pitch_sos = pitch_sos
        self.pitch_eos = pitch_eos
        self.pitch_pad = pitch_pad
        self.pitch_range = max_pitch - min_pitch + 3  # not including pad.
        self.dur_pad = dur_pad
        self.dur_width = dur_width
        self.note_size = self.pitch_range + dur_width
        self.max_simu_note = max_simu_note  # the max # of notes at each ts.
        self.num_step = num_step  # 32
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        self.note_emb_size = note_emb_size
        self.z_size = z_size
        self.enc_notes_hid_size = enc_notes_hid_size
        self.enc_time_hid_size = enc_time_hid_size

        self.note_embedding = nn.Linear(self.note_size, note_emb_size)
        self.enc_notes_gru = nn.GRU(note_emb_size, enc_notes_hid_size,
                                    num_layers=1, batch_first=True,
                                    bidirectional=True)
        self.enc_time_gru = nn.GRU(2 * enc_notes_hid_size, enc_time_hid_size,
                                   num_layers=1, batch_first=True,
                                   bidirectional=True)
        self.linear_mu = nn.Linear(2 * enc_time_hid_size, z_size)
        self.linear_std = nn.Linear(2 * enc_time_hid_size, z_size)

    def get_len_index_tensor(self, ind_x):
        """Calculate the lengths ((B, 32), torch.LongTensor) of pgrid."""
        with torch.no_grad():
            lengths = self.max_simu_note - \
                      (ind_x[:, :, :, 0] - self.pitch_pad == 0).sum(dim=-1)
        return lengths

    def index_tensor_to_multihot_tensor(self, ind_x):
        """Transfer piano_grid to multi-hot piano_grid."""
        # ind_x: (B, 32, max_simu_note, 1 + dur_width)
        with torch.no_grad():
            dur_part = ind_x[:, :, :, 1:].float()
            out = torch.zeros(
                [ind_x.size(0) * self.num_step * self.max_simu_note,
                 self.pitch_range + 1],
                dtype=torch.float).to(self.device)

            out[range(0, out.size(0)), ind_x[:, :, :, 0].view(-1)] = 1.
            out = out.view(-1, 32, self.max_simu_note, self.pitch_range + 1)
            out = torch.cat([out[:, :, :, 0: self.pitch_range], dur_part],
                            dim=-1)
        return out

    def encoder(self, x, lengths):
        embedded = self.note_embedding(x)
        # x: (B, num_step, max_simu_note, note_emb_size)
        # now x are notes
        x = embedded.view(-1, self.max_simu_note, self.note_emb_size)
        x = pack_padded_sequence(x, lengths.view(-1), batch_first=True,
                                 enforce_sorted=False)
        x = self.enc_notes_gru(x)[-1].transpose(0, 1).contiguous()
        x = x.view(-1, self.num_step, 2 * self.enc_notes_hid_size)
        # now, x is simu_notes.
        x = self.enc_time_gru(x)[-1].transpose(0, 1).contiguous()
        # x: (B, 2, enc_time_hid_size)
        x = x.view(x.size(0), -1)
        mu = self.linear_mu(x)  # (B, z_size)
        std = self.linear_std(x).exp_()  # (B, z_size)
        dist = Normal(mu, std)
        return dist, embedded

    def forward(self, x, return_iterators=False):
        lengths = self.get_len_index_tensor(x)
        x = self.index_tensor_to_multihot_tensor(x)
        dist, embedded_x = self.encoder(x, lengths)
        if return_iterators:
            return dist.mean, dist.scale, embedded_x
        else:
            return dist, embedded_x, lengths


class PtvaeDecoder(nn.Module):

    def __init__(self, device=None, note_embedding=None,
                 max_simu_note=16, max_pitch=127, min_pitch=0,
                 pitch_sos=128, pitch_eos=129, pitch_pad=130,
                 dur_pad=2, dur_width=5, num_step=32,
                 note_emb_size=128, z_size=512,
                 dec_emb_hid_size=128,
                 dec_time_hid_size=1024, dec_notes_hid_size=512,
                 dec_z_in_size=256, dec_dur_hid_size=16):
        super(PtvaeDecoder, self).__init__()
        # Parameters
        # note and time
        self.max_pitch = max_pitch  # the highest pitch in train/val set.
        self.min_pitch = min_pitch  # the lowest pitch in train/val set.
        self.pitch_sos = pitch_sos
        self.pitch_eos = pitch_eos
        self.pitch_pad = pitch_pad
        self.pitch_range = max_pitch - min_pitch + 3  # 88, not including pad.
        self.dur_pad = dur_pad
        self.dur_width = dur_width
        self.note_size = self.pitch_range + dur_width
        self.max_simu_note = max_simu_note  # the max # of notes at each ts.
        self.num_step = num_step  # 32

        # device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        self.note_emb_size = note_emb_size
        self.z_size = z_size

        # decoder
        self.dec_z_in_size = dec_z_in_size
        self.dec_emb_hid_size = dec_emb_hid_size
        self.dec_time_hid_size = dec_time_hid_size
        self.dec_init_input = \
            nn.Parameter(torch.rand(2 * self.dec_emb_hid_size))
        self.dec_notes_hid_size = dec_notes_hid_size
        self.dur_sos_token = nn.Parameter(torch.rand(self.dur_width))
        self.dec_dur_hid_size = dec_dur_hid_size

        # Modules
        # For both encoder and decoder
        if note_embedding is None:
            self.note_embedding = nn.Linear(self.note_size, note_emb_size)
        else:
            self.note_embedding = note_embedding
        self.z2dec_hid_linear = nn.Linear(self.z_size, dec_time_hid_size)
        self.z2dec_in_linear = nn.Linear(self.z_size, dec_z_in_size)
        self.dec_notes_emb_gru = nn.GRU(note_emb_size, dec_emb_hid_size,
                                        num_layers=1, batch_first=True,
                                        bidirectional=True)
        self.dec_time_gru = \
            nn.GRU(dec_z_in_size + 2 * dec_emb_hid_size,
                   dec_time_hid_size,
                   num_layers=1, batch_first=True,
                   bidirectional=False)
        self.dec_time_to_notes_hid = nn.Linear(dec_time_hid_size,
                                               dec_notes_hid_size)
        self.dec_notes_gru = nn.GRU(dec_time_hid_size + note_emb_size,
                                    dec_notes_hid_size,
                                    num_layers=1, batch_first=True,
                                    bidirectional=False)
        self.pitch_out_linear = nn.Linear(dec_notes_hid_size, self.pitch_range)
        self.dec_dur_gru = nn.GRU(dur_width, dec_dur_hid_size,
                                  num_layers=1, batch_first=True,
                                  bidirectional=False)
        self.dur_hid_linear = nn.Linear(self.pitch_range + dec_notes_hid_size,
                                        dec_dur_hid_size)
        self.dur_out_linear = nn.Linear(dec_dur_hid_size, 2)

    def get_len_index_tensor(self, ind_x):
        """Calculate the lengths ((B, 32), torch.LongTensor) of pgrid."""
        with torch.no_grad():
            lengths = self.max_simu_note - \
                      (ind_x[:, :, :, 0] - self.pitch_pad == 0).sum(dim=-1)
        return lengths

    def index_tensor_to_multihot_tensor(self, ind_x):
        """Transfer piano_grid to multi-hot piano_grid."""
        # ind_x: (B, 32, max_simu_note, 1 + dur_width)
        with torch.no_grad():
            dur_part = ind_x[:, :, :, 1:].float()
            out = torch.zeros(
                [ind_x.size(0) * self.num_step * self.max_simu_note,
                 self.pitch_range + 1],
                dtype=torch.float).to(self.device)

            out[range(0, out.size(0)), ind_x[:, :, :, 0].view(-1)] = 1.
            out = out.view(-1, 32, self.max_simu_note, self.pitch_range + 1)
            out = torch.cat([out[:, :, :, 0: self.pitch_range], dur_part],
                            dim=-1)
        return out

    def get_sos_token(self):
        sos = torch.zeros(self.note_size)
        sos[self.pitch_sos] = 1.
        sos[self.pitch_range:] = 2.
        sos = sos.to(self.device)
        return sos

    def dur_ind_to_dur_token(self, inds, batch_size):
        token = torch.zeros(batch_size, self.dur_width)
        token[range(0, batch_size), inds] = 1.
        token = token.to(self.device)
        return token

    def pitch_dur_ind_to_note_token(self, pitch_inds, dur_inds, batch_size):
        token = torch.zeros(batch_size, self.note_size)
        token[range(0, batch_size), pitch_inds] = 1.
        token[:, self.pitch_range:] = dur_inds
        token = token.to(self.device)
        token = self.note_embedding(token)
        return token

    def decode_note(self, note_summary, batch_size):
        # note_summary: (B, 1, dec_notes_hid_size)
        # This function estimate pitch, and dur for a single pitch based on
        # note_summary.
        # Returns: est_pitch (B, 1, pitch_range), est_durs (B, 1, dur_width, 2)

        # The estimated pitch is calculated by a linear layer.
        est_pitch = self.pitch_out_linear(note_summary).squeeze(1)
        # est_pitch: (B, pitch_range)

        # The estimated dur is calculated by a 5-step gru.
        dur_hid = note_summary.transpose(0, 1)
        # dur_hid: (1, B, dec_notes_hid_size)
        dur_hid = \
            self.dur_hid_linear(torch.cat([dur_hid,
                                           est_pitch.unsqueeze(0)],
                                          dim=-1))
        token = self.dur_sos_token.repeat(batch_size, 1).unsqueeze(1)
        # token: (B, 1, dur_width)

        est_durs = torch.zeros(batch_size, self.dur_width, 2)
        est_durs = est_durs.to(self.device)

        for t in range(self.dur_width):
            token, dur_hid = self.dec_dur_gru(token, dur_hid)
            est_dur = self.dur_out_linear(token).squeeze(1)
            est_durs[:, t] = est_dur
            if t == self.dur_width - 1:
                break
            token_inds = est_dur.max(1)[1]
            token = self.dur_ind_to_dur_token(token_inds,
                                              batch_size).unsqueeze(1)
        return est_pitch, est_durs

    def decode_notes(self, notes_summary, batch_size, notes, inference,
                     teacher_forcing_ratio=0.5):
        # notes_summary: (B, 1, dec_time_hid_size)
        # notes: (B, max_simu_note, note_emb_size), ground_truth
        notes_summary_hid = \
            self.dec_time_to_notes_hid(notes_summary.transpose(0, 1))
        if inference:
            assert teacher_forcing_ratio == 0
            assert notes is None
            sos = self.get_sos_token()  # (note_size,)
            token = self.note_embedding(sos).repeat(batch_size, 1).unsqueeze(1)
            # hid: (B, 1, note_emb_size)
        else:
            token = notes[:, 0].unsqueeze(1)

        predicted_notes = torch.zeros(batch_size, self.max_simu_note,
                                      self.note_emb_size)
        predicted_notes[:, :, self.pitch_range:] = 2.
        predicted_notes[:, 0] = token.squeeze(1)  # fill sos index
        lengths = torch.zeros(batch_size)
        predicted_notes = predicted_notes.to(self.device)
        lengths = lengths.to(self.device)
        pitch_outs = []
        dur_outs = []

        for t in range(1, self.max_simu_note):
            note_summary, notes_summary_hid = \
                self.dec_notes_gru(torch.cat([notes_summary, token], dim=-1),
                                   notes_summary_hid)
            # note_summary: (B, 1, dec_notes_hid_size)
            # notes_summary_hid: (1, B, dec_time_hid_size)

            est_pitch, est_durs = self.decode_note(note_summary, batch_size)
            # est_pitch: (B, pitch_range)
            # est_durs: (B, dur_width, 2)

            pitch_outs.append(est_pitch.unsqueeze(1))
            dur_outs.append(est_durs.unsqueeze(1))
            pitch_inds = est_pitch.max(1)[1]
            dur_inds = est_durs.max(2)[1]
            predicted = self.pitch_dur_ind_to_note_token(pitch_inds, dur_inds,
                                                         batch_size)
            # predicted: (B, note_size)

            predicted_notes[:, t] = predicted
            eos_samp_inds = (pitch_inds == self.pitch_eos)
            lengths[eos_samp_inds & (lengths == 0)] = t

            if t == self.max_simu_note - 1:
                break
            teacher_force = random.random() < teacher_forcing_ratio
            if inference or not teacher_force:
                token = predicted.unsqueeze(1)
            else:
                token = notes[:, t].unsqueeze(1)
        lengths[lengths == 0] = t
        pitch_outs = torch.cat(pitch_outs, dim=1)
        dur_outs = torch.cat(dur_outs, dim=1)
        return pitch_outs, dur_outs, predicted_notes, lengths

    def decoder(self, z, inference, x, lengths, teacher_forcing_ratio1,
                teacher_forcing_ratio2):
        # z: (B, z_size)
        # x: (B, num_step, max_simu_note, note_emb_size)
        batch_size = z.size(0)
        z_hid = self.z2dec_hid_linear(z).unsqueeze(0)
        # z_hid: (1, B, dec_time_hid_size)
        z_in = self.z2dec_in_linear(z).unsqueeze(1)
        # z_in: (B, dec_z_in_size)

        if inference:
            assert x is None
            assert lengths is None
            assert teacher_forcing_ratio1 == 0
            assert teacher_forcing_ratio2 == 0
        else:
            x_summarized = x.view(-1, self.max_simu_note, self.note_emb_size)
            x_summarized = pack_padded_sequence(x_summarized, lengths.view(-1),
                                                batch_first=True,
                                                enforce_sorted=False)
            x_summarized = self.dec_notes_emb_gru(x_summarized)[-1].\
                transpose(0, 1).contiguous()
            x_summarized = x_summarized.view(-1, self.num_step,
                                             2 * self.dec_emb_hid_size)

        pitch_outs = []
        dur_outs = []
        token = self.dec_init_input.repeat(batch_size, 1).unsqueeze(1)
        # (B, 2 * dec_emb_hid_size)

        for t in range(self.num_step):
            notes_summary, z_hid = \
                self.dec_time_gru(torch.cat([token, z_in], dim=-1), z_hid)
            if inference:
                pitch_out, dur_out, predicted_notes, predicted_lengths = \
                    self.decode_notes(notes_summary, batch_size, None,
                                      inference, teacher_forcing_ratio2)
            else:
                pitch_out, dur_out, predicted_notes, predicted_lengths = \
                    self.decode_notes(notes_summary, batch_size, x[:, t],
                                      inference, teacher_forcing_ratio2)
            pitch_outs.append(pitch_out.unsqueeze(1))
            dur_outs.append(dur_out.unsqueeze(1))
            if t == self.num_step - 1:
                break

            teacher_force = random.random() < teacher_forcing_ratio1
            if teacher_force and not inference:
                token = x_summarized[:, t].unsqueeze(1)
            else:
                token = pack_padded_sequence(predicted_notes,
                                             predicted_lengths.cpu(),
                                             batch_first=True,
                                             enforce_sorted=False)
                token = self.dec_notes_emb_gru(token)[-1].\
                    transpose(0, 1).contiguous()
                token = token.view(-1, 2 * self.dec_emb_hid_size).unsqueeze(1)
        pitch_outs = torch.cat(pitch_outs, dim=1)
        dur_outs = torch.cat(dur_outs, dim=1)
        # print(pitch_outs.size())
        # print(dur_outs.size())
        return pitch_outs, dur_outs

    def forward(self, z, inference, x, lengths, teacher_forcing_ratio1,
                teacher_forcing_ratio2):
        return self.decoder(z, inference, x, lengths, teacher_forcing_ratio1,
                            teacher_forcing_ratio2)

    def recon_loss(self, x, recon_pitch, recon_dur, weights=(1, 0.5),
                   weighted_dur=False):
        pitch_loss_func = \
            nn.CrossEntropyLoss(ignore_index=self.pitch_pad)
        recon_pitch = recon_pitch.view(-1, recon_pitch.size(-1))
        #print(recon_pitch.shape)
        
        gt_pitch = x[:, :, 1:, 0].contiguous().view(-1)
        #print(gt_pitch.shape)
        pitch_loss = pitch_loss_func(recon_pitch, gt_pitch)

        dur_loss_func = \
            nn.CrossEntropyLoss(ignore_index=self.dur_pad)
        if not weighted_dur:
            recon_dur = recon_dur.view(-1, 2)
            gt_dur = x[:, :, 1:, 1:].contiguous().view(-1)
            dur_loss = dur_loss_func(recon_dur, gt_dur)
        else:
            recon_dur = recon_dur.view(-1, self.dur_width, 2)
            gt_dur = x[:, :, 1:, 1:].contiguous().view(-1, self.dur_width)
            dur0 = dur_loss_func(recon_dur[:, 0, :], gt_dur[:, 0])
            dur1 = dur_loss_func(recon_dur[:, 1, :], gt_dur[:, 1])
            dur2 = dur_loss_func(recon_dur[:, 2, :], gt_dur[:, 2])
            dur3 = dur_loss_func(recon_dur[:, 3, :], gt_dur[:, 3])
            dur4 = dur_loss_func(recon_dur[:, 4, :], gt_dur[:, 4])
            w = torch.tensor([1, 0.6, 0.4, 0.3, 0.3],
                             device=recon_dur.device).float()
            dur_loss = \
                w[0] * dur0 + \
                w[1] * dur1 + \
                w[2] * dur2 + \
                w[3] * dur3 + \
                w[4] * dur4
        loss = weights[0] * pitch_loss + weights[1] * dur_loss
        return loss, pitch_loss, dur_loss

    def emb_x(self, x):
        lengths = self.get_len_index_tensor(x)
        x = self.index_tensor_to_multihot_tensor(x)
        embedded = self.note_embedding(x)
        return embedded, lengths

    def output_to_numpy(self, recon_pitch, recon_dur):
        est_pitch = recon_pitch.max(-1)[1].unsqueeze(-1)  # (B, 32, 11, 1)
        est_dur = recon_dur.max(-1)[1]  # (B, 32, 11, 5)
        est_x = torch.cat([est_pitch, est_dur], dim=-1)  # (B, 32, 11, 6)
        est_x = est_x.cpu().numpy()
        recon_pitch = recon_pitch.cpu().numpy()
        recon_dur = recon_dur.cpu().numpy()
        return est_x, recon_pitch, recon_dur

    def pr_to_notes(self, pr, bpm=80, start=0., one_hot=False):
        pr_matrix = self.pr_to_pr_matrix(pr, one_hot)
        alpha = 0.25 * 60 / bpm
        notes = []
        for t in range(32):
            for p in range(128):
                if pr_matrix[t, p] >= 1:
                    s = alpha * t + start
                    e = alpha * (t + pr_matrix[t, p]) + start
                    notes.append(pretty_midi.Note(100, int(p), s, e))
        return notes
    
    def pr_matrix_to_note(self, pr_matrix, bpm=120, start=0):
        alpha = 0.25 * 60 / bpm
        notes = []
        for t in range(32):
            for p in range(128):
                if pr_matrix[t, p] >= 1:
                    s = alpha * t + start
                    e = alpha * (t + pr_matrix[t, p]) + start
                    notes.append(pretty_midi.Note(100, int(p), s, e))
        return notes

    def grid_to_pr_and_notes(self, grid, bpm=60., start=0.):
        if grid.shape[1] == self.max_simu_note:
            grid = grid[:, 1:]
        pr = np.zeros((32, 128), dtype=int)
        alpha = 0.25 * 60 / bpm
        notes = []
        for t in range(32):
            for n in range(10):
                note = grid[t, n]
                if note[0] == self.pitch_eos:
                    break
                pitch = note[0] + self.min_pitch
                dur = int(''.join([str(_) for _ in note[1:]]), 2) + 1
                pr[t, pitch] = min(dur, 32 - t)
                notes.append(
                    pretty_midi.Note(100, int(pitch), start + t * alpha,
                                     start + (t + dur) * alpha))
        return pr, notes

