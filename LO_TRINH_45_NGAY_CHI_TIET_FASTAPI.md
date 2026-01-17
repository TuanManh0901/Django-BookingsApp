# 📅 HƯỚNG DẪN CHI TIẾT 45 NGÀY - FASTAPI BACKEND DEVELOPER

## 🎯 MỤC TIÊU CUỐI CÙNG

Sau 45 ngày (6-8 giờ/ngày), bạn sẽ có:

- **4 Portfolio Projects** đầy đủ chức năng, deployed
- **FastAPI mastery** từ cơ bản đến nâng cao
- **AI Integration** với OpenAI/Gemini APIs
- **Sẵn sàng đi làm** vị trí Junior FastAPI Backend Developer

**Triết lý:** Học nhanh, code nhiều, build projects thực tế, focus FastAPI.

---

## 📋 CHUẨN BỊ (NGÀY 0 - TRƯỚC KHI BẮT ĐẦU)

### 1. C ài đặt môi trường

**Bước 1.1: Cài đặt Python 3.11+**

- Mở trình duyệt, truy cập python.org
- Download phiên bản Python 3.11 trở lên (chọn macOS)
- Mở file .pkg vừa download, cài đặt theo hướng dẫn
- Mở Terminal (Cmd + Space, gõ "Terminal")
- Gõ `python3 --version` để kiểm tra (phải thấy Python 3.11.x)

**Bước 1.2: Cài đặt VS Code**

- Truy cập code.visualstudio.com
- Download cho macOS, cài đặt
- Mở VS Code, vào Extensions (Cmd + Shift + X)
- Cài extensions: Python, Pylance, Black Formatter, Ruff

**Bước 1.3: Cài đặt PostgreSQL**

- Truy cập postgresql.org/download/macosx
- Download phiên bản mới nhất (PostgreSQL 15+)
- Cài đặt theo hướng dẫn
- Mở pgAdmin 4
- Tạo database mới tên "fastapi_learning"

**Bước 1.4: Cài đặt Git**

- Mở Terminal, gõ `git --version`
- Nếu chưa có: gõ `xcode-select --install`
- Tạo tài khoản GitHub tại github.com nếu chưa có

**Bước 1.5: Tạo thư mục làm việc**

- Mở Terminal
- Gõ `mkdir ~/fastapi-45days`
- Gõ `cd ~/fastapi-45days`
- Gõ `python3 -m venv venv` (tạo virtual environment)
- Gõ `source venv/bin/activate` (activate venv - sẽ thấy (venv))

### 2. Cài đặt các tools cần thiết

**Bước 2.1: Install Postman**

- Truy cập postman.com/downloads
- Download Postman cho macOS
- Cài đặt và mở Postman
- Tạo tài khoản free (để save collections)

**Bước 2.2: Install Docker (optional nhưng recommend)**

- Truy cập docker.com/products/docker-desktop
- Download Docker Desktop cho macOS
- Cài đặt và khởi động Docker Desktop
- Gõ `docker --version` để kiểm tra

**Bước 2.3: Install Redis**

- Gõ `brew install redis` (nếu có Homebrew)
- Hoặc download từ redis.io
- Start Redis: `brew services start redis`
- Test: `redis-cli ping` (phải thấy PONG)

### 3. Đăng ký dịch vụ

**Bước 3.1: OpenAI API** 

- Truy cập platform.openai.com/signup
- Đăng ký tài khoản
- Vào API Keys, tạo key mới
- Lưu key vào file `.env` (sẽ tạo sau)

**Bước 3.2: Google Gemini API**

- Truy cập aistudio.google.com/app/apikey
- Đăng nhập Google
- Click "Create API key"
- Copy và lưu key

**Bước 3.3: Railway/Render (deployment)**

- Truy cập railway.app hoặc render.com
- Tạo tài khoản free
- Connect với GitHub

---

## 🐍 TUẦN 1 (NGÀY 1-7): PYTHON FUNDAMENTALS

### NGÀY 1: PYTHON BASICS SPRINT

**Mục tiêu:** Nắm vững Python basics trong 1 ngày.

**Buổi sáng (4 giờ): Syntax & Data Types**

**Bước 1.1: Tạo file first.py**

- Mở VS Code
- File > Open Folder > Chọn ~/fastapi-45days
- Click New File, đặt tên `day01_basics.py`
- Gõ code:

