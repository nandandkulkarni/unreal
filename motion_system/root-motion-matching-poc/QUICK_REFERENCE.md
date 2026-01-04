# Motion Matching POC - Quick Reference

## 🚀 Quick Commands

### Verify Everything Works
```bash
python run_remote.py test_verify_database.py
```
**What it does**: Checks all assets, spawns Manny in scene

### Create Database
```bash
python run_remote.py create_motion_database.py
```
**What it does**: Creates schema and database with 123 animations discovered

### Run Diagnostics
```bash
python run_remote.py diagnostic_check.py
```
**What it does**: Checks plugin availability and asset paths

### List All Scripts
```bash
python run_remote.py
```
**What it does**: Shows all available scripts

---

## 📁 Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `run_remote.py` | Generic script runner | 165 |
| `create_motion_database.py` | Database creation | 420 |
| `test_verify_database.py` | Verification test | 280 |
| `diagnostic_check.py` | Diagnostics | 140 |

---

## 📊 Current Status

✅ **Database Created**: Schema + Database at `/Game/MotionMatching/`  
✅ **Animations Found**: 123 locomotion animations  
✅ **Verification**: All tests passing  
✅ **Manny Spawning**: Working correctly  

---

## 🎯 Next Steps

1. **Manual Configuration** (Required)
   - Open `/Game/MotionMatching/MannyMotionSchema`
   - Add trajectory and bone channels
   - Open `/Game/MotionMatching/MannyMotionDatabase`
   - Add animations and build database

2. **Create Movie Sequence** (Next Phase)
   - Spawn Manny with motion matching
   - Create movement path
   - Add camera tracking

---

## 📝 Logs

All logs are timestamped and auto-cleaned:
- `database_creation_YYYYMMDD_HHMMSS.log`
- `test_verify_YYYYMMDD_HHMMSS.log`

Old logs deleted automatically on each run.

---

## 🔧 Troubleshooting

### Can't Connect to Unreal
- Ensure Unreal Engine is running
- Enable Remote Control plugin
- Check port 30010 is open

### Assets Not Found
Run verification test:
```bash
python run_remote.py test_verify_database.py
```

### Need Fresh Start
Delete assets in `/Game/MotionMatching/` and re-run:
```bash
python run_remote.py create_motion_database.py
```

---

**For detailed documentation, see `README.md` and `STATUS.md`**
