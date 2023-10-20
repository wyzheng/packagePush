import re
import uvicorn
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from push import send_xml
logging.basicConfig(level=logging.INFO,
                    filename='error.log',
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )

app = FastAPI()


class Item(BaseModel):
    uin: str
    versionId: int
    version: Union[int, None] = None


@app.get('/')
def index():
    return {'message':'-----------------------adTest for s1s---------------------'}


@app.post('/s1sAdTest/autoMessagePush')
async def autos1sAdTest(item: Item):
    uin_str, versionId = item.uin, item.versionId
    if str(versionId) is None:
        logging.debug("version wrong")
        return 400, "version wrong, please check"
    uin_list = uin_str.split(';')
    for uin in uin_list:
        send_xml(int(uin), versionId, type=10002)
    return 200, "push success"


@app.post('/s1sAdTest/messagePush')
async def s1sAdTest(item: Item):
    uin_str, versionId, version = item.uin, item.versionId, item.version
    if re.match('8000\\d{4}', str(version)) is None:
        logging.debug("template id is wrong")
        return 400, "template id wrong, please check"
    if str(versionId) is None:
        logging.debug("version wrong")
        return 400, "version wrong, please check"
    uin_list = uin_str.split(';')
    for uin in uin_list:
        send_xml(int(uin), versionId, type=10002)
    return 200, "push success"


if __name__ == "__main__":
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=8055,
                workers=1)