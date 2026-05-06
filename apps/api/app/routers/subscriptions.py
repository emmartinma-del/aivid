import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription

router = APIRouter()
stripe.api_key = settings.stripe_secret_key


class CheckoutRequest(BaseModel):
    tier: str  # starter, pro, agency
    success_url: str
    cancel_url: str


TIER_PRICE_MAP = {
    "starter": "stripe_price_starter",
    "pro": "stripe_price_pro",
    "agency": "stripe_price_agency",
}


@router.get("/me")
async def get_subscription(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription).where(Subscription.organization_id == user.organization_id))
    sub = result.scalar_one_or_none()
    if not sub:
        return {"tier": "free", "status": "active", "videos_used": 0, "videos_limit": 1}
    return {
        "tier": sub.tier,
        "status": sub.status,
        "videos_used": sub.videos_used_this_period,
        "videos_limit": sub.videos_limit,
        "period_end": sub.period_end,
    }


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.tier not in TIER_PRICE_MAP:
        raise HTTPException(status_code=400, detail="Invalid tier")

    price_id = getattr(settings, TIER_PRICE_MAP[body.tier])
    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe price not configured")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        metadata={"organization_id": str(user.organization_id)},
    )
    return {"checkout_url": session.url}


@router.post("/portal")
async def create_portal(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subscription).where(Subscription.organization_id == user.organization_id))
    sub = result.scalar_one_or_none()
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    from app.models.organization import Organization
    org_result = await db.execute(select(Organization).where(Organization.id == user.organization_id))
    org = org_result.scalar_one_or_none()

    portal = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=f"{settings.frontend_url}/billing",
    )
    return {"portal_url": portal.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = session["metadata"].get("organization_id")
        stripe_sub_id = session.get("subscription")
        if org_id and stripe_sub_id:
            stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
            tier = _price_to_tier(stripe_sub["items"]["data"][0]["price"]["id"])
            result = await db.execute(select(Subscription).where(Subscription.organization_id == org_id))
            sub = result.scalar_one_or_none()
            if sub:
                sub.stripe_subscription_id = stripe_sub_id
                sub.tier = tier
                sub.status = "active"
            from app.models.organization import Organization
            org_result = await db.execute(select(Organization).where(Organization.id == org_id))
            org = org_result.scalar_one_or_none()
            if org:
                org.stripe_customer_id = session.get("customer")

    elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
        stripe_sub = event["data"]["object"]
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub["id"])
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = stripe_sub["status"]
            if event["type"] == "customer.subscription.updated":
                sub.tier = _price_to_tier(stripe_sub["items"]["data"][0]["price"]["id"])

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        stripe_sub_id = invoice.get("subscription")
        if stripe_sub_id:
            result = await db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
            )
            sub = result.scalar_one_or_none()
            if sub:
                sub.videos_used_this_period = 0

    return {"ok": True}


def _price_to_tier(price_id: str) -> str:
    mapping = {
        settings.stripe_price_starter: "starter",
        settings.stripe_price_pro: "pro",
        settings.stripe_price_agency: "agency",
    }
    return mapping.get(price_id, "free")
