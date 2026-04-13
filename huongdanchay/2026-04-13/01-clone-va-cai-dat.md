# 01 — Clone repo và cài đặt dependencies

## 1. Clone repo

```bash
git clone https://github.com/ukelele0718/bienso.git
cd bienso
```

## 2. Cài đặt Python dependencies

### Backend

```bash
cd apps/backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
cd ../..
```

### AI Engine

```bash
pip install -r apps/ai_engine/requirements.txt
```

Nếu gặp lỗi thiếu package khi chạy AI Engine, cài thêm:

```bash
pip install filterpy lap seaborn pandas tqdm
```

### Cài PyTorch (nếu chưa có)

**Có GPU NVIDIA (khuyến nghị):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Chỉ CPU:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

Kiểm tra:
```bash
python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

## 3. Cài đặt Dashboard (Node.js)

```bash
cd apps/dashboard
npm install
cd ../..
```

## 4. Kiểm tra cài đặt

```bash
# Python
python --version          # >= 3.11

# Backend import test
PYTHONPATH=apps/backend python -c "from app.main import app; print('Backend OK')"

# Node
node --version            # >= 18
npm --version

# Dashboard build test
cd apps/dashboard && npm run typecheck && cd ../..
```

Nếu tất cả OK → chuyển sang [02-download-models.md](02-download-models.md).
