# Pizza-Assembling Robot Project Brief

## Executive Summary

This project proposes an end-to-end robotic pizza assembly system that translates a customer’s natural-language order into physical actions performed by a low-cost open-source robot arm.

The system will use an SO-ARM101 robotic arm, a MuJoCo simulation environment, LeRobot tooling, and a vision-language-action policy fine-tuned for pizza assembly skills. The project is designed to progress from simulated pick-and-place tasks to real-world multi-ingredient assembly, with optional extensions for visual verification and recovery.

A strong first milestone is a real-hardware, language-conditioned pick-and-place system. The full demonstration adds sauce dispensing, sauce spreading, ingredient placement, and natural-language order customization such as “extra cheese” or “no basil.”

---

## Recommended Technical Direction

The proposed stack is viable with a few important design choices:

### Use SmolVLA as the Primary Robot Policy

SmolVLA is the recommended starting policy because it is lightweight enough for consumer GPU fine-tuning and is well aligned with SO-ARM100/SO-ARM101-style hardware. Larger policies such as π0 or π0.5 may be useful later, but they are less suitable as the initial implementation path because their pretrained embodiments are not naturally matched to the SO-ARM101.

### Use a Custom MuJoCo Environment Instead of LIBERO

LIBERO is useful as a reference for language-conditioned robotic tasks, but it is not the right runtime environment for this project. The SO-ARM101 has a different morphology than the Franka Panda arm used by LIBERO, so the project should instead use a custom MuJoCo scene built around the official SO-ARM101 model and custom pizza-related objects.

### Keep Natural-Language Reasoning Separate from Low-Level Control

The recommended architecture separates order understanding from robot execution:

1. A language parser converts the user’s order into structured actions.
2. An executor dispatches each action.
3. A robot policy performs individual physical skills such as placing cheese or pepperoni.

This separation makes the system easier to debug, improves reliability, and allows constraints such as “no basil” or “extra cheese” to be handled before the robot policy is invoked.

---

## System Architecture

```text
User order
  ↓
Order parser
  Converts language into structured JSON
  ↓
Executor
  Dispatches each step to hardware commands or robot skills
  ↓
Robot policy
  Executes individual skills such as placing ingredients
  ↓
Optional verification layer
  Checks progress with an overhead camera or vision-language model
```

Example order:

> “Make me a margherita with extra cheese, no basil.”

Example structured output:

```json
{
  "base": "margherita",
  "actions": [
    {"skill": "dispense_sauce", "amount": "standard"},
    {"skill": "spread_sauce"},
    {"skill": "place", "ingredient": "cheese_ball", "count": 9},
    {"skill": "place", "ingredient": "tomato", "count": 4}
  ]
}
```

The robot policy receives specific, skill-level instructions such as:

> “Place a cheese ball on the pizza.”

This avoids asking the low-level policy to interpret full customer orders. The language parser handles menu logic, ingredient constraints, quantities, and sequencing.

---

## Hardware Recommendation

The project should use the SO-ARM101’s native parallel-jaw gripper for ingredient placement.

For sauce spreading, the recommended approach is a simple fixed silicone paddle mounted to the gripper or wrist. This avoids a tool-changing mechanism, which would add unnecessary mechanical complexity and introduce new failure modes.

### Recommended End-Effector Setup

- Native parallel-jaw gripper for picking and placing rigid ingredients.
- Small silicone paddle mounted beside the gripper or wrist for spreading sauce.
- Rigid pre-portioned ingredients, such as cheese balls or pepperoni cylinders, to simplify grasping.

Tool changing, suction, and deformable ingredient simulation should be deferred unless the simpler approach proves insufficient.

---

## Phase Plan

## Phase 0: Baseline Setup

**Goal:** Establish a working hardware and software baseline.

### Build

- Assemble and calibrate the SO-ARM101.
- Install and validate LeRobot.
- Confirm teleoperation and data recording.
- Open the SO-ARM101 MuJoCo model and verify basic simulation control.

### Success Criteria

- The arm can be teleoperated reliably.
- A small set of demonstrations can be recorded and replayed.
- The MuJoCo model loads successfully and can be controlled.

### Training Required

None.

---

## Phase 1: Single-Skill Pick-and-Place in Simulation

**Goal:** Train a policy to place one rigid topping on a pizza in simulation.

### Build

- Custom MuJoCo scene with:
  - SO-ARM101 robot model.
  - Dough disc.
  - Topping bin.
  - Rigid topping objects.
  - Overhead and wrist camera views.
- Scripted demonstration generator using an IK-based controller.
- LeRobot-format dataset writer.
- SmolVLA fine-tuning pipeline.

### Success Criteria

- The fine-tuned policy achieves strong held-out simulation performance on randomized topping positions and target placements.

### Training Approach

Supervised fine-tuning through behavior cloning. This is appropriate because the task is well-defined, demonstrations can be generated in simulation, and reinforcement learning would add unnecessary complexity.

---

## Phase 2: Multi-Skill, Language-Conditioned Simulation

**Goal:** Extend the system to multiple ingredient types and language-conditioned skills.

### Build

- Multiple ingredient bins.
- Separate ingredient geometries, such as cheese balls, pepperoni, and tomato pieces.
- Scripted demonstrations labeled with different language instructions.
- Combined multi-skill training dataset.

### Success Criteria

