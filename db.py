from sqlalchemy import func, select, and_
from postgresql import PayToPixTxStatus, save_pay_to_pix_tx_status
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session

import asyncio
from datetime import datetime, timedelta
from lib import SessionLocal, API_USER, API_SECRET, API_URL, PayToPixTxStatusSchema
from pydantic import ValidationError


def FinalSelect(now: datetime, delta: timedelta):
    pay_to_pix_status_select = (
        select(
            PayToPixTxStatus.tx_hash,
            func.max(PayToPixTxStatus.datetime).label("latest_datetime"),
        )
        .group_by(PayToPixTxStatus.tx_hash)
        .having(
            and_(
                func.max(PayToPixTxStatus.action_id) == 0,
                now - func.max(PayToPixTxStatus.datetime) < delta
            )
        )
        .alias()
    )

    at = aliased(PayToPixTxStatus)

    final_select_query = (
        select(
            at.pay_tx_status_id,
            at.tx_hash,
            at.api_user_id,
            at.step_id,
            at.status_id,
            at.action_id,
            at.datetime,
        )
        .select_from(at)
        .join(
            pay_to_pix_status_select,
            and_(
                at.tx_hash == pay_to_pix_status_select.c.tx_hash,
                at.datetime == pay_to_pix_status_select.c.latest_datetime,
            ),
        )
        .where(and_(at.step_id == 2, at.status_id == 3, at.action_id == 0))  # Agregar condiciones aquí
    )
    
    return final_select_query

async def StatusUpdate(db:Session,x: PayToPixTxStatus) -> None:
    data = {
        'api_user_id': x.api_user_id, 
        'txid': x.tx_hash,
        'step_id': x.step_id,
        'status_id': x.status_id,
        'API_USER': API_USER,
        'API_SECRET': API_SECRET,
        'API_URL': API_URL, 
        'chain': 'polygon', 
        'type': 'pay',
        'target': 'tx_id', 
        'pay_markup': 1,
        'datetime': x.datetime,
    }
    try:
        PayToPixTxStatusSchema(**data)

        api_user_id, txid, _, _, _, _, _, _, _, _, _, _ = tuple(data.values())
        await save_pay_to_pix_tx_status(db, api_user_id, txid, step_id = 2, status_id = 3, action_id = 1)


    except ValidationError as e:
        for error in e.errors():
            print({"status_code": 400, "detail": f"Incorrect {error['loc'][0]}: {error['input']}. {error['msg']}"})



async def main():
    now = datetime.now()
    delta = timedelta(days=1)

    while True:
        with SessionLocal() as db:
            result_final_select = db.execute(FinalSelect(now, delta)).fetchall()
            print('*-*-*')
            for item in result_final_select:
                await StatusUpdate(db, item)

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
