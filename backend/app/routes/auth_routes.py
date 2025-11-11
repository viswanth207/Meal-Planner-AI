from fastapi import APIRouter, HTTPException, Depends, Response
import re
from pydantic import BaseModel, EmailStr
from app.database import db
from app.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from pydantic import constr
from typing import Optional
from datetime import datetime
import pytz

router = APIRouter()

class SignupUser(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None

class UpdatePhone(BaseModel):
    phone: constr(strip_whitespace=True)

class UpdateDeliverySettings(BaseModel):
    delivery_time: Optional[str] = None  # HH:MM 24h
    delivery_date: Optional[str] = None  # YYYY-MM-DD
    delivery_enabled: Optional[bool] = None
    timezone: Optional[str] = None

@router.post("/signup")
async def signup(user: SignupUser):
    email_norm = user.email.strip().lower()
    # case-insensitive lookup to prevent duplicates
    existing_user = db.users.find_one({
        "email": {"$regex": f"^{re.escape(email_norm)}$", "$options": "i"}
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = get_password_hash(user.password)
    db.users.insert_one({
        "name": user.name,
        "email": email_norm,
        "phone": user.phone,
        "password": hashed_pw,
        "whatsappVerified": False
    })
    token = create_access_token({"sub": email_norm})
    return {"access_token": token, "token_type": "bearer"}

# Clarify method expectations and support CORS preflight
@router.get("/signup", include_in_schema=False)
def signup_get():
    raise HTTPException(status_code=405, detail="Method Not Allowed. Use POST.")

@router.options("/signup", include_in_schema=False)
def signup_options():
    return Response(status_code=204)

@router.post("/login")
async def login(user: LoginUser):
    email_norm = user.email.strip().lower()
    existing_user = db.users.find_one({
        "email": {"$regex": f"^{re.escape(email_norm)}$", "$options": "i"}
    })
    # Validate password with legacy fallback for plaintext records
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Support multiple legacy password fields
    stored_pw = ""
    for key in ["password", "password_hash", "hashed_password", "pass"]:
        val = existing_user.get(key)
        if isinstance(val, str) and val:
            stored_pw = val
            break
    valid = False
    try:
        if stored_pw:
            valid = verify_password(user.password, stored_pw)
    except Exception:
        valid = False
    # Fallback: support legacy plaintext password once and upgrade to hashed
    if not valid and stored_pw and user.password == stored_pw:
        valid = True
        try:
            new_hash = get_password_hash(user.password)
            db.users.update_one({
                "email": {"$regex": f"^{re.escape(email_norm)}$", "$options": "i"}
            }, {"$set": {"password": new_hash, "password_hash": None, "hashed_password": None, "pass": None}})
        except Exception:
            pass
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # If phone provided during sign-in, validate and persist to profile
    if user.phone is not None:
        phone_val = (user.phone or '').strip()
        if not re.match(r"^(whatsapp:)?\+?\d{7,15}$", phone_val):
            raise HTTPException(status_code=400, detail="Phone must be E.164 like '+<countrycode><number>' or 'whatsapp:+<number>'.")
        db.users.update_one({
            "email": {"$regex": f"^{re.escape(email_norm)}$", "$options": "i"}
        }, {"$set": {"phone": phone_val}})
    token = create_access_token({"sub": email_norm})
    return {"access_token": token, "token_type": "bearer"}

# Clarify method expectations and support CORS preflight
@router.get("/login", include_in_schema=False)
def login_get():
    raise HTTPException(status_code=405, detail="Method Not Allowed. Use POST.")

@router.options("/login", include_in_schema=False)
def login_options():
    return Response(status_code=204)

@router.get("/me")
async def me(current_user: str = Depends(decode_access_token)):
    # current_user is the email stored as "sub"
    # case-insensitive match to handle legacy mixed-case emails
    user_doc = db.users.find_one({
        "email": {"$regex": f"^{re.escape(current_user)}$", "$options": "i"}
    }, {"_id": 0, "password": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc

class WhatsAppVerifyPayload(BaseModel):
    verified: Optional[bool] = True

@router.put("/me/whatsapp-verify")
async def whatsapp_verify(payload: WhatsAppVerifyPayload, current_user: str = Depends(decode_access_token)):
    # Default behavior: set whatsappVerified to True when user confirms
    flag = bool(payload.verified) if payload.verified is not None else True
    result = db.users.update_one({
        "email": {"$regex": f"^{re.escape(current_user)}$", "$options": "i"}
    }, {"$set": {"whatsappVerified": flag, "whatsappVerifiedAt": datetime.utcnow()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    # Return updated minimal status
    return {"ok": True, "whatsappVerified": flag}

@router.put("/me/phone")
async def update_phone(payload: UpdatePhone, current_user: str = Depends(decode_access_token)):
    import re
    phone = (payload.phone or '').strip()
    # Accept E.164 or whatsapp:+ prefix; store as provided to preserve intent
    if not re.match(r"^(whatsapp:)?\+?\d{7,15}$", phone):
        raise HTTPException(status_code=400, detail="Phone must be E.164 like '+<countrycode><number>' or 'whatsapp:+<number>'.")
    result = db.users.update_one({
        "email": {"$regex": f"^{re.escape(current_user)}$", "$options": "i"}
    }, {"$set": {"phone": phone}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "phone": phone}

@router.put("/me/delivery")
async def update_delivery_settings(payload: UpdateDeliverySettings, current_user: str = Depends(decode_access_token)):
    updates = {}
    if payload.delivery_time is not None:
        time_str = (payload.delivery_time or '').strip()
        # Validate HH:MM and that it's a real time
        if not re.match(r"^\d{2}:\d{2}$", time_str):
            raise HTTPException(status_code=400, detail="delivery_time must be in HH:MM format")
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="delivery_time is not a valid time")
        updates["delivery_time"] = time_str

    if payload.delivery_date is not None:
        date_str = (payload.delivery_date or '').strip()
        # Validate YYYY-MM-DD and that it's a real date
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            raise HTTPException(status_code=400, detail="delivery_date must be in YYYY-MM-DD format")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="delivery_date is not a valid date")
        updates["delivery_date"] = date_str

    if payload.delivery_enabled is not None:
        updates["delivery_enabled"] = bool(payload.delivery_enabled)

    if payload.timezone is not None:
        tz = (payload.timezone or '').strip()
        # Validate IANA timezone
        if len(tz) > 64:
            raise HTTPException(status_code=400, detail="timezone value too long")
        try:
            pytz.timezone(tz)
        except Exception:
            raise HTTPException(status_code=400, detail="timezone must be a valid IANA name like 'Asia/Kolkata' or 'America/Los_Angeles'")
        updates["timezone"] = tz

    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = db.users.update_one({
        "email": {"$regex": f"^{re.escape(current_user)}$", "$options": "i"}
    }, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"ok": True, **updates}
