"""Heterogeneous GNN architectures for ownership-graph learning.

All models inherit from BaseHeteroGNN and share the same constructor signature
and forward API.  When torch and torch_geometric are not installed, a CPU-only
stub is provided so that import succeeds and tests can exercise the interface.
"""

from __future__ import annotations

from typing import Any

TORCH_AVAILABLE = False
try:
    import torch
    from torch import nn
    from torch_geometric.nn import GCNConv, HeteroConv, SAGEConv

    TORCH_AVAILABLE = True
except ImportError:
    pass


class BaseHeteroGNN:
    """Abstract base for heterogeneous GNN models.

    All concrete models implement forward() and predict_ownership_share().
    """

    def __init__(
        self,
        node_types: list[str],
        edge_types: list[tuple[str, str, str]],
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.1,
        seed: int = 42,
    ) -> None:
        self.node_types = node_types
        self.edge_types = edge_types
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.seed = seed

    def forward(
        self,
        x_dict: dict[str, Any],
        edge_index_dict: dict[tuple[str, str, str], Any],
    ) -> dict[str, Any]:
        """Run forward pass and return node embeddings.

        Args:
            x_dict: Dictionary mapping node type to feature tensor.
            edge_index_dict: Dictionary mapping edge type triple to edge index.

        Returns:
            Dictionary mapping node type to embedding tensor.
        """
        raise NotImplementedError

    def predict_ownership_share(self, graph: Any) -> Any:
        """Predict latent beneficial-ownership shares for all ownership edges.

        Args:
            graph: A HeteroData graph object (or stub dict).

        Returns:
            Tensor (or array) of predicted ownership shares in [0, 1].
        """
        raise NotImplementedError


