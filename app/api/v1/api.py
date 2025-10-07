


from fastapi import APIRouter, Depends

from app.api.v1.endpoints import (
    users,webhooks,psp,vsla,auth,claims,product,beneficiary,paypremium
    
)

router = APIRouter(prefix="/v1")

#router.include_router(users.router, prefix="/users")
router.include_router(vsla.router)
router.include_router(psp.router)
router.include_router(auth.router)  
router.include_router(claims.router)  
router.include_router(product.router)
router.include_router(beneficiary.router)
router.include_router(paypremium.router)
# router.include_router(test.router, prefix="/test")