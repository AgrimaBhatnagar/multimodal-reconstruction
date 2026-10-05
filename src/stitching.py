import numpy as np
import networkx as nx

def room_centroid(room):
    return np.asarray(room.get("centroid",[0,0]),dtype=float)

def stitch_rooms(rooms, max_gap=2.5):
    G=nx.Graph()
    for r in rooms:
        G.add_node(r["room_id"])
    for i,a in enumerate(rooms):
        for b in rooms[i+1:]:
            d=float(np.linalg.norm(room_centroid(a)-room_centroid(b)))
            if d<=max_gap:
                G.add_edge(a["room_id"],b["room_id"],distance_m=d)
    return [{"room_a":a,"room_b":b,**d} for a,b,d in G.edges(data=True)]

def whole_property_possible(rooms):
    if not rooms: return False
    G=nx.Graph()
    G.add_nodes_from(r["room_id"] for r in rooms)
    for e in stitch_rooms(rooms):
        G.add_edge(e["room_a"],e["room_b"])
    return nx.is_connected(G)
