# pybackground

## Run

```powershell
& 'D:\work_project\python\base\.venv\Scripts\python.exe' run.py
```

## Import Sites

```powershell
& 'D:\work_project\python\base\.venv\Scripts\python.exe' import_sites.py --source ..\数据爬取\pybackground_sites.json
```

## Default Admin

- username: `admin`
- password: `admin123`

可通过环境变量覆盖：

- `NAV_ADMIN_USERNAME`
- `NAV_ADMIN_PASSWORD`
- `NAV_SECRET_KEY`
