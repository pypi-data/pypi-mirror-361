def prac_2():
  print("""
# practical 2 - Scrape an online Social Media Site for Data. Use python to scrape information from twitter.Exploratory Data Analysis and visualization of Social Media Data
# pip install pandas matplotlib seaborn wordcloud
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
# 1. Create Dummy Twitter Data
data = {
'username': ['user1', 'user2', 'user3', 'user1', 'user4', 'user2', 'user5'],
'tweet': [
'I love Python programming! #coding',
'Python is great for data science. #Python',
'Just posted a photo on Instagram!',
'Working on a new AI project. #AI',
'Check out my new blog post! #blogging',
'Data visualization is amazing! #DataViz',
'Feeling happy today! #life'
],
'likes': [10, 25, 5, 30, 15, 22, 3],
'retweets': [2, 5, 0, 4, 1, 3, 0],
'timestamp': pd.date_range(start='2025-06-01', periods=7, freq='D')
}
df = pd.DataFrame(data)
# 2. Show Basic Info
print("Basic Info:")
print(df.info())
print("\nFirst 5 rows:")
print(df.head())
# 3. Most Active Users
print("\nTweet count by user:")
print(df['username'].value_counts())
# 4. Average Likes and Retweets
print("\nAverage likes:", df['likes'].mean())
print("Average retweets:", df['retweets'].mean())
# 5. Scatter Plot: Likes vs Retweets
sns.scatterplot(data=df, x='likes', y='retweets', hue='username')
plt.title("Likes vs Retweets")
plt.show()
# 6. Tweets Over Time
df['timestamp'].value_counts().sort_index().plot(kind='bar')
plt.title("Tweets Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Tweets")
plt.show()
# 7. Word Cloud from Tweets
all_text = ' '.join(df['tweet'])
wordcloud = WordCloud(width=800, height=400,
background_color='white').generate(all_text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Tweet WordCloud")
plt.show()
  """)


def prac_3():
  print("""
# Practical 3
# Aim: Create sociograms for the persons-by-persons network and the community-by- community
# network for a given relevant problem. Create a one-mode network and two- node network for the
# same. Datasets: les-Misérables, Airlines, Internet Core Routers.

# pip install networkx matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
# Data
persons = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
person_edges = [
 ('Alice', 'Bob'),
 ('Alice', 'Charlie'),
 ('Bob', 'David'),
 ('Charlie', 'David'),
 ('David', 'Eve')
]
person_community = {
 'Alice': 'Community1',
 'Bob': 'Community1',
 'Charlie': 'Community2',
 'David': 'Community2',
 'Eve': 'Community3'
}
# -------------------------------
# Sociogram 1: Person-to-Person
# -------------------------------
G_person = nx.Graph()
G_person.add_edges_from(person_edges)
plt.figure(figsize=(6, 4))
nx.draw(G_person, with_labels=True, node_color='skyblue', edge_color='gray', node_size=1200)
plt.title("Sociogram: Person-to-Person Network")
plt.show()
# -------------------------------
# Sociogram 2: Community-to-Community
# -------------------------------
G_community = nx.Graph()
for a, b in person_edges:
 comm_a = person_community[a]
 comm_b = person_community[b]
 if comm_a != comm_b:
  G_community.add_edge(comm_a, comm_b)
plt.figure(figsize=(6, 4))
nx.draw(G_community, with_labels=True, node_color='lightgreen', edge_color='brown',
node_size=1500)
plt.title("Sociogram: Community-to-Community Network")
plt.show()
# -------------------------------
# Bipartite Graph: Person ↔ Community
# -------------------------------
B = nx.Graph()
communities = list(set(person_community.values()))
# Add nodes
B.add_nodes_from(persons, bipartite=0)
B.add_nodes_from(communities, bipartite=1)
# Add edges
B.add_edges_from((p, c) for p, c in person_community.items())
# Draw bipartite graph
plt.figure(figsize=(7, 5))
pos = nx.bipartite_layout(B, persons)
node_colors = ['skyblue' if node in persons else 'lightgreen' for node in B.nodes()]
nx.draw(B, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=1400)
plt.title("Bipartite Network: Persons ↔Communities")
plt.show()
# -------------------------------
# One-Mode Projection: Persons Sharing Communities
# -------------------------------
person_proj = bipartite.weighted_projected_graph(B, persons)
plt.figure(figsize=(6, 4))
nx.draw(person_proj, with_labels=True, node_color='orange', edge_color='gray', node_size=1200)
plt.title("Projection: Persons Sharing Communities")
plt.show()
      """)



