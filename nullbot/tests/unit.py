from nonebot import get_bot, on_command, on_request, on_notice, CommandSession, RequestSession, NoticeSession
from nonebot.permission import PRIVATE, SUPERUSER
from nonebot.command import call_command
from spideroj.mongo import DataManager
from nullbot.utils.helpers import multiline_msg_generator
import asyncio
from spideroj.config import OJID_DB, MEMBER_DB, SNAPSHOT_DB
import pymongo


QQ_ID = 724463877
GROUP_ID_200 = 598880963
GROUP_ID_WEEKLY = 958127821


async def tell_dad(msg):
    bot = get_bot()
    await bot.send_private_msg_rate_limited(user_id=QQ_ID, message=msg)


@on_command('test_send_private_msg', aliases=('私聊测试', ), permission=SUPERUSER)
async def test_send_private_msg(session: CommandSession):
    await tell_dad('测试成功')


@on_command('test_at', permission=SUPERUSER)
async def test_at(session: CommandSession):
    await tell_dad('欢迎[CQ:at,qq={}]'.format(QQ_ID))
    

@on_command('test_db_refactor', permission=SUPERUSER)
async def test_db_refactor(session: CommandSession):
    group_id = 1234

    dm = DataManager(group_id)
    
    ok, snapshot = await dm.get_and_save_user_summary(QQ_ID, 'nuullll', 'leetcode')
    await session.send(str(snapshot.accepted))


@on_command('show_db', permission=SUPERUSER)
async def show_db(session: CommandSession):
    db = pymongo.MongoClient()[MEMBER_DB]
    target = db[str(GROUP_ID_200)]

    docs = target.find()
    for doc in docs:
        print(doc)
    
    print(docs.count())

@on_command('test_timer', permission=SUPERUSER)
async def test_timer(session: CommandSession):
    async def timer():
        for count in range(10):
            print(count)
            await asyncio.sleep(1)
            
    task = asyncio.create_task(timer())


@on_command('refactor_members', permission=SUPERUSER)
async def refactor_ids(session: CommandSession):
    src = pymongo.MongoClient()[MEMBER_DB]

    for group_id in [GROUP_ID_WEEKLY, GROUP_ID_200]:
        collection = src[str(group_id)]

        collection.update_many({}, {
            '$unset': {
                'accounts': ''
            }
        })


@on_command('change_field', permission=SUPERUSER)
async def change_field(session: CommandSession):
    _ids = pymongo.MongoClient()[OJID_DB]['all']

    docs = _ids.find({
        'platform': 'leetcodecn'
    })

    for doc in docs:
        qq_id = doc['qq_id']

        snapshots = DataManager.get_snapshots(qq_id)

        ss = snapshots.find_and_modify({
            'platform': 'leetcodecn'
        }, {
            "$rename": {
                "data.Global Ranking": "data.AC Ranking"
            }
        })

        print(snapshots.find_one({'platform': 'leetcodecn'}))
    

@on_command('test_call', permission=SUPERUSER)
async def test_call_command(session: CommandSession):
    ctx = {'anonymous': None, 'font': 1623440, 'group_id': 1048606265, 'message': [{'type': 'text', 'data': {'text': 'report'}}], 'message_id': 20804, 'message_type': 'group', 'post_type': 'message', 'raw_message': 'report', 'self_id': 2210705648, 'sender': {'age': 24, 'area': '北京', 'card': '', 'level': '冒泡', 'nickname': 'Nuullll', 'role': 'owner', 'sex': 'unknown', 'title': '', 'user_id': 724463877}, 'sub_type': 'normal', 'time': 1584248424, 'user_id': 724463877, 'to_me': True}
    await call_command(get_bot(), ctx, 'report')