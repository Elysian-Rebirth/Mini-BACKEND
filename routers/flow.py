from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from database import get_session
from models import Flow
from datetime import datetime
import uuid

router = APIRouter()

class FlowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: Optional[dict] = {}

class FlowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    data: Optional[dict]
    status: int
    user_id: Optional[str]
    update_time: Optional[str]
    create_time: Optional[str]

class FlowListResponse(BaseModel):
    data: List[FlowResponse]
    total: int

@router.get("/", response_model=FlowListResponse)
def read_flows(
    page_num: int = 1,
    page_size: int = 20,
    name: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Flow)
    if name:
        query = query.where(Flow.name.contains(name))
    
    # Calculate offset
    offset = (page_num - 1) * page_size
    flows = session.exec(query.offset(offset).limit(page_size)).all()
    # In a real app, count efficiently. Here just fetching all for count is okay for Lite
    total = len(session.exec(select(Flow)).all()) 
    
    return {"data": flows, "total": total}

@router.post("/", response_model=FlowResponse)
def create_flow(flow: FlowCreate, session: Session = Depends(get_session)):
    db_flow = Flow(
        id=str(uuid.uuid4()),
        name=flow.name,
        description=flow.description,
        data=flow.data,
        create_time=datetime.now().isoformat(),
        update_time=datetime.now().isoformat()
    )
    session.add(db_flow)
    session.commit()
    session.refresh(db_flow)
    return db_flow

@router.get("/{flow_id}", response_model=FlowResponse)
def read_flow(flow_id: str, session: Session = Depends(get_session)):
    flow = session.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow

@router.patch("/{flow_id}", response_model=FlowResponse)
def update_flow(flow_id: str, flow_update: FlowCreate, session: Session = Depends(get_session)):
    db_flow = session.get(Flow, flow_id)
    if not db_flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    flow_data = flow_update.dict(exclude_unset=True)
    for key, value in flow_data.items():
        setattr(db_flow, key, value)
    
    db_flow.update_time = datetime.now().isoformat()
    session.add(db_flow)
    session.commit()
    session.refresh(db_flow)
    return db_flow

@router.delete("/{flow_id}")
def delete_flow(flow_id: str, session: Session = Depends(get_session)):
    flow = session.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    session.delete(flow)
    session.commit()
    return {"ok": True}
