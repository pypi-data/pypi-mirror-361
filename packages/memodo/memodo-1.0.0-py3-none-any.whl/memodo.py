import torch
import torch.nn as nn
import math

class TokenLerp(nn.Module):
    def __init__(self, num_channels: int, lerp_feats: int):
        super().__init__()
        self.initial = nn.Parameter(torch.randn(num_channels))
        self.premix = nn.Parameter(torch.rand(num_channels))
        self.decide = nn.Sequential(
            nn.Linear(num_channels, lerp_feats),
            nn.GELU(),
            nn.Linear(lerp_feats, num_channels),
            nn.Sigmoid()
        )
    def forward(self, x, state=None):
        """
        :param x: tensor[T, *, C]
        :param state: tensor[*, C] or None
        :return y: tensor[T, *, C]
        :return state: tensor[*, C] or None
        """
        x = x
        xf = torch.zeros_like(x)
        if state is None:
            xf[0] = self.initial
        else:
            xf[0] = state
        xf[1:] = x[:-1]
        state = x[-1]
        pm = x + (xf - x) * self.premix
        x = x + (xf - x) * self.decide(pm)
        return x, state

class DeltanetHead(nn.Module):
    def __init__(self, num_channels: int, num_feats: int):
        super().__init__()
        self.initial = nn.Parameter(torch.randn(num_feats, num_feats))
        self.A = nn.Linear(num_channels, num_feats)
        self.B = nn.Linear(num_channels, num_feats)
        nn.init.zeros_(self.B.weight)
        self.C = nn.Linear(num_channels, num_feats)
        self.D = nn.Linear(num_channels, num_feats)
        self.I = nn.Linear(num_channels, num_feats)
        self.select = nn.Linear(num_channels, num_feats)
        self.O = nn.Linear(num_feats, num_channels, bias=False)
        self.awk_safe = math.sqrt(num_feats)
    def cell(self, sel, at, bt, ct, dt, it, state):
        state = state * torch.sigmoid(it.unsqueeze(-2)) + (state @ at.unsqueeze(-1) @ bt.unsqueeze(-2)) / self.awk_safe + ct.unsqueeze(-1) @ dt.unsqueeze(-2)
        out = (sel.unsqueeze(-2) @ state).squeeze(-2)
        return out, state
    def forward(self, x, state):
        """
        :param x: tensor[T, *, C]
        :param state: tensor[*, F, F] or None
        :return y: tensor[T, *, C]
        :return state: tensor[*, F, F]
        """
        a = self.A(x)
        b = self.B(x)
        c = self.C(x)
        d = self.D(x)
        i = self.I(x)
        s = self.select(x)
        o = torch.zeros_like(s)
        if state is None:
            state = self.initial
        for t in range(a.shape[0]):
            o[t], state = self.cell(s[t], a[t], b[t], c[t], d[t], i[t], state)
        return self.O(o), state

class MemodoLayer(nn.Module):
    def __init__(
            self,
            num_channels: int = 512,
            attn_feats: list[int] = [64, 64, 64, 64, 64, 64, 64, 64],
            lerp_feats: int = 64,
            gating_feats: int = 64,
            use_residual: bool=True,
            time_dim: int=-2
        ):
        super().__init__()
        self.norm = nn.LayerNorm(num_channels)
        self.token_lerp = TokenLerp(num_channels, lerp_feats)
        self.deltanets = nn.ModuleList([
            DeltanetHead(num_channels, af) for af in attn_feats
        ])
        self.bias = nn.Parameter(torch.zeros(num_channels))
        self.use_residual = use_residual
        self.gating_res = nn.Parameter(torch.rand(num_channels))
        self.gating = nn.Sequential(
            nn.Linear(num_channels, gating_feats),
            nn.GELU(),
            nn.Linear(gating_feats, num_channels),
            nn.Sigmoid()
        )
        self.time_dim = time_dim
    def forward(self, x, state=None):
        x = x.transpose(0, self.time_dim)
        if self.use_residual:
            res = x
        x = self.norm(x)
        if state is None:
            state = [ None ] * (len(self.deltanets) + 1)
        else:
            state = list(state)
        x, state[0] = self.token_lerp(x, state[0])
        y = torch.zeros_like(x) + self.bias
        for idx, deltanet in enumerate(self.deltanets):
            y, state[idx + 1] = deltanet(y, state[idx + 1])
        y = y * self.gating(y + x * self.gating_res)
        if self.use_residual:
            return res + y, state
        return y.transpose(0, self.time_dim), state

__all__ = ["MemodoLayer"]