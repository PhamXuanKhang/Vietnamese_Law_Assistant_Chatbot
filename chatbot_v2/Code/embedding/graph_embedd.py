import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data

def hop2token(X, A_hat, K):
    """
    X: [n, d] - ma trận feature ban đầu của các node.
    A_hat: [n, n] - ma trận kề chuẩn hóa (có self-loop).
    K: số bước (hop) cần tính.
    
    Trả về: XG có kích thước [n, K+1, d], trong đó XG[:, 0, :] = X (0-hop)
    và với mỗi k từ 1 đến K, XG[:, k, :] = A_hat^k * X.
    """
    tokens = [X]  # hop 0
    Xk = X
    for k in range(1, K+1):
        Xk = torch.matmul(A_hat, Xk)
        tokens.append(Xk)
    XG = torch.stack(tokens, dim=1) 
    return XG

class TransformerEncoderLayer(nn.Module):
    def __init__(self, dm, num_heads, dropout=0.1):
        super(TransformerEncoderLayer, self).__init__()
        assert dm % num_heads == 0, f"dm ({dm}) must be divisible by num_heads ({num_heads})"
        self.self_attn = nn.MultiheadAttention(embed_dim=dm, num_heads=num_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(dm)
        self.norm2 = nn.LayerNorm(dm)
        self.ffn = nn.Sequential(
            nn.Linear(dm, dm * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dm * 4, dm),
            nn.Dropout(dropout)
        )
        
    def forward(self, x):
        attn_out, _ = self.self_attn(x, x, x)
        x = self.norm1(x + attn_out)
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x

class NAGphormer(nn.Module):
    def __init__(self, in_channels, dm, out_channels, K=2, num_layers=3, num_heads=4, dropout=0.1):
        """
        in_channels: Số chiều feature ban đầu (d)
        dm: Số chiều ẩn sau khi projection (d_m) - phải chia hết cho num_heads.
        out_channels: Số chiều của embedding cuối cùng (có thể dùng cho phân loại)
        K: Số hop (tức, sẽ có K+1 token cho mỗi node)
        num_layers: Số lớp Transformer encoder
        num_heads: Số heads cho multi-head attention
        dropout: Tỷ lệ dropout
        """
        super(NAGphormer, self).__init__()
        self.K = K
        self.dm = dm
        self.proj = nn.Linear(in_channels, dm)
        
        self.transformer_layers = nn.ModuleList([
            TransformerEncoderLayer(dm, num_heads, dropout=dropout) for _ in range(num_layers)
        ])
        
        self.attn_readout = nn.Linear(2 * dm, 1)
        
        self.out_linear = nn.Linear(dm, out_channels)
        
    def forward(self, X, A_hat):
        n = X.size(0)
        XG = hop2token(X, A_hat, self.K)

        XG = XG.view(-1, XG.size(-1))
        XG = self.proj(XG)
        XG = XG.view(n, self.K + 1, self.dm)
        
        for layer in self.transformer_layers:
            XG = layer(XG)  
        
        Z0 = XG[:, 0, :]   
        Zk = XG[:, 1:, :]    
        
        Z0_exp = Z0.unsqueeze(1).expand(-1, self.K, -1)
        attn_input = torch.cat([Z0_exp, Zk], dim=-1)
        attn_scores = self.attn_readout(attn_input)
        attn_weights = F.softmax(attn_scores, dim=1)
        weighted_sum = torch.sum(attn_weights * Zk, dim=1) 
        
        Z_out = Z0 + weighted_sum 
        
        out = self.out_linear(Z_out)
        return out

class Decoder(nn.Module):
    def __init__(self, out_channels, in_channels):
        super(Decoder, self).__init__()
        self.linear = nn.Linear(out_channels, in_channels)
    
    def forward(self, x):
        return self.linear(x)

def delete_old_graph_embeddings(session):
    query = """
    MATCH (n)
    REMOVE n.graph_embedding
    """
    session.run(query)
    print("Đã xóa các giá trị graph_embedding cũ trong Neo4j")

def get_graph_data_from_neo4j(session):
    query_nodes = "MATCH (n) RETURN n.ten AS name"
    result = session.run(query_nodes)
    nodes = [record["name"] for record in result]
    
    query_edges = "MATCH (n)-[r]->(m) RETURN n.ten AS source, m.ten AS target"
    result = session.run(query_edges)
    edges = [(record["source"], record["target"]) for record in result]
    return nodes, edges

def build_pyg_data(nodes, edges):
    node2idx = {node: idx for idx, node in enumerate(nodes)}
    
    edge_index = []
    for source, target in edges:
        if source in node2idx and target in node2idx:
            edge_index.append([node2idx[source], node2idx[target]])
            edge_index.append([node2idx[target], node2idx[source]])
    if len(edge_index) == 0:
        edge_index = torch.empty((2, 0), dtype=torch.long)
    else:
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    
    num_nodes = len(nodes)
    x = torch.eye(num_nodes, dtype=torch.float)
    
    data = Data(x=x, edge_index=edge_index)
    return data, node2idx

def save_graph_embeddings_to_neo4j(session, nodes, node2idx, embeddings):
    embeddings_np = embeddings.detach().cpu().numpy()
    for node in nodes:
        idx = node2idx[node]
        emb = embeddings_np[idx].tolist()
        query = """
        MATCH (n) WHERE n.ten = $node_name
        SET n.graph_embedding = $embedding
        """
        session.run(query, node_name=node, embedding=emb)
    print("Graph embeddings đã được lưu vào db")

def train_model(model, decoder, data, num_epochs, device, lr=0.01):
    model.train()
    decoder.train()
    optimizer = torch.optim.Adam(list(model.parameters()) + list(decoder.parameters()), lr=lr)
    loss_fn = nn.MSELoss()
    
    x = data.x.to(device)
    num_nodes = data.num_nodes
    edge_index = data.edge_index.to(device)
    values = torch.ones(edge_index.size(1)).to(device)
    A = torch.sparse_coo_tensor(edge_index, values, (num_nodes, num_nodes)).to_dense()
    A = A + torch.eye(num_nodes).to(device)
    D = A.sum(dim=1)
    D_inv_sqrt = torch.diag(torch.pow(D, -0.5))
    A_hat = D_inv_sqrt @ A @ D_inv_sqrt
    
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        out = model(x, A_hat)    
        reconstructed = decoder(out)  
        loss = loss_fn(reconstructed, x)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")
    
    return model, decoder
