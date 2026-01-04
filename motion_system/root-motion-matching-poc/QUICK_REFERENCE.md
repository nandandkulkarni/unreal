# Motion Matching POC - Quick Reference (Updated)

## 🚀 Quick Commands

### NEW: Run V2 Configuration (Automated Schema Setup)
```bash
python run_remote.py configure_database_v2.py
```
**What it does**: Automatically adds Trajectory + Pose channels to schema

### Verify Everything Works
```bash
python run_remote.py test_verify_database.py
```
**What it does**: Checks all assets, spawns Manny in scene

### Explore API (For Development)
```bash
python run_remote.py explore_api.py
```
**What it does**: Discovers available PoseSearch API via reflection

### Create Database (Initial Setup)
```bash
python run_remote.py create_motion_database.py
```
**What it does**: Creates schema and database with 123 animations discovered

### List All Scripts
```bash
python run_remote.py
```
**What it does**: Shows all available scripts

---

## 📁 Key Files

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `configure_database_v2.py` | **V2 Auto config** | 330 | ✅ NEW! |
| `explore_api.py` | API exploration | 270 | ✅ NEW! |
| `run_remote.py` | Generic runner | 165 | ✅ |
| `create_motion_database.py` | Database creation | 420 | ✅ |
| `test_verify_database.py` | Verification | 280 | ✅ |

---

## 📊 Current Status

✅ **Database Created**: Schema + Database at `/Game/MotionMatching/`  
✅ **Animations Found**: 123 locomotion animations  
✅ **Verification**: All tests passing  
✅ **API Explored**: 88 PoseSearch classes discovered  
✅ **Schema Config**: **67% automated!**  

---

## 🎯 Next Steps

### Option A: Automated + Manual (Recommended)

1. **Run V2 Configuration** (Automated - 10 seconds)
   ```bash
   python run_remote.py configure_database_v2.py
   ```
   This adds Trajectory and Pose channels automatically!

2. **Manual Steps** (5 minutes)
   - Open `/Game/MotionMatching/MannyMotionDatabase`
   - Add 11 core animations
   - Click "Build Database"

### Option B: Full Manual

Follow `MANUAL_CONFIG_GUIDE.md` (10 minutes total)

---

## 📝 Documentation

- `API_EXPLORATION_RESULTS.md` - **NEW!** API discovery findings
- `STATUS.md` - Current progress (67% automated!)
- `MANUAL_CONFIG_GUIDE.md` - Step-by-step manual instructions
- `README.md` - Complete usage guide

---

## 🔧 Troubleshooting

### Can't Connect to Unreal
- Ensure Unreal Engine is running
- Enable Remote Control plugin
- Check port 30010 is open

### Want to See API Details
```bash
python run_remote.py explore_api.py
```
Check `api_exploration_YYYYMMDD_HHMMSS.log`

### Need Fresh Start
Delete assets in `/Game/MotionMatching/` and re-run:
```bash
python run_remote.py create_motion_database.py
python run_remote.py configure_database_v2.py
```

---

## 🎉 What's New

**API Exploration Success!**
- Discovered 88 PoseSearch classes
- Found working channel creation API
- Automated schema configuration (67%)
- Only 5 minutes of manual work needed

**For detailed technical info, see `API_EXPLORATION_RESULTS.md`**
