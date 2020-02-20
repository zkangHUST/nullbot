from nonebot.natural_language import on_natural_language, NLPSession
from nullbot.utils.deco import group_only


RECORD = {}


@on_natural_language(only_to_me=False)
@group_only
async def repeat_bullshit(session: NLPSession):
    group_id = session.ctx['group_id']

    msg = session.msg.strip()

    if group_id not in RECORD:
        RECORD[group_id] = [msg, 1]
        return
    
    prev_msg = RECORD[group_id][0]

    if msg != prev_msg:
        RECORD[group_id] = [msg, 1]
        return

    RECORD[group_id][1] += 1
    count = RECORD[group_id][1]

    print("Message [{}] repeated {} times.".format(prev_msg, count))

    if count == 3:
        await session.send(msg)
        print("Repeated bullshit: {}".format(msg))