# LingBot-Map — Repo Analysis & Project Ideas

*Analysis of [interplanetarycriminal/lingbot-map](https://github.com/interplanetarycriminal/lingbot-map) (fork of Robbyant/lingbot-map), July 2026.*

## What it is

LingBot-Map is a **feed-forward 3D foundation model for streaming 3D reconstruction** from ordinary monocular RGB video (paper: "Geometric Context Transformer for Streaming 3D Reconstruction", arXiv:2604.14141, Apache-2.0). Feed it a video or image folder and, per frame, it predicts:

- **Camera pose** (`pose_enc` → extrinsics + intrinsics)
- **Dense depth map + confidence**
- **World-space 3D points + confidence**

Unlike classic SLAM/SfM (COLMAP, ORB-SLAM) there is no iterative optimization — a single transformer pass per frame. Key properties:

- **Streaming**: causal attention with a paged KV cache (FlashInfer backend, SDPA fallback), ~20 FPS at 518×378, sequences beyond 10,000 frames (25k-frame demo included).
- **Long-range stability**: anchor context, pose-reference window, and trajectory memory handle drift; keyframe intervals and sliding-window mode extend range past the 320-frame RoPE training horizon.
- **Built on VGGT/DINOv2** lineage; checkpoints on HuggingFace (`robbyant/lingbot-map`): `lingbot-map`, `lingbot-map-long`, and a `stage1` checkpoint loadable into VGGT for bidirectional inference.

## What's in the repo

| Component | What it gives you |
|---|---|
| `lingbot_map/` | The model package: streaming aggregator, camera/DPT heads, FlashInfer paged-KV attention, RoPE, pose utils, viser visualization, GLB export, ONNX sky segmentation |
| `demo.py` | Interactive browser viewer (viser) — streaming & windowed modes, keyframing, sky masking, CPU offload, `--compile` |
| `demo_render/` | Offline cinematic render pipeline: CUDA extensions (Morton voxelization, frustum culling), YAML-driven virtual camera paths (follow / birdeye / static / pivot), MP4 output, NPZ→GLB converter, websocket interactive viewer |
| `benchmark/` | A full evaluation framework: 10 dataset adapters (KITTI, TUM, ETH3D, 7-Scenes, Oxford Spires, VBR, Tanks&Temples, NRGBD, Droid-W + a `general` ad-hoc adapter), trajectory/depth/point metrics, prepare→run→evaluate→report pipeline, resumable, multi-env |
| `gct_profile.py`, `scripts/` | Performance & memory profiling |
| `lingbot-map_paper.pdf` | The paper, in-repo |

Notable: `--save_predictions` persists per-frame NPZs (poses, depth, points) — i.e. the pipeline already emits everything needed to feed *other* systems. The `general` benchmark adapter accepts any image folder/video with optional COLMAP ground truth. No tests/CI, no Dockerfile, no PyPI package — all low-hanging fruit for contributions.

**Hardware reality check**: CUDA GPU required (PyTorch 2.8 + CU128 recommended); FlashInfer recommended; a community fork runs it on an 8 GB RTX 4060, and `--offload_to_cpu` / `--keyframe_interval` / windowed mode manage memory.

---

## Things to do with it

### 1. Quick wins (days)

1. **Run it on your own footage** — phone walkthrough, drone clip, dashcam — via `demo.py`; instant 3D point cloud + trajectory in the browser.
2. **Cinematic "video → 3D flythrough" clips** with `demo_render/batch_demo.py` — great demo content; camera paths are pure YAML.
3. **Video → GLB assets**: `--save_predictions` + `npz_to_glb.py` → glTF you can drop into Blender/Three.js/Unity.
4. **Colab / Jupyter notebook** for zero-install trial.
5. **Dockerfile + one-command run** (repo ships none).
6. **Gradio app / HF Space**: upload video → interactive 3D + downloadable GLB.

### 2. PhysicalAI content & community

7. Architecture explainer: how the Geometric Context Transformer unifies anchor context, pose-reference window, trajectory memory; paged KV cache for vision models.
8. Hands-on tutorial series: install → first scan → long-video windowed mode → offline renders.
9. Head-to-head comparison posts: LingBot-Map vs VGGT, CUT3R, Spann3R, MASt3R-SLAM, DROID-SLAM — the in-repo benchmark harness makes this reproducible.
10. "SLAM is becoming a forward pass" thought piece — feed-forward reconstruction as the new front-end for physical AI.
11. Curated dataset of community scans + a leaderboard using `benchmark/`.

### 3. Robotics & embodied AI (the PhysicalAI sweet spot)

12. **ROS 2 node**: wrap `inference_streaming` to publish `nav_msgs/Odometry`, `sensor_msgs/PointCloud2`, depth images — a drop-in learned visual odometry front-end.
13. **Occupancy mapping**: fuse per-frame depth+conf into a voxel/ESDF map for planning and obstacle avoidance.
14. **Sim2real environment capture**: scan real rooms → mesh → import as collision geometry into Genesis / Isaac Sim / MuJoCo for robot training (pairs with the Genesis work).
15. **Drone mapping**: aerial video → large-scale outdoor maps (sky masking is built in; aerial demo is on their TODO as done).
16. **Relocalization / state reset research**: the README admits unbounded sequences need state resetting — build a reset + re-anchor layer, or splice in loop-closure via pose-graph optimization on the predicted trajectory.
17. **3D-aware perception for VLAs**: use the streaming world-points/pose latents as geometric context tokens for vision-language-action policies.
18. **IMU / wheel-odometry fusion**: EKF the predicted poses with cheap inertial data for metric scale and robustness.

### 4. 3D content pipelines

19. **COLMAP-free Gaussian Splatting**: use predicted poses + point cloud to initialize 3DGS/nerfstudio — replaces hours of COLMAP with seconds of inference. Probably the single highest-leverage integration.
20. **TSDF fusion → textured meshes** (Open3D) instead of raw point clouds — real estate walkthroughs, digital twins, game environments.
21. **Matchmove/previz tool**: export predicted camera tracks to Blender/After Effects — instant camera tracking for VFX.
22. **World-model evaluation metric**: run generated videos (LingBot-World, Sora-class models) through it and score 3D consistency of the output — a novel "geometry FID" for video generation. The repo already demos reconstruction of generated footage.

### 5. Engineering & OSS contributions

23. **Live camera input**: demo.py only reads folders/videos — add webcam/RTSP streaming for a true real-time demo.
24. **Edge deployment**: quantization / TensorRT / smaller distilled model for Jetson Orin; publish FPS-vs-VRAM tables (extend `gct_profile.py`).
25. **Tests + CI + PyPI packaging** — none exist today; easy way to become a meaningful contributor.
26. **Dynamic-object masking**: extend the ONNX sky-mask hook to people/vehicles (SAM or a small segmenter) for clean maps in busy scenes.
27. **Semantic 3D mapping**: fuse per-frame open-vocabulary segmentation into the point cloud → queryable maps ("where is the fire extinguisher?").
28. **New benchmark adapters**: ScanNet++, EuRoC, Bonn dynamic — the adapter interface is small and documented.

### 6. Product / startup angles

29. Real-estate & Airbnb walkthrough scans-as-a-service (phone video → hosted 3D tour).
30. Construction progress tracking: weekly site walk → aligned 3D snapshots → diff over time.
31. Insurance/property documentation: room capture for claims.
32. Facility digital twins for logistics/warehouse planning.
33. Heritage/museum digitization on commodity hardware.
34. Fine-tuning verticals from the `stage1` checkpoint: endoscopy, underwater, warehouse — domain-tuned streaming reconstruction.

---

## Suggested starting order

1. Run the demo on your own footage (day 1, needs a CUDA GPU).
2. Ship the Docker + Gradio wrapper — makes everything after it easier to show.
3. Pick one flagship integration: **3DGS initialization** (content pipeline) or **ROS 2 node** (robotics) depending on which PhysicalAI audience you want first.
4. Write the tutorial/comparison content off the back of whichever you build.