def prac_4():
  print("""
https://drive.google.com/drive/folders/1hLK_mKGXo7piA99V9rGWx2qzVaUu9pJ_
# Practical 4 Develop Content (text, emoticons, image, audio, video) based social media analytics model for
# business. (e.g., Content Based Analysis: Topic, Issue, Trend, sentiment/opinion analysis, audio, video,
# image analytics)
# Required installations:
#!pip install textblob emoji matplotlib pillow opencv-python SpeechRecognition moviepy

from textblob import TextBlob
import emoji
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import os
import speech_recognition as sr

# -------------------------------
# Text Analysis
# -------------------------------
def analyze_text(text):
    print("===== TEXT ANALYSIS =====")
    blob = TextBlob(text)
    print("Text:", text)
    print("Polarity:", blob.sentiment.polarity)
    print("Subjectivity:", blob.sentiment.subjectivity)

    # Basic Emoji Sentiment Count
    pos_emojis = ['😊', '😁', '😍', '❤', '👍']
    neg_emojis = ['😢', '😡', '😞', '👎']
    pos_count = sum(text.count(e) for e in pos_emojis)
    neg_count = sum(text.count(e) for e in neg_emojis)

    print("Positive Emojis:", pos_count)
    print("Negative Emojis:", neg_count)

# -------------------------------
# Image Analysis
# -------------------------------
def analyze_image(img_path):
    print("\n===== IMAGE ANALYSIS =====")
    if not os.path.exists(img_path):
        print("Image file not found.")
        return

    img = Image.open(img_path)
    plt.imshow(img)
    plt.axis('off')
    plt.title("Loaded Image")
    plt.show()

    print("Image size:", img.size)
    print("Image mode:", img.mode)

# -------------------------------
# Audio Analysis (Speech-to-Text + Sentiment)
# -------------------------------
def analyze_audio(audio_path):
    print("\n===== AUDIO ANALYSIS =====")
    if not os.path.exists(audio_path):
        print("Audio file not found.")
        return

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print("Transcribed Audio:", text)
            sentiment = TextBlob(text).sentiment
            print("Polarity:", sentiment.polarity)
            print("Subjectivity:", sentiment.subjectivity)
    except Exception as e:
        print("Audio processing failed:", e)

# -------------------------------
# Video Frame Extraction
# -------------------------------
def analyze_video(video_path, frame_interval=30):
    print("\n===== VIDEO ANALYSIS =====")
    if not os.path.exists(video_path):
        print("Video file not found.")
        return

    cap = cv2.VideoCapture(video_path)
    frame_count, saved_frames = 0, 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            fname = f'frame_{saved_frames}.jpg'
            cv2.imwrite(fname, frame)
            print(f"Saved: {fname}")
            saved_frames += 1

        frame_count += 1

    cap.release()
    print(f"Total frames saved: {saved_frames}")
# -------------------------------
# Run All Analyses
# -------------------------------
if __name__ == "__main__":
  sample_text = "I absolutely love the new features! But it still has some bugs👍 "
  analyze_text(sample_text)
  analyze_image("sample.jpg")
  analyze_audio("sample.wav")
  analyze_video("sample.mp4")

  """)



