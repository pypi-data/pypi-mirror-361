# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: baby
#     language: python
#     name: baby
# ---

# %%
import requests

baby_url = "http://0.0.0.0:5101"  # URL to reach baby-phone

# %% [markdown]
# ## Check version of the BABY server

# %%
r = requests.get(baby_url)
r.json() if r.ok else r.text

# %% [markdown]
# ## Check which models are available

# %% [markdown]
# ### Summary

# %%
r = requests.get(baby_url + "/models")
r.json() if r.ok else r.text

# %% [markdown]
# ### Including additional meta data

# %%
r = requests.get(baby_url + "/models?meta=true")
r.json() if r.ok else r.text

# %% [markdown]
# ## Start a new session

# %%
modelset = "yeast-alcatras-brightfield-sCMOS-60x-1z"
r = requests.get(f"{baby_url}/session/{modelset}")
if not r.ok:
    raise Exception(f"{r.status_code}: {r.text}")
print(r.json())
session_id = r.json()["sessionid"]

# %% [markdown]
# ## List running sessions

# %%
r = requests.get(baby_url + "/sessions")
r.json() if r.ok else r.text

# %% [markdown]
# ## Send an image to the server

# %%
import numpy as np

rng = np.random.default_rng(42)

# Create suitable N x H x W x Z array
# dtype must be either uint8 or uint16
img = rng.integers(2**8, size=(2, 80, 120, 1), dtype="uint8")

# Initiate a multipart-encoded request
r = requests.post(
    f"{baby_url}/segment?sessionid={session_id}",
    files=[
        # The ordering of these parts must be fixed
        ("dims", ("", str(list(img.shape)))),
        ("bitdepth", ("", "8")),
        ("img", ("", img.tobytes(order="F"))),
        # Optionally specify additional parts that set
        # any kwargs accepted by BabyCrawler.step (ordering
        # is no longer fixed)
        ("refine_outlines", ("", "true")),
    ],
)

r.json() if r.ok else r.text

# %% [markdown]
# *NB: To run the following, `baby-phone` should have been started in debug mode (`baby-phone --debug-mode`) in a subfolder named `baby-phone-debugging`.*

# %%
from imageio import v3 as iio

img1 = iio.imread("../../../baby_train/baby_phone_debugging_image_received_001.png")
# Check that the image received by the server is identical to the one sent
assert np.allclose(img1, img[0, ..., -1])
# metadata associated with the image (i.e., info1) includes the additional keyword arguments
img1.shape, img1.dtype

# %% [markdown]
# ## Retrieve results after processing

# %% [markdown]
# ### Default output without edge masks

# %% [markdown]
# By default the returned result does not include the edge masks and the outlines need to be recreated by the client from the radial spline representation (e.g., using `baby.segmentation.draw_radial`). This is how I did it for the Matlab client to reduce the amount of data being sent over the socket.
#
# See the next section for an example including edge mask output.

# %%
r = requests.get(f"{baby_url}/segment?sessionid={session_id}")
if not r.ok:
    raise Exception(f"{r.status_code}: {r.text}")
outputs = r.json()

# outputs is a list of dicts for each image in batch
print([{k: len(v) for k, v in output.items()} for output in outputs])

# The outputs are (lists of) lists of numbers
with np.printoptions(precision=2):
    print("\ncentres:")
    print(np.array(outputs[0]["centres"]))  # row, col
    print("\nradii:")
    print([np.array(r) for r in outputs[0]["radii"]])

# %% [markdown]
# ### Process images to get output *with* edge masks

# %% [markdown]
# Process the images with the keyword argument `with_edgemasks` set to true:

# %%
# Initiate a multipart-encoded request
r = requests.post(
    f"{baby_url}/segment?sessionid={session_id}",
    files=[
        # The ordering of these parts must be fixed
        ("dims", ("", str(list(img.shape)))),
        ("bitdepth", ("", "8")),
        ("img", ("", img.tobytes(order="F"))),
        # Optionally specify additional parts that set
        # any kwargs accepted by BabyCrawler.step (ordering
        # is no longer fixed)
        ("refine_outlines", ("", "true")),
        ("with_edgemasks", ("", "true")),
    ],
)

r.json() if r.ok else r.text

# %% [markdown]
# Retrieve the processed results:

# %%
r = requests.get(f"{baby_url}/segment?sessionid={session_id}")
if not r.ok:
    raise Exception(f"{r.status_code}: {r.text}")
outputs = r.json()
len(outputs), outputs[0].keys()

# %% [markdown]
# The edgemasks are returned as coordinates using Matlab indexing (i.e., starting from 1). We can regenerate edge mask images from the coordinates using the following:

# %%
all_edgemasks = []
for output in outputs:
    edge_coords_i = output["edgemasks"]
    edgemasks_i = []
    for edge_coords in edge_coords_i:
        edgemask = np.zeros(img.shape[1:3], dtype="bool")
        edgemask[tuple(np.array(d) - 1 for d in edge_coords)] = True
        edgemasks_i.append(edgemask)
    all_edgemasks.append(np.stack(edgemasks_i))

# %% [markdown]
# Now we can display the outlines that BABY hallucinated from noise:

# %%
from matplotlib import pyplot as plt
from visualise import colour_segstack, plot_ims

_, axs = plot_ims(img.squeeze(), show=False)
for ax, edgemasks in zip(axs, all_edgemasks):
    ax.imshow(colour_segstack(edgemasks))
plt.show()
