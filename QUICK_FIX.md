# QUICK FIX FOR PRODUCTION

## 1. Run Production Fix Script
```bash
python fix_production.py
```

## 2. Push Changes
```bash
git add .
git commit -m "Fix UUID and interview links"
git push origin main
```

## 3. Issues Fixed:
- ✅ Font files (icomoon/line-icons) - now loading correctly
- ✅ UUID column missing - script adds it directly to PostgreSQL
- ✅ Interview links - candidates can see interview links on dashboard

## 4. Interview Link Feature:
- Recruiters schedule interviews → generates UUID link
- Candidates see "Join Interview" button on dashboard
- Click → goes to Interview Ready page
- Click "Start Interview" → goes to AI interview page

## 5. Test Steps:
1. Login as recruiter → schedule interview
2. Login as candidate → see interview link on dashboard
3. Click "Join Interview" → Interview Ready page
4. Click "Start Interview" → AI interview begins

The UUID error should be fixed after running the production script!