```python
# Variables and Types
name = "John"
age = 25
height = 1.75
is_student = True

print(f"Name: {name}, Age: {age}")

# Lists
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
print(fruits[0])  # apple

# Dictionaries
person = {
    "name": "Alice",
    "age": 30,
    "city": "Hanoi"
}
print(person["name"])

# Loops
for fruit in fruits:
    print(fruit)

for i in range(5):
    print(i)

# Functions
def greet(name):
    return f"Hello, {name}!"

message = greet("World")
print(message)
```

**Bước 1.2: Chạy file**

- Mở Terminal trong VS Code (Ctrl + `)
- Gõ `python day01_basics.py`
- Xem kết quả in ra

**Bước 1.3: Conditional statements**

- Thêm vào file:

```python
# If/Else
age = 20
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")

# List comprehension
numbers = [1, 2, 3, 4, 5]
squares = [n**2 for n in numbers]
evens = [n for n in numbers if n % 2 == 0]
print(squares)
print(evens)
```

**Buổi chiều (4 giờ): OOP Basics**

**Bước 1.4: Classes and Objects**

- Tạo file `day01_oop.py`:

```python
# Class definition
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hi, I'm {self.name}, {self.age} years old"
    
    def birthday(self):
        self.age += 1

# Create objects
person1 = Person("Alice", 25)
person2 = Person("Bob", 30)

print(person1.greet())
person1.birthday()
print(f"After birthday: {person1.age}")

# Inheritance
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
    
    def study(self, subject):
        return f"{self.name} is studying {subject}"

student = Student("Charlie", 20, "S001")
print(student.greet())
print(student.study("Python"))
```

**Bài tập tự làm (2 giờ):**

1. Tạo class `BankAccount` với deposit, withdraw methods
2. Tạo class `Rectangle` với area, perimeter methods
3. Tạo class `TodoList` với add, remove, list_all methods

**Kết quả ngày 1:** Hiểu Python basics, OOP, chạy được code.

---

### NGÀY 2: FILE I/O & EXCEPTION HANDLING

**Mục tiêu:** Xử lý files, errors như pro.

**Buổi sáng (4 giờ): File Operations**

**Bước 2.1: Đọc/ghi text files**

- Tạo `day02_files.py`:

```python
# Write to file
with open("sample.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("Learning Python\n")

# Read from file
with open("sample.txt", "r") as f:
    content = f.read()
    print(content)

# Read line by line
with open("sample.txt", "r") as f:
    for line in f:
        print(line.strip())
```

**Bước 2.2: JSON files**

```python
import json

# Write JSON
data = {
    "name": "Alice",
    "age": 30,
    "hobbies": ["reading", "coding"]
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON
with open("data.json", "r") as f:
    loaded_data = json.load(f)
    print(loaded_data["name"])
```

**Buổi chiều (4 giờ): Exception Handling**

**Bước 2.3: Try/Except**

```python
# Basic exception handling
try:
    num = int(input("Enter a number: "))
    result = 10 / num
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("This always runs")

# Custom exceptions
class InsufficientFundsError(Exception):
    pass

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
    
    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError(f"Only ${self.balance} available")
        self.balance -= amount
        return self.balance

# Usage
account = BankAccount(100)
try:
    account.withdraw(150)
except InsufficientFundsError as e:
    print(f"Error: {e}")
```

**Bài tập:** Tạo Contact Manager lưu JSON với full error handling.

---

### NGÀY 3: ADVANCED PYTHON FEATURES

**Mục tiêu:** Decorators, comprehensions, type hints.

**Buổi sáng (4 giờ): Decorators & Lambdas**

**Bước 3.1: Decorators**

```python
import time
from functools import wraps

# Timer decorator
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

result = slow_function()

# Logger decorator
def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with {args} {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result
    return wrapper

@log
def add(a, b):
    return a + b

add(5, 3)
```

**Buổi chiều (4 giờ): Type Hints & Pydantic**

**Bước 3.2: Type Hints** (CRITICAL for FastAPI!)

```python
from typing import List, Dict, Optional, Union

def process_numbers(numbers: List[int]) -> int:
    return sum(numbers)

def get_user(user_id: int) -> Optional[Dict[str, str]]:
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)

# Using type hints
numbers: List[int] = [1, 2, 3, 4, 5]
total: int = process_numbers(numbers)
user: Optional[Dict[str, str]] = get_user(1)
```

**Bước 3.3: Pydantic Models** (CRITICAL!)

```python
# Install: pip install pydantic
from pydantic import BaseModel, EmailStr, validator

class User(BaseModel):
    name: str
    email: EmailStr
    age: int
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v

# Valid data
user = User(name="Alice", email="alice@example.com", age=30)
print(user.model_dump())  # Convert to dict

# Invalid data - will raise error
try:
    bad_user = User(name="Bob", email="invalid-email", age=-5)
except Exception as e:
    print(f"Validation error: {e}")
```

**Kết quả:** Hiểu type hints và Pydantic = nền tảng FastAPI!

---

### NGÀY 4-5: ASYNC/AWAIT (2 NGÀY)

**Mục tiêu:** Master async programming (CRITICAL cho FastAPI).

**NGÀY 4 Buổi sáng: Async Basics**

**Bước 4.1: Install asyncio tools**

```bash
pip install aiohttp aiofiles
```

**Bước 4.2: First async function**

```python
import asyncio

async def say_hello():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# Run async function
asyncio.run(say_hello())

# Multiple async tasks
async def task1():
    print("Task 1 starting")
    await asyncio.sleep(2)
    print("Task 1 done")
    return "Result 1"

async def task2():
    print("Task 2 starting")
    await asyncio.sleep(1)
    print("Task 2 done")
    return "Result 2"

async def main():
    # Run concurrently
    results = await asyncio.gather(task1(), task2())
    print(results)

asyncio.run(main())
```

**NGÀY 4 Buổi chiều: Async HTTP Requests**

```python
import aiohttp
import asyncio

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_multiple_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# Usage
urls = [
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/posts/3",
]

results = asyncio.run(fetch_multiple_urls(urls))
```

**NGÀY 5: Async File I/O & Performance**

```python
import aiofiles
import time

async def write_file_async(filename, content):
    async with aiofiles.open(filename, 'w') as f:
        await f.write(content)

async def read_file_async(filename):
    async with aiofiles.open(filename, 'r') as f:
        return await f.read()

# Performance comparison
import time

def sync_task():
    time.sleep(1)

async def async_task():
    await asyncio.sleep(1)

# Sync version (10 calls = 10 seconds)
start = time.time()
for i in range(10):
    sync_task()
print(f"Sync: {time.time() - start}s")

# Async version (10 calls = 1 second!)
async def run_async():
    tasks = [async_task() for _ in range(10)]
    await asyncio.gather(*tasks)

start = time.time()
asyncio.run(run_async())
print(f"Async: {time.time() - start}s")
```

**Kết quả 2 ngày:** Hiểu async/await = ready for FastAPI!

---

### NGÀY 6: TESTING VỚI PYTEST

**Mục tiêu:** Viết tests professional.

**Bước 6.1: Install pytest**

```bash
pip install pytest pytest-cov pytest-asyncio
```

**Bước 6.2: First test**

Tạo `calculator.py`:
```python
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

Tạo `test_calculator.py`:
```python
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5
    
def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

# Parametrize
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
```

**Bước 6.3: Chạy tests**

```bash
pytest test_calculator.py -v
pytest --cov=calculator
```

**Kết quả:** Biết viết và chạy tests!

---

### NGÀY 7: PYTHON REVIEW & PROJECT

**Cả ngày: Build Mini Project - TODO API (No Framework)**

Tạo simple HTTP server để hiểu concepts:

```python
# simple_api.py chỉ minh họa - Chi tiết xem trong file gốc
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

todos = []

class SimpleAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/todos':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(todos).encode())
    
    def do_POST(self):
        # Handle POST để add todo
        pass

# Run server
server = HTTPServer(('localhost', 8000), SimpleAPI)
server.serve_forever()
```

**Kết quả Tuần 1:** Python solid, ready for FastAPI!

---

## 🗄️ TUẦN 2 (NGÀY 8-14): SQL & DATABASES

*(Tóm tắt - xem workflow tương tự NGÀY 1)*

**NGÀY 8-9:** PostgreSQL basics, SQL queries (2 ngày)  
**NGÀY 10:** Python + psycopg2 / asyncpg  
**NGÀY 11:** SQLAlchemy Core  
**NGÀY 12:** Async SQLAlchemy  
**NGÀY 13-14:** Database Project - User Management System

---

## ⚡ TUẦN 3-4 (NGÀY 15-28): FASTAPI CORE

### NGÀY 15: FASTAPI HELLO WORLD → CRUD

**MỤC TIÊU:** Từ zero đến có API với database trong 1 ngày!

**Bước 15.1: Install FastAPI**

```bash
pip install fastapi uvicorn[standard] sqlalchemy asyncpg
```

**Bước 15.2: First FastAPI app**

Tạo `main.py`:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

**Bước 15.3: Chạy server**

```bash
uvicorn main:app --reload
```

**Bước 15.4: Test API**

- Mở browser: http://127.0.0.1:8000
- Xem auto docs: http://127.0.0.1:8000/docs (SWAGGER!)
- Click "Try it out" để test

**Bước 15.5: Thêm Pydantic models**

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items/")
def create_item(item: Item):
    return {"message": f"Created {item.name}"}
```

**Bước 15.6: Connect PostgreSQL** (Sử dụng async SQLAlchemy)

Tạo `database.py`:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session
```

**Bước 15.7: Tạo models**

Tạo `models.py`:
```python
from sqlalchemy import Column, Integer, String, Float
from database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String, nullable=True)
```

**Bước 15.8: Tạo schemas**

Tạo `schemas.py`:
```python
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    price: float
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    
    class Config:
        from_attributes = True
```

**Bước 15.9: CRUD endpoints**

Update `main.py`:
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models, schemas
from database import get_db, engine, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/items/", response_model=schemas.ItemResponse)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[schemas.ItemResponse])
async def list_items(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Item).offset(skip).limit(limit))
    items = result.scalars().all()
    return items

@app.get("/items/{item_id}", response_model=schemas.ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Item).where(models.Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

**Bước 15.10: Test với Postman**

- Mở Postman
- POST http://127.0.0.1:8000/items/ với body JSON
- GET http://127.0.0.1:8000/items/
- Check database trong pgAdmin

**KR dày 15:** Complete CRUD API với PostgreSQL chạy ngon! 🎉

---

### NGÀY 16-17: AUTHENTICATION JWT (2 NGÀY)

*(Format workflow tương tự NGÀY 15)*

**NGÀY 16:** Password hashing, JWT tokens  
**NGÀY 17:** Login/Register endpoints, protected routes

---

### NGÀY 18-28: FastAPI Advanced Topics

*(Mỗi ngày 1-2 topics, format tương tự)*

- NGÀY 18-19: Background Tasks & Celery
- NGÀY 20-21: File Upload & Storage
- NGÀY 22-23: WebSockets
- NGÀY 24-25: Testing FastAPI
- **NGÀY 26-28: PROJECT 1 - Blog API** (3 ngày)

---

## 🤖 TUẦN 5-6 (NGÀY 29-40): ADVANCED FASTAPI & AI

### NGÀY 29-35: Performance, Microservices, Deployment

*(Format workflow chi tiết cho từng ngày)*

### NGÀY 36-40: AI INTEGRATION

**NGÀY 36: OpenAI API với FastAPI**  
**NGÀY 37: Google Gemini API**  
**NGÀY 38: LangChain + Vector DB**  
**NGÀY 39-40: PROJECT - AI Travel Advisor**

---

## 🎨 TUẦN 7 (NGÀY 41-45): PORTFOLIO PROJECTS

### NGÀY 41-42: E-COMMERCE API

### NGÀY 43-44: REAL-TIME CHAT API

### NGÀY 45: POLISH & DEPLOY ALL PROJECTS

---

## 📚 TÀI LIỆU HỌC MỖI NGÀY

**Đọc hàng ngày:**
- FastAPI Documentation: https://fastapi.tiangolo.com
- Real Python: https://realpython.com
- Python Type Hints: https://mypy.readthedocs.io

**Practice hàng ngày:**
- LeetCode: 1-2 bài Easy
- Commit code lên GitHub
- Viết notes/journal

---

## ✅ DAILY CHECKLIST TEMPLATE

```markdown
## NGÀY [X]: [TOPIC]

**Morning (4h):** ⏰ 7:00 - 11:00
- [ ] Concept 1
- [ ] Concept 2
- [ ] Code examples

**Afternoon (4h):** ⏰ 13:00 - 17:00
- [ ] Practice exercises
- [ ] Build mini project
- [ ] Write tests

**Completed:** ✅ / ❌
**GitHub Commit:** [link]
**Notes:**
**Tomorrow Goal:**
```

---

## 🎯 MỐC QUAN TRỌNG

**Ngày 7:** Python solid ✅  
**Ngày 14:** SQL + DB ready ✅  
**Ngày 15:** First FastAPI app! 🎉  
**Ngày 28:** Blog API deployed ✅  
**Ngày 35:** Advanced FastAPI mastery ✅  
**Ngày 40:** AI Travel Advisor done ✅  
**Ngày 45:** 4 projects live, READY FOR JOBS! 💼

---

**BẮT ĐẦU NGAY BÂY GIỜ! 🚀**

*"Trong 45 ngày nữa, bạn sẽ ước mình đã bắt đầu từ hôm nay."*

Good luck! 💪
