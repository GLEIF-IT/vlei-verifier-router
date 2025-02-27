import json

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from controllers import VerifierController
from utils.router_state import RouterState

app = FastAPI()
config: dict = json.load(open("vlei_verifier_router_config.json"))
RouterState.initialize(**config)



@app.put("/presentations/{said}")
async def present_credential(said: str, request: Request):
    vlei_bytes = await request.body()
    vlei = vlei_bytes.decode("utf-8")
    response = VerifierController.presentation(said, vlei)
    return JSONResponse(status_code=response.code, content=response.body)


@app.get("/authorizations/{aid}")
async def authorization(aid: str,):
    response = VerifierController.authorization(aid)
    return JSONResponse(status_code=response.code, content=response.body)


@app.post("/request/verify/{aid}")
async def verify_request(aid: str, request: Request):
    params = request.query_params
    sig = params.get("sig")
    ser = params.get("data")
    response = VerifierController.signed_headers_verification(aid, sig, ser)
    return JSONResponse(status_code=response.code, content=response.body)


@app.post("/signature/verify")
async def verify_signature(aid: str, request: Request):
    request_json = await request.json()
    sig = request_json.get("signature")
    aid = request_json.get("signer_aid")
    digest = request_json.get("non_prefixed_digest")
    response = VerifierController.signature_verification(aid, sig, digest)
    return JSONResponse(status_code=response.code, content=response.body)


@app.post("/root_of_trust/{aid}")
async def add_root_of_trust(aid: str, request: Request):
    request_json = await request.json()
    vlei = request_json.get("vlei")
    oobi = request_json.get("oobi")
    response = VerifierController.add_root_of_trust(aid, vlei, oobi)
    return JSONResponse(status_code=response.code, content=response.body)