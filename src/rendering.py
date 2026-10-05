from pathlib import Path
import matplotlib.pyplot as plt

def render_room(room, out):
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(10,8))
    for w in room.get("walls",[]):
        a=w["start"]; b=w["end"]
        ax.plot([a[0],b[0]],[a[1],b[1]],"-",linewidth=3)
    ax.set_aspect("equal")
    ax.set_title(f"Reconstructed plan — {room['room_id']}")
    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")
    fig.tight_layout(); fig.savefig(out,dpi=180); plt.close(fig)