def prac_5():
  print("""
# Practical 5
# Aim: Develop Structure based social media analytics model for any business. (e.g., Structure Based
# Models -community detection, influence analysis)
import networkx as nx
import matplotlib.pyplot as plt

# Step 1: Create a sample social network graph
G = nx.Graph()

# Adding edges (representing interactions between users)
edges = [
    ('Alice', 'Bob'), ('Alice', 'Charlie'), ('Bob', 'Charlie'),
    ('Bob', 'David'), ('Charlie', 'David'), ('Eve', 'Frank'),
    ('Frank', 'Grace'), ('Grace', 'Heidi'), ('Eve', 'Heidi'),
    ('David', 'Eve'),  # Connecting two communities
]

G.add_edges_from(edges)

# Step 2: Visualize the graph
plt.figure(figsize=(8, 6))
nx.draw(G, with_labels=True, node_color='skyblue', node_size=1000, font_weight='bold')
plt.title("Social Network Graph")
plt.show()

# Step 3: Community Detection using Greedy Modularity
from networkx.algorithms.community import greedy_modularity_communities

communities = list(greedy_modularity_communities(G))
print("\nDetected Communities:")
for i, community in enumerate(communities):
    print(f"Community {i + 1}: {list(community)}")

# Color the communities
color_map = {}
colors = ['red', 'green', 'blue', 'purple', 'orange']
for i, community in enumerate(communities):
    for node in community:
        color_map[node] = colors[i % len(colors)]

node_colors = [color_map[node] for node in G.nodes()]

plt.figure(figsize=(8, 6))
nx.draw(G, with_labels=True, node_color=node_colors, node_size=1000, font_weight='bold')
plt.title("Community Detection in Social Network")
plt.show()

# Step 4: Influence Analysis using Degree Centrality
centrality = nx.degree_centrality(G)
sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

print("\nTop Influential Users (by Degree Centrality):")
for user, score in sorted_centrality:
    print(f"{user}: {score:.2f}")

# Highlight top influencer
top_user = sorted_centrality[0][0]
node_colors = ['gold' if node == top_user else 'lightgrey' for node in G.nodes()]

plt.figure(figsize=(8, 6))
nx.draw(G, with_labels=True, node_color=node_colors, node_size=1000, font_weight='bold')
plt.title(f"Top Influencer Highlighted: {top_user}")
plt.show()
  """)



def prac_7():
  print('''
# Practical 7
# Aim: Develop Structure based social media analytics model for any business. (e.g., Structure Based
# Models -community detection, influence analysis)

# social_media_chart.py

# Data: Each row represents a platform and its engagement metrics
data = [
    ['Platform', 'Likes', 'Comments', 'Shares'],
    ['Facebook', 1200, 300, 200],
    ['Instagram', 1500, 500, 250],
    ['Twitter', 900, 200, 100],
    ['LinkedIn', 600, 150, 80]
]

# HTML + JavaScript content using Google Charts
html_content = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Social Media Engagement</title>
    <script src="https://www.gstatic.com/charts/loader.js"></script>
    <script>
      google.charts.load('current', {{packages: ['corechart']}});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {{
        var data = google.visualization.arrayToDataTable({data});
        var options = {{
          title: 'Social Media Engagement',
          hAxis: {{title: 'Platform'}},
          vAxis: {{title: 'Count'}},
          chartArea: {{width: '70%', height: '70%'}},
          colors: ['#3366CC', '#DC3912', '#FF9900']
        }};
        var chart = new google.visualization.ColumnChart(
          document.getElementById('chart_div')
        );
        chart.draw(data, options);
      }}
    </script>
  </head>
  <body>
    <h2 style="text-align:center;">Social Media Data Analysis</h2>
    <div id="chart_div" style="width: 900px; height: 500px; margin: auto;"></div>
  </body>
</html>
"""

# Write the HTML content to a file
output_file = "social_media_chart.html"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"Chart generated! Open '{output_file}' in your browser.")


''')




def prac_8():
  print('''
# Practical 8
# Aim: Analyze social media data Network Analysis with Orange Software
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 1. Dummy Data: Who mentions whom
data = {
    'user': ['user1', 'user2', 'user3', 'user4', 'user5'],
    'mentions': [
        ['user2', 'user3'],  # user1 mentions user2 and user3
        ['user1'],           # user2 mentions user1
        ['user1', 'user4'],  # user3 mentions user1 and user4
        ['user2'],           # user4 mentions user2
        ['user3', 'user1']   # user5 mentions user3 and user1
    ]
}

df = pd.DataFrame(data)

# 2. Create Directed Graph
G = nx.DiGraph()
for _, row in df.iterrows():
    for mention in row['mentions']:
        G.add_edge(row['user'], mention)

# 3. Draw the Graph
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G, seed=1)  # layout for visual consistency
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, edge_color='gray', font_size=10)
plt.title("User Mention Network")
plt.show()

# 4. Network Metrics
print("\nDegree Centrality (Activity):")
for user, score in nx.degree_centrality(G).items():
    print(f"{user}: {score:.2f}")

print("\nBetweenness Centrality (Influence):")
for user, score in nx.betweenness_centrality(G).items():
    print(f"{user}: {score:.2f}")

print("\nPageRank (Popularity):")
for user, score in nx.pagerank(G).items():
    print(f"{user}: {score:.2f}")


''')