if TORCH_AVAILABLE:

    class _TorchHeteroBase(BaseHeteroGNN, nn.Module):  # type: ignore[misc]
        """Mixin that satisfies both BaseHeteroGNN and nn.Module."""

        def __init__(
            self,
            node_types: list[str],
            edge_types: list[tuple[str, str, str]],
            hidden_dim: int = 64,
            num_layers: int = 2,
            dropout: float = 0.1,
            seed: int = 42,
            in_dim: int = 8,
        ) -> None:
            nn.Module.__init__(self)
            BaseHeteroGNN.__init__(
                self,
                node_types,
                edge_types,
                hidden_dim,
                num_layers,
                dropout,
                seed,
            )
            torch.manual_seed(seed)
            self.node_emb = nn.ModuleDict(
                {nt: nn.Linear(in_dim, hidden_dim) for nt in node_types},
            )
            self.dropout_layer = nn.Dropout(dropout)

        def _embed(self, x_dict: dict[str, Any]) -> dict[str, Any]:
            out: dict[str, Any] = {}
            for nt, x in x_dict.items():
                if nt in self.node_emb:
                    t = x if isinstance(x, torch.Tensor) else torch.tensor(x, dtype=torch.float32)
                    pad_size = self.node_emb[nt].in_features - t.shape[-1]
                    if pad_size > 0:
                        t = torch.cat([t, torch.zeros(t.shape[0], pad_size)], dim=-1)
                    elif pad_size < 0:
                        t = t[:, : self.node_emb[nt].in_features]
                    out[nt] = self.dropout_layer(torch.relu(self.node_emb[nt](t)))
                else:
                    out[nt] = x
            return out

        def predict_ownership_share(self, graph: Any) -> Any:
            self.eval()
            with torch.no_grad():
                try:
                    x_dict = {nt: graph[nt].x for nt in self.node_types if hasattr(graph[nt], "x")}
                    edge_index_dict = {
                        et: graph[et[0], et[1], et[2]].edge_index
                        for et in self.edge_types
                        if hasattr(graph[et[0], et[1], et[2]], "edge_index")
                    }
                except (AttributeError, KeyError):
                    x_dict = graph.get("node_features", {})
                    edge_index_dict = {}
                emb = self.forward(x_dict, edge_index_dict)
                if "household" in emb and "firm" in emb:
                    h = emb["household"]
                    f = emb["firm"]
                    min_n = min(h.shape[0], f.shape[0])
                    return torch.sigmoid((h[:min_n] * f[:min_n]).sum(-1))
                first = next(iter(emb.values()))
                return torch.sigmoid(first.sum(-1))

    class RGCN(_TorchHeteroBase):
        """Relational Graph Convolutional Network (Schlichtkrull et al., 2018).

        Args:
            node_types: List of node-type name strings.
            edge_types: List of (src, rel, dst) triples.
            hidden_dim: Hidden dimension for all layers.
            num_layers: Number of message-passing layers.
            dropout: Dropout probability.
            seed: Initialisation seed.
            in_dim: Input feature dimension per node type.

        Examples:
            >>> model = RGCN(["household", "firm"],
            ...              [("household", "ownership", "firm")], hidden_dim=16, seed=42)
            >>> model is not None
            True
        """

        def __init__(
            self,
            node_types: list[str],
            edge_types: list[tuple[str, str, str]],
            hidden_dim: int = 64,
            num_layers: int = 2,
            dropout: float = 0.1,
            seed: int = 42,
            in_dim: int = 8,
        ) -> None:
            super().__init__(node_types, edge_types, hidden_dim, num_layers, dropout, seed, in_dim)
            self.convs = nn.ModuleList()
            for _ in range(num_layers):
                conv = HeteroConv(
                    {et: GCNConv(-1, hidden_dim, add_self_loops=False) for et in edge_types},
                    aggr="sum",
                )
                self.convs.append(conv)

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            out = self._embed(x_dict)
            for conv in self.convs:
                out = conv(out, edge_index_dict)
                out = {k: torch.relu(v) for k, v in out.items()}
            return out

    class HeteroGAT(_TorchHeteroBase):
        """Heterogeneous Graph Attention Network.

        Args:
            node_types: List of node-type name strings.
            edge_types: List of (src, rel, dst) triples.
            hidden_dim: Hidden dimension.
            num_layers: Number of message-passing layers.
            dropout: Dropout probability.
            seed: Initialisation seed.
            in_dim: Input feature dimension.

        Examples:
            >>> model = HeteroGAT(["household", "firm"],
            ...                   [("household", "ownership", "firm")], hidden_dim=16, seed=42)
            >>> model is not None
            True
        """

        def __init__(
            self,
            node_types: list[str],
            edge_types: list[tuple[str, str, str]],
            hidden_dim: int = 64,
            num_layers: int = 2,
            dropout: float = 0.1,
            seed: int = 42,
            in_dim: int = 8,
        ) -> None:
            from torch_geometric.nn import GATConv

            super().__init__(node_types, edge_types, hidden_dim, num_layers, dropout, seed, in_dim)
            self.convs = nn.ModuleList()
            for _ in range(num_layers):
                conv = HeteroConv(
                    {
                        et: GATConv(-1, hidden_dim, heads=1, add_self_loops=False)
                        for et in edge_types
                    },
                    aggr="mean",
                )
                self.convs.append(conv)

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            out = self._embed(x_dict)
            for conv in self.convs:
                out = conv(out, edge_index_dict)
                out = {k: self.dropout_layer(torch.relu(v)) for k, v in out.items()}
            return out

    class HeteroTransformer(_TorchHeteroBase):
        """Heterogeneous Graph Transformer with type-aware self-attention.

        Args:
            node_types: List of node-type name strings.
            edge_types: List of (src, rel, dst) triples.
            hidden_dim: Hidden dimension.
            num_layers: Number of layers.
            dropout: Dropout probability.
            seed: Initialisation seed.
            in_dim: Input feature dimension.

        Examples:
            >>> model = HeteroTransformer(["household", "firm"],
            ...     [("household", "ownership", "firm")], hidden_dim=16, seed=42)
            >>> model is not None
            True
        """

        def __init__(
            self,
            node_types: list[str],
            edge_types: list[tuple[str, str, str]],
            hidden_dim: int = 64,
            num_layers: int = 2,
            dropout: float = 0.1,
            seed: int = 42,
            in_dim: int = 8,
        ) -> None:
            from torch_geometric.nn import TransformerConv

            super().__init__(node_types, edge_types, hidden_dim, num_layers, dropout, seed, in_dim)
            self.convs = nn.ModuleList()
            for _ in range(num_layers):
                conv = HeteroConv(
                    {
                        et: TransformerConv(-1, hidden_dim, heads=1, dropout=dropout)
                        for et in edge_types
                    },
                    aggr="mean",
                )
                self.convs.append(conv)

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            out = self._embed(x_dict)
            for conv in self.convs:
                out = conv(out, edge_index_dict)
                out = {k: self.dropout_layer(torch.relu(v)) for k, v in out.items()}
            return out

    class GraphSAGEHetero(_TorchHeteroBase):
        """Graph Sample and Aggregate (Hamilton et al., 2017), heterogeneous variant.

        Args:
            node_types: List of node-type name strings.
            edge_types: List of (src, rel, dst) triples.
            hidden_dim: Hidden dimension.
            num_layers: Number of layers.
            dropout: Dropout probability.
            seed: Initialisation seed.
            in_dim: Input feature dimension.

        Examples:
            >>> model = GraphSAGEHetero(["household", "firm"],
            ...     [("household", "ownership", "firm")], hidden_dim=16, seed=42)
            >>> model is not None
            True
        """

        def __init__(
            self,
            node_types: list[str],
            edge_types: list[tuple[str, str, str]],
            hidden_dim: int = 64,
            num_layers: int = 2,
            dropout: float = 0.1,
            seed: int = 42,
            in_dim: int = 8,
        ) -> None:
            super().__init__(node_types, edge_types, hidden_dim, num_layers, dropout, seed, in_dim)
            self.convs = nn.ModuleList()
            for _ in range(num_layers):
                conv = HeteroConv(
                    {et: SAGEConv(-1, hidden_dim) for et in edge_types},
                    aggr="mean",
                )
                self.convs.append(conv)

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            out = self._embed(x_dict)
            for conv in self.convs:
                out = conv(out, edge_index_dict)
                out = {k: self.dropout_layer(torch.relu(v)) for k, v in out.items()}
            return out

