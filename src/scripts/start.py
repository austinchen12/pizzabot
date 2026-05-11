import mujoco
import mujoco.viewer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

model = mujoco.MjModel.from_xml_path(str(ROOT / 'assets' / 'SO101' / 'scene.xml'))
data = mujoco.MjData(model)
mujoco.viewer.launch(model, data)
