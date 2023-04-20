from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from fastapi.responses import JSONResponse
from .services import RuleService, NotFoundException
from .models import APIGeneralResponse, APIUpdateRequest, APIAddRequest, RuleModel, APIErrorResponse

router = APIRouter(
    prefix="/rules",
    tags=["rules"],
)

@router.get("/")
@inject
async def all(
    service: RuleService = Depends(Provide["rule_module.rule_service"]),
):
    return {"status": True}

@router.get("/{rule_id}", 
    response_model=APIGeneralResponse,
    responses={
            404: {"model": APIErrorResponse},
            400: {"model": APIErrorResponse},
            500: {"model": APIErrorResponse}
        }
    )
@inject
async def get(
    rule_id: str,
    service: RuleService = Depends(Provide["rule_module.rule_service"]),
):
    try:
        return {"data": await service.find(rule_id)}
    except NotFoundException as e:
        return JSONResponse(status_code=404, content={ "message": "Item not found", "status": False, "data":None, "error":e.args})
    except Exception as e:
        return JSONResponse(status_code=400, content={ "message": "Operation error", "status": False, "data":None, "error":e.args})

@router.post("/",
    response_model=APIGeneralResponse,
    responses={
            400: {"model": APIErrorResponse},
            500: {"model": APIErrorResponse}
    }
)
@inject
async def add(
    request:APIAddRequest,
    service: RuleService = Depends(Provide["rule_module.rule_service"]),
):
    try:
        model = RuleModel(**request.dict())
        await service.create_rule(model)
        return {"data": model}
    except Exception as e:
        return JSONResponse(status_code=400, content={ "message": "Operation error", "status": False, "data":None, "error":e.args})

@router.put("/{rule_id}" , 
    response_model=APIGeneralResponse,
    responses={
            404: {"model": APIErrorResponse},
            400: {"model": APIErrorResponse},
            500: {"model": APIErrorResponse}
        }
    )
@inject
async def update(
    rule_id: str,
    request:APIUpdateRequest,
    service: RuleService = Depends(Provide["rule_module.rule_service"])
):
    try:
        model:RuleModel = await service.find(rule_id)
        if model.is_trigger:
            raise Exception(f"Rule id {rule_id} has triggered, and not able to update")

        request_dict = request.dict()
        for k,v in model:
            if k in request_dict and request_dict[k] :
                model.__setattr__(k, request_dict[k])
        
        await service.update_rule(model)

        return {"data": model}
    except NotFoundException as e:
        return JSONResponse(status_code=404, content={ "message": "Item not found", "status": False, "data":None, "error":e.args})
    except Exception as e:
        return JSONResponse(status_code=400, content={ "message": "Operation error", "status": False, "data":None, "error":e.args})

@router.delete("/{rule_id}",
    response_model=APIGeneralResponse,
    responses={
            404: {"model": APIErrorResponse},
            400: {"model": APIErrorResponse},
            500: {"model": APIErrorResponse}
        }
)
@inject
async def delete(rule_id: str, service: RuleService = Depends(Provide["rule_module.rule_service"])):
    try:
        await service.delete_rule(rule_id)
        return {"status": True}
    except Exception as e:
        return JSONResponse(status_code=400, content={ "message": "Operation error", "status": False, "data":None, "error":e.args})
