# JiuEat

這是一個提供測試與示範用的 Python 專案。
為了方便快速測試，本專案預設使用 **SQL** 作為資料庫，你無需額外安裝任何資料庫伺服器即可直接啟動運行。後續也可以輕鬆抽換為其他關聯式資料庫（如 MSSQL、MySQL、PostgreSQL）。

## 


前後端由同一個 FastAPI 服務提供；推薦功能目前採規則式計分，之後可只替換
`backend/services/recommendation_service.py`，API 與前端不需更動。

## 啟動

```bash
uv sync
uv run uvicorn backend.main:app --reload
```

- **網頁：<http://127.0.0.1:8000/>**
- API 文件：<http://127.0.0.1:8000/docs>
- 健康檢查：<http://127.0.0.1:8000/api/health>


## 分層規則

- `routers/`：網址、輸入輸出、HTTP 錯誤
- `services/`：目前只放推薦邏輯；未來可換成 ML
- `models.py`：SQLAlchemy 資料表
- `schemas.py`：Pydantic API 格式
- `frontend/`：HTML、CSS、JavaScript


#### 建立虛擬環境 (.venv)
uv venv

#### 安裝 requirements.txt 中的所有套件
uv pip install -r requirements.txt



####  備註:git指令 (請忽略)

```
git switch 你的分支名稱
```



