from init_path import init_path

if __name__ == "__main__":
    init_path()


import os
import time
import random
import signal
import queue

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError

from  app.core.config import settings

from app.models.smsinbound import SmsInbound
from app.crud import smsinbound

import asyncio


async def sync_inbounds():

    while True:

        print("Sync campaigns")

        try:
            db = AsyncSessionLocal()

            active_unsynced_inbounds: List[SmsInbound] = await smsinbound.get_all_waiting(db)
            
            
            #db.expunge_all()
            db.expire_on_commit = False


            for ac in active_unsynced_inbounds:
                #basing on user input, content of the message is created
                smstext=""
                print("phone",ac.phone_no_id,ac.display_phone,ac.text_body)
                print("token",settings.WHATSAPP_API_TOKEN)
                
                dataup={"state":3}
                print("body object found",ac.text_body)
                if ac.text_body=="Guide" or ac.text_body=="Help" or ac.type=="interactive":
                    await smsinbound.sentsmsinteractive(settings.WHATSAPP_API_TOKEN,ac.contact_wa_id,smstext,ac.sms_id,db)
                else:
                    if ac.text_body=="Hi":
                        smstext="Thank you for reaching to Cross Gate Solutions, Your bulk sms provider.Send \n 'Guide' or 'Help' To continue "
                        #await smsinbound.sentsms()
                    elif ac.text_body=="1":
                        smstext="We offer bulk at the following rates: \n 1-100k units at ksh 1.00 \n 100k-500k units at ksh 0.8 \n 500k-1m at ksh 0.6 \n over 1m units at ksh 0.5 \n send:\n 10 to order \n 11 main menu  \n 0 Exit "
                    elif ac.text_body=="2":
                        smstext="Welcome feel free to ask any question"
                    
                    else:
                        smstext="oops, seems you selected an invalid option"
                    
                    
                    await smsinbound.sentsms(settings.WHATSAPP_API_TOKEN,ac.contact_wa_id,smstext,ac.sms_id)

                await smsinbound.update_sent(db,ac.sms_id)

        except  SQLAlchemyError:
            #@TODO log this
            pass

        finally:
            await db.close()


        #check if is set for exit and close

       
        await asyncio.sleep( random.uniform(1.0, 2.0) )


session_maker = sessionmaker(bind=create_engine(settings.ASYNC_DATABASE_URL, poolclass=NullPool))

def signal_handler(loop: asyncio.BaseEventLoop):
    for task in asyncio.all_tasks():
        task.cancel()
    print("All tasks cancelled ")
    loop.stop()


loop: asyncio.BaseEventLoop = asyncio.get_event_loop()

loop.add_signal_handler(signal.SIGINT, signal_handler, loop)
loop.add_signal_handler(signal.SIGTERM, signal_handler, loop)
loop.add_signal_handler(signal.SIGHUP, signal_handler, loop)


try:

    
    asyncio.ensure_future( sync_inbounds() )
    
    loop.run_forever()

except KeyboardInterrupt:
    pass

finally:
    print("Closing loop")
    loop.close()