def prac_9():
    print("""
# Install PyTorch
!pip install torch torchvision torchaudio

# Install PyTorch Geometric dependencies
!pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-2.0.0+cpu.html

# Practical 9
# Aim: Use Graph Neural Networks on the datasets (Planetoid Cora Dataset)/ Jazz Musicians Network
import torch
import torch.nn.functional as F
from torch_geometric.datasets import Planetoid
from torch_geometric.nn import GCNConv

# -------------------------------
# Load the Cora dataset
# -------------------------------
dataset = Planetoid(root='data/Planetoid', name='Cora')
data = dataset[0]

# -------------------------------
# Define Graph Convolutional Network
# -------------------------------
class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(dataset.num_features, 16)
        self.conv2 = GCNConv(16, dataset.num_classes)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

# -------------------------------
# Initialize model and optimizer
# -------------------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = GCN().to(device)
data = data.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

# -------------------------------
# Training loop
# -------------------------------
print("Training...")
for epoch in range(1, 201):
    model.train()
    optimizer.zero_grad()
    out = model(data)
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()
    if epoch % 20 == 0:
        print(f'Epoch {epoch:3d} | Loss: {loss:.4f}')

# -------------------------------
# Evaluation on Test Set
# -------------------------------
model.eval()
with torch.no_grad():
    pred = model(data).argmax(dim=1)
    correct = (pred[data.test_mask] == data.y[data.test_mask]).sum()
    acc = int(correct) / int(data.test_mask.sum())
    print(f'\nTest Accuracy: {acc:.4f}')
         
""")

# Call the function




def prac_10():
    print("""
# Practical 10
# Aim: Analyze Twitter conversations to identify the most active and influential users using Machine Learning Algorithms with Gephi Tool.
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import community.community_louvain as community_louvain  # fixed import

# import community as community_louvain  # pip install python-louvain

# 1. Dummy Twitter Conversation Data
data = {
    'sender':   ['user1', 'user2', 'user3', 'user2', 'user4', 'user5', 'user3', 'user1', 'user5'],
    'receiver': ['user2', 'user3', 'user1', 'user1', 'user2', 'user3', 'user4', 'user3', 'user1'],
    'type':     ['reply', 'mention', 'reply', 'retweet', 'mention', 'reply', 'mention', 'retweet', 'mention']
}
df = pd.DataFrame(data)

# 2. Create Directed Graph with Weights
G = nx.DiGraph()
for _, row in df.iterrows():
    u, v = row['sender'], row['receiver']
    if G.has_edge(u, v):
        G[u][v]['weight'] += 1
    else:
        G.add_edge(u, v, weight=1, type=row['type'])

# 3. Visualize Conversation Network
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G, seed=42)
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000,
        edge_color=edge_weights, edge_cmap=plt.cm.Blues, width=2, font_size=10)
plt.title("Twitter Conversation Network")
plt.show()

# 4. Most Active Users (by Out-Degree)
print("\nMost Active Users (Out-Degree):")
for user, score in sorted(G.out_degree(), key=lambda x: x[1], reverse=True):
    print(f"{user}: {score}")

# 5. Most Influential Users
print("\nIn-Degree Centrality (Replied/Mentioned):")
for user, score in sorted(nx.in_degree_centrality(G).items(), key=lambda x: x[1], reverse=True):
    print(f"{user}: {score:.2f}")

print("\nPageRank (Importance):")
for user, score in sorted(nx.pagerank(G).items(), key=lambda x: x[1], reverse=True):
    print(f"{user}: {score:.2f}")

print("\nBetweenness Centrality (Connector Role):")
for user, score in sorted(nx.betweenness_centrality(G).items(), key=lambda x: x[1], reverse=True):
    print(f"{user}: {score:.2f}")

# 6. Louvain Community Detection (Clusters)
print("\nLouvain Community Detection:")
partition = community_louvain.best_partition(G.to_undirected())
for user, cluster in partition.items():
    print(f"{user} → Cluster {cluster}")

# 7. Visualize Communities
plt.figure(figsize=(8, 6))
colors = [partition[node] for node in G.nodes()]
nx.draw(G, pos, with_labels=True, node_color=colors, cmap=plt.cm.Set3,
        node_size=2000, edge_color='gray', font_size=10)
plt.title("Twitter User Communities (Louvain)")
plt.show()

""")
    
