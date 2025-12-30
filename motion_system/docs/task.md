# 400m Dash Choreography System Implementation

## Phase 1: Waypoint Chain API
- [x] Add speed/acceleration parameters to ActorBuilder methods
- [x] Implement basic 2D visualizer with Pygame
- [x] Create track renderer, runner renderer, simulation engine

## Phase 2: 400m Track Choreography
- [x] Create `race_400m.py` movie definition
- [x] Define 6 runners with lane assignments
- [x] Implement staggered starts for fair race (0-40.7m offsets)
- [x] Define 3-phase race (stay in lane, break to inside, sprint to finish)

## Phase 3: Testing & Verification
- [x] Create 100m sprint (1 runner) for isolation testing
- [x] Run state/logic tests for 100m sprint
- [x] Run visual tests for 100m sprint
- [ ] Integrate race_400m with 2D visualizer
- [ ] Test speed profiles and lane breaking
- [ ] Run automated test suite
- [ ] Export to Unreal and verify execution
