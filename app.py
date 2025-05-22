import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Animated Policy Explorer")
if st.button("View Dashboard"):
    st.markdown("[Click here to open the funding explorer](http://localhost:8501)", unsafe_allow_html=True)

import networkx as nx
import matplotlib.pyplot as plt

# 1. Create graph from edge list
G = nx.Graph()

# Add nodes with attributes
for _, row in nodes_df.iterrows():
    G.add_node(row['organization_id'],
               degree=row['degree_centrality'],
               betweenness=row['betweenness'])

# Add edges
for _, row in edges_df.iterrows():
    G.add_edge(row['source'], row['target'], weight=row['weight'])

# 2. Filter top N nodes to reduce clutter
top_nodes = nodes_df.sort_values('degree_centrality', ascending=False).head(100)['organization_id'].tolist()
G_sub = G.subgraph(top_nodes).copy()

# 3. Node size and color
node_size = [G_sub.nodes[n]['degree'] * 4000 for n in G_sub.nodes()]
node_color = [G_sub.nodes[n]['betweenness'] for n in G_sub.nodes()]

# 4. Layout
pos = nx.spring_layout(G_sub, k=0.3, iterations=20, seed=42)

# 5. Plot
plt.figure(figsize=(16, 10))
nx.draw_networkx_nodes(G_sub, pos, node_size=node_size, node_color=node_color, cmap='viridis', alpha=0.85)
nx.draw_networkx_edges(G_sub, pos, alpha=0.3, width=1)
nx.draw_networkx_labels(G_sub, pos, labels={n: str(n) for n in G_sub.nodes()}, font_size=8)

plt.title("Filtered Organization Collaboration Network", fontsize=16)
plt.axis("off")
plt.show()

import plotly.graph_objs as go

# Create same G_sub as above
G_sub = G.subgraph(top_nodes).copy()
pos = nx.spring_layout(G_sub, k=0.3, iterations=20, seed=42)

edge_x = []
edge_y = []

for u, v in G_sub.edges():
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
node_text = []
node_color = []
node_size = []

for node in G_sub.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(f'Org ID: {node}<br>Degree: {G_sub.nodes[node]["degree"]:.3f}<br>Betweenness: {G_sub.nodes[node]["betweenness"]:.3f}')
    node_color.append(G_sub.nodes[node]['betweenness'])
    node_size.append(G_sub.nodes[node]['degree'] * 30)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    text=node_text,
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=node_size,
        color=node_color,
        colorbar=dict(
            thickness=15,
            title='Betweenness',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Top 100 Organizations Collaboration Network',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[dict(
                    text="Hover to inspect organization metrics",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002)],
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False))
                )

fig.show()