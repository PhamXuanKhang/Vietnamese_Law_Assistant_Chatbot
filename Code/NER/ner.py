import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split

with open("/home/maianhtruong/Law_bot/Law_Chatbot/Code/NER/ner_data_8000.json", "r", encoding="utf-8") as f:
    examples = json.load(f)

token_set = set()
for ex in examples:
    token_set.update(ex["tokens"])

token2id = {"<PAD>": 0, "<UNK>": 1}
for token in sorted(token_set):
    token2id[token] = len(token2id)
id2token = {v: k for k, v in token2id.items()}

label2id = {"O": 0, "B-ARTICLE": 1, "I-ARTICLE": 2}
id2label = {v: k for k, v in label2id.items()}

class NERDataset(Dataset):
    def __init__(self, examples, token2id, label2id):
        self.examples = examples
        self.token2id = token2id
        self.label2id = label2id

    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        ex = self.examples[idx]
        tokens = ex["tokens"]
        labels = ex["labels"]
        token_ids = [self.token2id.get(t, self.token2id["<UNK>"]) for t in tokens]
        label_ids = [self.label2id[l] for l in labels]
        return torch.tensor(token_ids, dtype=torch.long), torch.tensor(label_ids, dtype=torch.long)

def pad_collate(batch):
    tokens, labels = zip(*batch)
    lengths = [len(t) for t in tokens]
    max_len = max(lengths)
    padded_tokens = []
    padded_labels = []
    for t, l in zip(tokens, labels):
        pad_len = max_len - len(t)
        padded_tokens.append(torch.cat([t, torch.zeros(pad_len, dtype=torch.long)]))
        # Sử dụng -100 cho padding label để ignore khi tính loss
        padded_labels.append(torch.cat([l, torch.full((pad_len,), -100, dtype=torch.long)]))
    return torch.stack(padded_tokens), torch.stack(padded_labels), lengths

class BiLSTM_NER(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers, num_labels, dropout=0.1):
        super(BiLSTM_NER, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.bilstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers, 
            dropout=dropout, 
            bidirectional=True, 
            batch_first=True
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, num_labels)
    
    def forward(self, input_ids):
        x = self.embedding(input_ids)
        lstm_out, _ = self.bilstm(x)
        lstm_out = self.dropout(lstm_out)
        logits = self.classifier(lstm_out)
        return logits

embedding_dim = 100
hidden_dim = 128
num_layers = 2
num_labels = len(label2id)

def load_model(model_path="bilstm_ner.pt", device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BiLSTM_NER(
        vocab_size=len(token2id),
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        num_labels=num_labels,
        dropout=0.1
    ).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def predict(query, model, token2id=token2id, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    query_tokens = query.split()
    query_token_ids = [token2id.get(tok, token2id["<UNK>"]) for tok in query_tokens]
    query_tensor = torch.tensor(query_token_ids, dtype=torch.long).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(query_tensor)  # (1, seq_len, num_labels)
        predictions = torch.argmax(logits, dim=-1).squeeze(0).tolist()
    return query_tokens, predictions

def extract_entities(tokens, predictions, id2label):
    entities = []
    current_entity = []
    for token, pred in zip(tokens, predictions):
        label = id2label[pred]
        if label == "B-ARTICLE":
            if current_entity:
                entities.append(" ".join(current_entity))
                current_entity = []
            current_entity.append(token)
        elif label == "I-ARTICLE":
            if current_entity:
                current_entity.append(token)
            else:
                current_entity.append(token)
        else:
            if current_entity:
                entities.append(" ".join(current_entity))
                current_entity = []
    if current_entity:
        entities.append(" ".join(current_entity))
    return entities

def infer(query, model_path="bilstm_ner.pt", device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(model_path, device)
    tokens, predictions = predict(query, model, device=device)
    entities = extract_entities(tokens, predictions, id2label)
    return tokens, predictions, entities

if __name__ == '__main__':
    full_dataset = NERDataset(examples, token2id, label2id)
    train_size = int(0.8 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = random_split(full_dataset, [train_size, test_size])

    batch_size = 16
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=pad_collate)
    test_loader  = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, collate_fn=pad_collate)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Thiết bị sử dụng:", device)

    learning_rate = 0.0001
    num_epochs = 10

    model = BiLSTM_NER(len(token2id), embedding_dim, hidden_dim, num_layers, num_labels, dropout=0.1).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=-100)

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0.0
        for batch_tokens, batch_labels, lengths in train_loader:
            batch_tokens = batch_tokens.to(device)
            batch_labels = batch_labels.to(device)
            optimizer.zero_grad()
            logits = model(batch_tokens)
            logits = logits.view(-1, num_labels)
            batch_labels = batch_labels.view(-1)
            loss = criterion(logits, batch_labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(train_loader)
        print(f"[Train] Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")

    model_save_path = "/home/maianhtruong/Law_bot/Law_Chatbot/Code/NER/bilstm_ner.pt"
    torch.save(model.state_dict(), model_save_path)
    print(f"Model đã được lưu tại: {model_save_path}")

    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for batch_tokens, batch_labels, lengths in test_loader:
            batch_tokens = batch_tokens.to(device)
            batch_labels = batch_labels.to(device)
            logits = model(batch_tokens)
            logits = logits.view(-1, num_labels)
            batch_labels = batch_labels.view(-1)
            loss = criterion(logits, batch_labels)
            test_loss += loss.item()
    avg_test_loss = test_loss / len(test_loader)
    print(f"\n[Test] Loss trung bình: {avg_test_loss:.4f}")

__all__ = [
    "token2id", "id2token", "label2id", "id2label",
    "embedding_dim", "hidden_dim", "num_layers", "num_labels",
    "BiLSTM_NER", "load_model", "predict", "extract_entities", "infer"
]