else:

    class RGCN(BaseHeteroGNN):  # type: ignore[no-redef]
        """CPU-only stub for RGCN when PyTorch is not installed."""

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            import numpy as np

            return {
                k: np.zeros((v.shape[0] if hasattr(v, "shape") else 1, self.hidden_dim))
                for k, v in x_dict.items()
            }

        def predict_ownership_share(self, graph: Any) -> Any:
            import numpy as np

            return np.array([0.5])

    class HeteroGAT(BaseHeteroGNN):  # type: ignore[no-redef]
        """CPU-only stub for HeteroGAT when PyTorch is not installed."""

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            import numpy as np

            return {
                k: np.zeros((v.shape[0] if hasattr(v, "shape") else 1, self.hidden_dim))
                for k, v in x_dict.items()
            }

        def predict_ownership_share(self, graph: Any) -> Any:
            import numpy as np

            return np.array([0.5])

    class HeteroTransformer(BaseHeteroGNN):  # type: ignore[no-redef]
        """CPU-only stub for HeteroTransformer when PyTorch is not installed."""

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            import numpy as np

            return {
                k: np.zeros((v.shape[0] if hasattr(v, "shape") else 1, self.hidden_dim))
                for k, v in x_dict.items()
            }

        def predict_ownership_share(self, graph: Any) -> Any:
            import numpy as np

            return np.array([0.5])

    class GraphSAGEHetero(BaseHeteroGNN):  # type: ignore[no-redef]
        """CPU-only stub for GraphSAGEHetero when PyTorch is not installed."""

        def forward(
            self,
            x_dict: dict[str, Any],
            edge_index_dict: dict[tuple[str, str, str], Any],
        ) -> dict[str, Any]:
            import numpy as np

            return {
                k: np.zeros((v.shape[0] if hasattr(v, "shape") else 1, self.hidden_dim))
                for k, v in x_dict.items()
            }

        def predict_ownership_share(self, graph: Any) -> Any:
            import numpy as np

            return np.array([0.5])


def get_model(
    architecture: str,
    node_types: list[str],
    edge_types: list[tuple[str, str, str]],
    hidden_dim: int = 64,
    num_layers: int = 2,
    dropout: float = 0.1,
    seed: int = 42,
) -> BaseHeteroGNN:
    """Factory function to instantiate a GNN by architecture name.

    Args:
        architecture: One of 'r-gcn', 'hetero-gat', 'hetero-transformer', 'graphsage'.
        node_types: List of node-type strings.
        edge_types: List of (src, rel, dst) triples.
        hidden_dim: Hidden dimension.
        num_layers: Number of message-passing layers.
        dropout: Dropout probability.
        seed: Initialisation seed.

    Returns:
        An instantiated GNN model.

    Raises:
        ValueError: If architecture is not recognised.

    Examples:
        >>> m = get_model("r-gcn", ["household"], [], hidden_dim=16, seed=42)
        >>> isinstance(m, BaseHeteroGNN)
        True
    """
    arch_map: dict[str, type[BaseHeteroGNN]] = {
        "r-gcn": RGCN,
        "hetero-gat": HeteroGAT,
        "hetero-transformer": HeteroTransformer,
        "graphsage": GraphSAGEHetero,
    }
    if architecture not in arch_map:
        raise ValueError(f"Unknown architecture '{architecture}'. Choose from {list(arch_map)}")
    cls = arch_map[architecture]
    return cls(
        node_types,
        edge_types,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        dropout=dropout,
        seed=seed,
    )
