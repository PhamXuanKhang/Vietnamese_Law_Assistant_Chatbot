from neo4j import GraphDatabase
import embedd_node, graph_embedd
import torch

uri = "bolt://localhost:7687"
user = "neo4j"
password = "Maianhtruong1112@"
driver = GraphDatabase.driver(uri, auth=(user, password))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with driver.session() as session:
    
    # --- Phần 1: Tạo embedding cho từng node sử dụng sBert
    embedd_node.delete_old_embeddings(session)
    entities = embedd_node.get_entities_from_neo4j(session)
    combined_texts = [f"{name} {value}" for name, value, _ in entities]
    embeddings = embedd_node.create_embeddings(combined_texts, device)
    embedd_node.save_embeddings_to_neo4j(session, entities, embeddings)
    
    # --- Phần 2: Tạo graph embedding sử dụng mô hình NAGphormer 
    graph_embedd.delete_old_graph_embeddings(session)
    nodes, edges = graph_embedd.get_graph_data_from_neo4j(session)
    data, node2idx = graph_embedd.build_pyg_data(nodes, edges)
    data = data.to(device)
    
    in_channels = data.x.shape[1]  
    hidden_channels = 128   
    out_channels = 256         
    num_layers = 3             
    heads = 8             
    dropout = 0.2              
    num_epochs = 50            
    lr = 0.001                
    K = 2        
    
    model = graph_embedd.NAGphormer(in_channels, hidden_channels, out_channels, K, num_layers, heads, dropout).to(device)
    decoder = graph_embedd.Decoder(out_channels, in_channels).to(device)
    
    model, decoder = graph_embedd.train_model(model, decoder, data, num_epochs, device, lr=lr)
    
    model.eval()
    with torch.no_grad():
        num_nodes = data.num_nodes
        edge_index = data.edge_index.to(device)
        values = torch.ones(edge_index.size(1)).to(device)
        A = torch.sparse_coo_tensor(edge_index, values, (num_nodes, num_nodes)).to_dense()
        A = A + torch.eye(num_nodes).to(device)
        D = A.sum(dim=1)
        D_inv_sqrt = torch.diag(torch.pow(D, -0.5))
        A_hat = D_inv_sqrt @ A @ D_inv_sqrt

        graph_embeddings = model(data.x, A_hat)
    
    graph_embedd.save_graph_embeddings_to_neo4j(session, nodes, node2idx, graph_embeddings)
    
    print("huấn luyện và lưu hoàn thành")
