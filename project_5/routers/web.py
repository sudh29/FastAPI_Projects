from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Todos, Users
from routers.auth import (
    authenticate_user,
    create_access_token,
    get_db,
)
from datetime import timedelta
from jose import jwt, JWTError
from routers.auth import SECRET_KEY, ALGORITHM

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Remove "Bearer " prefix if present (though we'll set it without prefix usually)
        if token.startswith("Bearer "):
            token = token[7:]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            return None
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        return None


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            url="/auth/login-page", status_code=status.HTTP_302_FOUND
        )

    todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todos, "user": user}
    )


@router.get("/auth/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/auth/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/auth/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(username, password, db)
    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": "Invalid credentials"}
        )

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=30)
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/auth/logout")
async def logout(request: Request):
    response = RedirectResponse(
        url="/auth/login-page", status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie("access_token")
    return response


@router.post("/auth/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    phone_number: str = Form(None),
    db: Session = Depends(get_db),
):
    from routers.auth import bcrypt_context

    user_model = Users(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role="user",
        hashed_password=bcrypt_context.hash(password),
        phone_number=phone_number,
        is_active=True,
    )
    db.add(user_model)
    db.commit()
    return RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)


@router.get("/add-todo", response_class=HTMLResponse)
async def add_todo_page(request: Request):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            url="/auth/login-page", status_code=status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


@router.post("/add-todo", response_class=HTMLResponse)
async def add_todo(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            url="/auth/login-page", status_code=status.HTTP_302_FOUND
        )

    todo_model = Todos(
        title=title,
        description=description,
        priority=priority,
        complete=False,
        owner_id=user.get("id"),
    )
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_page(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            url="/auth/login-page", status_code=status.HTTP_302_FOUND
        )

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo, "user": user}
    )


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    request: Request,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    complete: bool = Form(False),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            url="/auth/login-page", status_code=status.HTTP_302_FOUND
        )

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = complete

    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            url="/auth/login-page", status_code=status.HTTP_302_FOUND
        )

    db.query(Todos).filter(Todos.id == todo_id).filter(
        Todos.owner_id == user.get("id")
    ).delete()
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