- The policy can place the correct ingredient when given the corresponding language instruction.
- Evaluation includes tests where the wrong instruction is provided, confirming that the model is using language rather than only visual cues.

### Training Approach

Continue supervised fine-tuning on a combined multi-skill dataset.

---

## Phase 3: Sim-to-Real Transfer

**Goal:** Transfer the language-conditioned placement policy from simulation to the real robot.

### Build

- Real workspace matching the simulated layout.
- Fixed dough location.
- Ingredient bins positioned consistently with simulation.
- Overhead and wrist cameras.
- Domain-randomized simulation data.
- Real teleoperated demonstrations for fine-tuning.

### Key Techniques

- Randomize lighting, textures, camera poses, and joint noise in simulation.
- Match camera intrinsics and extrinsics between simulation and the real setup.
- Fine-tune with a mixture of simulated and real demonstrations.
- Validate gripper calibration and arm joint calibration before training.

### Success Criteria

- The real robot performs language-conditioned ingredient placement with repeatable success across multiple ingredient types.

### Training Approach

Supervised fine-tuning with mixed simulated and real data.

---

## Phase 4: Full Pizza Assembly

**Goal:** Integrate order parsing, sauce dispensing, sauce spreading, and ingredient placement into a complete pizza assembly demo.

### Build

- Natural-language order parser with structured output.
- Executor state machine.
- Sauce dispenser integration.
- Sauce spreading skill.
- End-to-end control loop connecting parsed orders to robot skills.

### Example Supported Orders

- “Make a margherita.”
- “Make a margherita with extra cheese, no basil.”
- “Add pepperoni and double tomato.”
- “Hold the cheese.”

### Success Criteria

- The system executes several distinct orders end-to-end.
- The robot follows ingredient inclusion, exclusion, and quantity changes.
- The final demo is understandable to a non-technical audience while still demonstrating a technically meaningful robotics stack.

---

## Optional Phase 5: Visual Verification and Recovery

**Goal:** Add robustness through mid-task verification.

### Build

- Overhead image capture between subtasks.
- Vision-language model or computer-vision check for ingredient placement.
- Retry behavior when a placement fails.

### Example Recovery Behavior

If a topping lands outside the dough boundary, the system identifies the failure and retries the placement once.

### Recommendation

This phase should be treated as optional polish. It adds meaningful demo value but should not be required for the first complete version.

---

## Key Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| MuJoCo environment integration takes longer than expected | High | Medium | Budget dedicated time for environment registration and testing. |
| Sim-to-real transfer underperforms | High | High | Use domain randomization and real demonstration fine-tuning. |
| Camera mismatch between simulation and hardware | High | High | Measure real camera positions and match camera intrinsics in simulation. |
| Gripper struggles with small or round ingredients | Medium | Medium | Use rigid ingredients with flat graspable features where possible. |
| Sauce spreading is unreliable | Medium | Low | Iterate simple paddle geometry before adding mechanical complexity. |
| Order parser misinterprets unsupported requests | Low | Medium | Constrain the menu and reject out-of-vocabulary ingredients. |
| Project scope expands too quickly | High | High | Treat Phase 3 as a complete milestone and Phase 4 as the full demo target. |

---

## Expected Final Demo

A user enters or speaks:

> “Make me a margherita with extra cheese, no basil.”

The system responds by:

1. Parsing the order.
2. Confirming the interpreted request.
3. Dispensing sauce.
4. Spreading sauce.
5. Placing the requested number of cheese pieces.
6. Skipping basil.
7. Completing the order.

The same system can then handle a different order, such as:

> “Add pepperoni and hold the cheese.”

This demonstrates grounded language-to-action control, compositional order handling, and real-world robotic execution on an accessible hardware platform.

---

## Why This Project Is Compelling

This project combines several important robotics capabilities in a single, understandable demonstration:

- Natural-language order interpretation.
- Structured planning.
- Vision-language-action skill execution.
- Simulation-first development.
- Sim-to-real transfer.
- Low-cost open-source hardware.
- A clear real-world task with visible success criteria.

The result is a practical and engaging demonstration of how modern language and robotics systems can work together.

---

## Recommended Scope Discipline

The project should prioritize the following path:

1. Single-skill simulated pick-and-place.
2. Multi-ingredient language-conditioned simulation.
3. Real-world ingredient placement.
4. Full pizza assembly.
5. Optional verification and recovery.

The following should be deferred unless clearly needed:

- π0 or π0.5 migration.
- LIBERO environment integration.
- Tool changing.
- Soft or deformable ingredient simulation.
- Reinforcement learning.
- Full autonomous failure recovery.

---

## Primary Resources

- LeRobot documentation and SO-ARM101 workflows.
- Official SO-ARM101 MuJoCo model.
- SmolVLA base checkpoint.
- MuJoCo simulation tooling.
- SO-ARM101 community examples.
- Relevant examples of SO-ARM simulation and robosuite integration.

---

## Assumptions and Open Questions

Several implementation details will need to be validated experimentally:

- Exact policy success rates will depend on dataset quality, calibration, lighting, and object geometry.
- Sauce dispenser reliability must be tested with the chosen hardware.
- The spreading paddle may require several geometry iterations.
- Sim-to-real performance will depend heavily on camera calibration and workspace consistency.
- Real-world ingredient geometry may need adjustment to improve grasp reliability.

The project should be managed empirically: results from hardware tests should override assumptions made during planning.
