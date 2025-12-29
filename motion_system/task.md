# Motion System Builder Design

- [ ] Design Fluent Builder Interface <!-- id: 1 -->
    - [x] Define helper enums (Direction, Speed, etc.) <!-- id: 2 -->
    - [x] Create `MovieBuilder` class structure (Already exists) <!-- id: 3 -->
    - [x] Implement `move_*` methods (Already exists) <!-- id: 4 -->
    - [x] Implement `turn_*` methods (Already exists) <!-- id: 5 -->
    - [x] Implement `animate` and `wait` methods (Already exists) <!-- id: 6 -->
- [ ] Implement State Awareness <!-- id: 7 -->
    - [ ] Track current position/rotation in builder <!-- id: 8 -->
    - [ ] Implement validation logic (e.g. check bounds) <!-- id: 9 -->
- [ ] Refactor Underlying System <!-- id: 10 -->
    - [ ] Update `motion_planner.py` to accept Builder objects <!-- id: 11 -->
    - [ ] Verify backward compatibility or migration path <!-- id: 12 -->
- [ ] Verification <!-- id: 13 -->
    - [x] Create test script `tests/test_builder_json.py` <!-- id: 14 -->
    - [x] Create `unreal_builder_test.py` (In-engine logic) <!-- id: 15 -->
    - [x] Create `run_builder_test_remote.py` (Local runner) <!-- id: 16 -->
    - [x] Run integrated test in Unreal <!-- id: 17 -->
